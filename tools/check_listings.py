#!/usr/bin/env python3
"""Compile-check every Ymir listing in the book against a reference compiler.

Extracts each `lstlisting` written in a Ymir style, reconstructs a compilable
translation unit around it, and runs `gyc -fsyntax-only`.  Listings are a mix of
top-level declarations and loose "inside main" statements, so the extractor
splits them and synthesises a `main` when needed.

A listing in `style=coloredverbatimError` must FAIL to compile: it is a
deliberate error demo, and the style is what badges it "Invalid Ymir" in the
PDF.  Listings can also be annotated in the .tex source, on the line *before*
`\\begin{lstlisting}`:

    %% check: error    -- must FAIL to compile (deliberate error demo)
    %% check: skip     -- narrative fragment, not compilable standalone

Usage:
    tools/check_listings.py [--compiler PATH] [--verbose] [--only SUBSTR]

Exit status is non-zero if any listing's outcome differs from what was expected.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BOOK_ROOT = Path(__file__).resolve().parent.parent
# `ymirc` wraps the in-development gyc of ~/ymir/ymir-dev, the compiler the book
# documents.  /usr/bin/gyc is a stale tree.
DEFAULT_COMPILER = shutil.which("ymirc") or "ymirc"

# Styles whose bodies are Ymir source.  `lyilVerb`/`myilVerb` hold YIL, the
# compiler's intermediate language, and `bashVerb` holds shell transcripts.
YMIR_STYLES = {"coloredverbatim", "coloredverbatimError", "coloredverbatimCorrect"}

LISTING_RE = re.compile(
    r"\\begin\{lstlisting\}(?:\[(?P<opts>[^\]]*)\])?\n(?P<body>.*?)\\end\{lstlisting\}",
    re.DOTALL,
)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Tokens that can start a top-level declaration.
DECL_START = re.compile(
    r"^\s*(?:@\w+\s+)*"
    r"(?:pub|prv|prot)?\s*"
    r"(?:fn|class|record|entity|enum|trait|mod|macro|def|static|lazy|extern|use|in|import|__test|aka)\b"
)
# An attribute may sit alone on the line above the declaration it applies to.
ATTR_ONLY = re.compile(r"^\s*@\w+\s*$")


def strip_escapes(body, opts):
    """Remove the LaTeX escapes that `escapechar=@` permits inside a listing."""
    if "escapechar=@" not in opts:
        return body
    # An escape between single quotes *is* the character -- it stands in for one
    # the mono font cannot draw (see BOOK_AUDIT.md ss 1.3).  Substitute a
    # placeholder before anything else, so it does not get unwrapped into the
    # LaTeX macro's argument or deleted outright, leaving `''`.
    body = re.sub(r"(?<=')@.*?@(?=')", "?", body)
    # Between double quotes the escape holds the text of a string literal, set
    # in a font the listing cannot use (`"@\korean{... 안녕하세요}@"`).  Keep
    # the text: listings assert on its length.
    body = re.sub(r'(?<=")@(.*?)@(?=")', lambda m: latex_text(m.group(1)), body)
    # Elsewhere, highlighting wrappers such as @\hb{a}@ merely decorate real
    # code: keep the argument.
    body = re.sub(r"@\\\w+\{([^{}]*)\}@", r"\1", body)
    body = re.sub(r"@[^@\n]*@", "", body)
    return body


def latex_text(escape):
    """The text a LaTeX escape typesets, without its macros and braces."""
    escape = re.sub(r"\\color\{[^{}]*\}", "", escape)
    escape = re.sub(r"\\\w+", "", escape)
    return escape.replace("{", "").replace("}", "").strip()


def parse_opts(opts):
    style = None
    m = re.search(r"style=(\w+)", opts or "")
    if m:
        style = m.group(1)
    return style


def extract(paths):
    """Yield (file, line, opts, body, directive) for every Ymir listing."""
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in LISTING_RE.finditer(text):
            opts = m.group("opts") or ""
            if parse_opts(opts) not in YMIR_STYLES:
                continue
            line = text[: m.start()].count("\n") + 1
            # Look for a `%% check: ...` directive immediately above.
            directive = None
            prev_start = text.rfind("\n", 0, m.start() - 1)
            prev_line = text[prev_start + 1 : m.start()].strip()
            d = re.match(r"%%\s*check:\s*(\w+)", prev_line)
            if d:
                directive = d.group(1)
            body = strip_escapes(m.group("body"), opts)
            yield path, line, opts, body, directive


def split_decls(body):
    """Split a listing body into (top-level declarations, main-body statements).

    A line that starts a declaration opens a region that runs until its brace
    depth returns to zero (or, for a bodiless prototype, until the `;`).
    """
    decls, stmts = [], []
    depth = 0
    in_decl = False
    for raw in body.split("\n"):
        line = raw
        if not in_decl and depth == 0 and (DECL_START.match(line) or ATTR_ONLY.match(line)):
            in_decl = True
        target = decls if in_decl else stmts
        target.append(line)
        code = re.sub(r"//.*", "", line).rstrip()
        depth += code.count("{") + code.count("(") - code.count("}") - code.count(")")
        if in_decl and depth <= 0 and code.endswith(("}", ";")):
            in_decl = False
            depth = 0
    return "\n".join(decls), "\n".join(stmts)


MODULE_RE = re.compile(r"^\s*(?:in|mod)\s+([\w:]+)\s*;", re.M)
MAIN_RE = re.compile(r"^\s*(?:pub\s+)?fn\s+main\b", re.M)


def module_name(body):
    """A listing declaring `in foo;` must live in a file literally named foo.yr."""
    m = MODULE_RE.search(body)
    return m.group(1).split("::")[-1] if m else None


# The harness imports std::io for the many listings that call `println` without
# importing it.  The compiler rejects a `use` that resolves nothing (E3038), so
# when it reports that very line, the unit is rebuilt without it.
IO_HEADER = "use std::io;\n"
UNUSED_HEADER_RE = re.compile(
    r"no symbol is resolved through the use of std::io\s*\n\s*--> \S+:\(1,"
)


def build_unit(body, throws=(), io=True):
    # A listing that writes its own `main` is already a whole translation unit;
    # splitting it would only risk synthesising a second, colliding one.
    if MAIN_RE.search(body):
        decls, stmts = body, ""
    else:
        decls, stmts = split_decls(body)
    # `in`/`mod` must precede everything, so no `use` may be prepended there.
    header = IO_HEADER if io and not MODULE_RE.search(body) else ""
    unit = header + decls
    if stmts.strip():
        sig = "fn main ()"
        if throws:
            sig += "\n  throws " + ", ".join(sorted(throws))
        unit += "\n" + sig + " {\n" + stmts + "\n}\n"
    # A `//` comment on the last line is reported as an unterminated comment
    # block when the file does not end with a newline.
    return unit if unit.endswith("\n") else unit + "\n"


# `main` must declare every exception its body can propagate, but declaring one
# that cannot actually be thrown is itself an error -- so the set is discovered
# by compiling once and reading it back off the diagnostic.
UNDECLARED_THROW_RE = re.compile(
    r"might throw an exception of type (?:mut &\(mut )?([\w:]+)"
)

# Failure classes that reflect a compiler policy the book predates, rather than
# a defect in the listing.  Tracked separately so the totals stay honest.
CLASSES = [
    # The installed standard library can be older than the reference compiler,
    # in which case importing it fails for reasons that have nothing to do with
    # the book.  Checked first so it never masquerades as a listing defect.
    ("stale-stdlib", re.compile(r"/usr/include/ymir/")),
    ("unused", re.compile(r"the symbol \w+ was declared but never used")),
    # A `use` the listing itself writes but resolves nothing through (E3038).
    ("unused-use", re.compile(r"no symbol is resolved through the use of")),
    ("const-assert", re.compile(r"useless runtime assertion")),
    ("undefined-symbol", re.compile(r"undefined symbol")),
    ("shadowing", re.compile(r"declaration of \w+ shadows another declaration")),
]


# A listing whose code is deliberately wrong carries `style=coloredverbatimError',
# which is also what puts the "Invalid Ymir" badge on it in the PDF.  The book
# used to mark error demos with `// error` comments and "Invalid" captions; every
# one now carries the style, and matching the old spellings only misread a valid
# listing whose comment mentions an "error option value" (BOOK_AUDIT.md ss 2.3).
ERROR_STYLE = "coloredverbatimError"


def expects_error(body, opts, directive):
    return directive == "error" or parse_opts(opts) == ERROR_STYLE


def classify(out):
    for name, rx in CLASSES:
        if rx.search(out):
            return name
    return "other"


def run(compiler, source, workdir, modname):
    path = Path(workdir) / f"{modname}.yr"
    path.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [compiler, "-fsyntax-only", path.name],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, ANSI_RE.sub("", proc.stdout + proc.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--compiler", default=os.environ.get("GYC", DEFAULT_COMPILER))
    ap.add_argument("--verbose", "-v", action="store_true", help="show compiler output for each unexpected result")
    ap.add_argument("--only", help="only check listings whose file path contains this substring")
    ap.add_argument("--dump", metavar="FILE:LINE", help="print the reconstructed unit for one listing and exit")
    args = ap.parse_args()

    if not Path(args.compiler).exists() and not shutil.which(args.compiler):
        sys.exit(f"compiler not found: {args.compiler}\nset --compiler or $GYC")

    paths = sorted((BOOK_ROOT / "chapters").rglob("*.tex"))
    if args.only:
        paths = [p for p in paths if args.only in str(p)]

    if args.dump:
        want_file, want_line = args.dump.rsplit(":", 1)
        for path, line, opts, body, directive in extract(paths):
            if want_file in str(path) and line == int(want_line):
                print(build_unit(body))
                return 0
        sys.exit(f"no listing at {args.dump}")

    ok = failed = skipped = xfail_ok = xfail_bad = 0
    problems = []

    with tempfile.TemporaryDirectory() as workdir:
        for n, (path, line, opts, body, directive) in enumerate(extract(paths)):
            rel = path.relative_to(BOOK_ROOT)
            if directive == "skip":
                skipped += 1
                continue
            expect_error = expects_error(body, opts, directive)
            modname = module_name(body) or f"lst{n:04d}"
            code, out = run(args.compiler, build_unit(body), workdir, modname)

            # Retry without the harness's own `use std::io`, if it is unused.
            io = not UNUSED_HEADER_RE.search(out)
            if code != 0 and not io:
                code, out = run(args.compiler, build_unit(body, io=io), workdir, modname)

            # Retry with the exceptions the first pass reported as undeclared.
            throws = set(UNDECLARED_THROW_RE.findall(out))
            if code != 0 and throws:
                code, out = run(args.compiler, build_unit(body, throws, io), workdir, modname)

            if expect_error:
                if code != 0:
                    xfail_ok += 1
                else:
                    xfail_bad += 1
                    problems.append((rel, line, "expected a compile error, but it compiled", "other", ""))
            else:
                if code == 0:
                    ok += 1
                else:
                    failed += 1
                    problems.append((rel, line, "failed to compile", classify(out), out))

    counts = {}
    for rel, line, what, kind, out in problems:
        counts[kind] = counts.get(kind, 0) + 1
        print(f"{rel}:{line}: {what} [{kind}]")
        if args.verbose and out:
            print("\n".join("    " + l for l in out.strip().split("\n")[:24]))
            print()

    print(
        f"\n{ok}/{ok + failed} plain listings compile; "
        f"{xfail_ok}/{xfail_ok + xfail_bad} error demos fail as intended; "
        f"{skipped} skipped."
    )
    if counts:
        print("failures by cause:")
        for kind, c in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {c:4d}  {kind}")
    return 1 if (failed or xfail_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
