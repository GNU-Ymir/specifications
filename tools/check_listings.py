#!/usr/bin/env python3
"""Compile-check every Ymir listing in the book against a reference compiler.

Extracts each `lstlisting` written in a Ymir style, reconstructs a compilable
translation unit around it, and runs `gyc -fsyntax-only`.  Listings are a mix of
top-level declarations and loose "inside main" statements, so the extractor
splits them and synthesises a `main` when needed.

Listings can be annotated in the .tex source, on the `\\begin{lstlisting}` line:

    %% check: error    -- must FAIL to compile (deliberate error demo)
    %% check: skip     -- narrative fragment, not compilable standalone

The annotation goes on the line *before* the listing.  A listing whose body
contains a `// error` comment is also treated as an expected failure, which is
the marker the book already uses.

Usage:
    tools/check_listings.py [--compiler PATH] [--verbose] [--only SUBSTR]

Exit status is non-zero if any listing's outcome differs from what was expected.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BOOK_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COMPILER = "/home/emile/ymir/gcc/gcc-install/bin/gyc"

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
    # Elsewhere, highlighting wrappers such as @\hb{a}@ merely decorate real
    # code: keep the argument.
    body = re.sub(r"@\\\w+\{([^{}]*)\}@", r"\1", body)
    body = re.sub(r"@[^@\n]*@", "", body)
    return body


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


def build_unit(body, throws=()):
    # A listing that writes its own `main` is already a whole translation unit;
    # splitting it would only risk synthesising a second, colliding one.
    if MAIN_RE.search(body):
        decls, stmts = body, ""
    else:
        decls, stmts = split_decls(body)
    # `in`/`mod` must precede everything, so no `use` may be prepended there.
    header = "" if MODULE_RE.search(body) else "use std::io;\n"
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
    ("const-assert", re.compile(r"useless runtime assertion")),
    ("undefined-symbol", re.compile(r"undefined symbol")),
    ("shadowing", re.compile(r"declaration of \w+ shadows another declaration")),
]


# A listing whose code is deliberately wrong carries `style=coloredverbatimError',
# which is also what puts the "Invalid Ymir" badge on it in the PDF.  That is the
# marker to use.  The inline spellings below are the ones the book used before it
# existed, and are still accepted (see BOOK_AUDIT.md ss 2.4).
ERROR_STYLE = "coloredverbatimError"
ERROR_COMMENT_RE = re.compile(
    r"//[^\n]*\b(?:error|not allowed|forbidden|prohibited|illegal)\b", re.I
)
ERROR_CAPTION_RE = re.compile(r"caption=[^,\]]*\b(?:invalid|with errors)\b", re.I)


def expects_error(body, opts, directive):
    if directive == "error":
        return True
    if parse_opts(opts) == ERROR_STYLE:
        return True
    return bool(ERROR_COMMENT_RE.search(body) or ERROR_CAPTION_RE.search(opts))


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

    if not Path(args.compiler).exists():
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

            # Retry with the exceptions the first pass reported as undeclared.
            throws = set(UNDECLARED_THROW_RE.findall(out))
            if code != 0 and throws:
                code, out = run(args.compiler, build_unit(body, throws), workdir, modname)

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
