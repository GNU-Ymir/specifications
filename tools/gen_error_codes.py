#!/usr/bin/env python3
"""Generate the compiler error codes appendix from the compiler's own pages.

The compiler documents every diagnostic code in `docs/errors/E*.md` of the
bootstrap repository. This script turns each live code into one page of the
appendix, grouped by the themes of `tools/error_themes.txt`, and lists the
retired codes in a closing table. It writes, under `chapters/appendix/codes/`,
one file per theme, `retired.tex`, and `index.tex` that inputs them in order.
`error_codes.tex` builds them as a document apart from the book.

It fails, writing nothing, when a live code has no theme, when a theme names a
code that is not live, or when a theme points at a chapter the book lacks.

Usage:
    tools/gen_error_codes.py [--bootstrap PATH]
"""

import argparse
import re
import sys
from pathlib import Path

BOOK_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BOOTSTRAP = Path.home() / "ymir/ymir-dev/repos/bootstrap"
THEMES = BOOK_ROOT / "tools/error_themes.txt"
OUT_DIR = BOOK_ROOT / "chapters/appendix/codes"
TEX_DIR = "chapters/appendix/codes"

CODE_RE = re.compile(r"E\d{4}")
THEME_RE = re.compile(r"\[(\w+)\]\s*(.*?)\s*(?:->\s*(\S+))?$")
RAISED_RE = re.compile(
    r"Raised during \*\*(?P<stage>[^*]+)\*\*, from "
    r"`(?P<entry>\w+::\w+)` \(`(?P<path>[^`]+)`\)\.$"
)
ENTRY_RE = re.compile(r"`(\w+::\w+)`")
CHAPTER_RE = re.compile(r"\\chapter\{(?P<title>[^}]*)\}%?\s*\\label\{(?P<label>chap:\w+)\}")
RETIRED_RE = re.compile(r"^\*\*(?:This code is )?[Rr]etired\.\*\*", re.MULTILINE)
PATH_RE = re.compile(r"[\w.-]+(?:/[\w.-]+)+")
# A chip cannot break across lines: a longer fragment is set in plain \texttt.
LONG_CHIP = 40
HOLE_NOTE = "where `<>` stands for a value the diagnostic fills in."

# Non-ASCII characters of the diagnostic renderer: heavy box drawing, drawn
# with its light counterpart from pmboxdraw, since the mono font has neither.
BOX = {
    "┃": r"\textSFxi{}", "━": r"\textSFx{}", "╋": r"\textSFv{}",
    "┗": r"\textSFii{}", "┏": r"\textSFi{}", "┣": r"\textSFviii{}",
    "┻": r"\textSFvii{}", "…": r"\ldots{}",
}
ESCAPE_CHARS = "~`!|^\"'"

TEXT_SPECIALS = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "%": r"\%", "#": r"\#",
    "$": r"\$", "&": r"\&", "_": r"\_", "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}", "<": r"\textless{}", ">": r"\textgreater{}",
}


def escape(text):
    return "".join(TEXT_SPECIALS.get(c, c) for c in text)


def escape_breakable(text):
    """Escape machine text, allowing a line break after each `::`, `/` and `_`."""
    breaks = {"::": r"::\allowbreak{}", "/": r"/\allowbreak{}", r"\_": r"\_\allowbreak{}"}
    text = escape(text)
    for token, tex in breaks.items():
        text = text.replace(token, tex)
    return text


def label(code):
    return f"sec:codes:{code.lower()}"


class Converter:
    """Markdown of one error page to LaTeX, resolving links to other codes."""

    def __init__(self, live, retired):
        self.live = live
        self.retired = retired

    def link(self, text, target):
        code = target.removesuffix(".md")
        if code in self.live:
            return rf"\hyperref[{label(code)}]{{{text}}}"
        if code in self.retired:
            return rf"\hyperref[sec:codes:retired]{{{text}}}"
        if re.match(r"https?://", target):
            return rf"\href{{{target}}}{{{text}}}"
        return text

    def inline(self, text):
        out = []
        pos = 0
        pattern = re.compile(
            r"(?P<code>``\s?(?P<c2>.+?)\s?``|`(?P<c1>[^`]+)`)"
            r"|\*\*(?P<bold>.+?)\*\*"
            r"|(?<![\w*])\*(?P<ital>[^*\s][^*]*?)\*(?!\w)"
            r"|\[(?P<ltext>[^\]]+)\]\((?P<ltarget>[^)]+)\)"
            r"|\"(?P<quote>[^\"]+)\""
        )
        for m in pattern.finditer(text):
            out.append(self.plain(text[pos:m.start()]))
            if m.group("code"):
                code = m.group("c2") if m.group("c2") is not None else m.group("c1")
                if PATH_RE.fullmatch(code):
                    out.append(rf"\textit{{{escape_breakable(code)}}}")
                elif len(code) > LONG_CHIP and " " in code:
                    out.append(rf"\texttt{{{escape(code)}}}")
                else:
                    out.append(rf"\tokennolst{{{escape(code)}}}")
            elif m.group("bold"):
                out.append(rf"\textbf{{{self.inline(m.group('bold'))}}}")
            elif m.group("ital"):
                out.append(rf"\textit{{{self.inline(m.group('ital'))}}}")
            elif m.group("ltext"):
                out.append(self.link(self.inline(m.group("ltext")), m.group("ltarget")))
            else:
                out.append(f"``{self.inline(m.group('quote'))}''")
            pos = m.end()
        out.append(self.plain(text[pos:]))
        return "".join(out)

    def plain(self, text):
        return escape(text).replace("\\textless{}\\textgreater{}", r"\errhole{}")

    def blocks(self, lines, in_example):
        """Body of a page, from its first `##` heading to the closing rule."""
        out = []
        para = []
        items = []

        def flush():
            if para:
                out.append(self.paragraph(" ".join(para)))
                para.clear()
            if items:
                out.append("\\begin{itemize}\n"
                           + "".join(f"\\item {self.inline(i)}\n" for i in items)
                           + "\\end{itemize}")
                items.clear()

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                flush()
                lang = line[3:].strip()
                j = i + 1
                while not lines[j].startswith("```"):
                    j += 1
                out.append(self.listing(lang, lines[i + 1:j], in_example))
                i = j + 1
                continue
            if line.startswith("## "):
                flush()
                heading = line[3:].strip()
                in_example = heading.startswith("Example")
                out.append(rf"\subsubsection*{{{self.inline(heading)}}}")
            elif not line.strip():
                flush()
            elif m := re.match(r"\s*(?:[-*]|\d+\.)\s+(.*)", line):
                if para:
                    flush()
                items.append(m.group(1))
            elif items:
                items[-1] += " " + line.strip()
            else:
                para.append(line.strip())
            i += 1
        flush()
        return "\n\n".join(out)

    def paragraph(self, text):
        m = RAISED_RE.match(text)
        if not m:
            return self.inline(text)
        return (rf"Raised during \textbf{{{escape(m['stage'])}}}, from"
                rf" \texttt{{{escape_breakable(m['entry'])}}}"
                rf" (\textit{{{escape_breakable(m['path'])}}}).")

    def listing(self, lang, body, in_example):
        while body and not body[0].strip():
            body = body[1:]
        while body and not body[-1].strip():
            body = body[:-1]
        if lang == "ymir":
            style = "coloredverbatimError" if in_example else "coloredverbatim"
            return ("%% check: skip\n"
                    f"\\begin{{lstlisting}}[style={style}]\n"
                    + "".join(l + "\n" for l in body)
                    + "\\end{lstlisting}")
        text = "\n".join(body)
        esc = next(c for c in ESCAPE_CHARS if c not in text)
        for char, tex in BOX.items():
            text = text.replace(char, f"{esc}\\lstbox{{{tex}}}{esc}")
        if re.search(r"[^\x00-\x7f]", text):
            sys.exit(f"unhandled non-ASCII character in output block: {text!r}")
        opts = "style=bashVerb, breaklines=true"
        if esc in text:
            opts += f", escapechar={esc}"
        return f"\\begin{{lstlisting}}[{opts}]\n{text}\n\\end{{lstlisting}}"


class Page:
    def __init__(self, code, text):
        self.code = code
        lines = text.rstrip("\n").split("\n")
        try:
            end = lines.index("---")
        except ValueError:
            end = len(lines)
        self.lines = lines[1:end]
        self.message = next(l[2:].strip() for l in self.lines if l.startswith("> "))
        self.retired = bool(RETIRED_RE.search(text))
        entry = ENTRY_RE.search(text)
        self.entry = entry.group(1) if entry else ""

    def body(self):
        """Lines between the message and the first heading, then the rest."""
        start = next(i for i, l in enumerate(self.lines) if l.startswith("> ")) + 1
        return [l for l in self.lines[start:] if l.strip() != HOLE_NOTE]


def read_pages(bootstrap):
    pages = {}
    for path in sorted((bootstrap / "docs/errors").glob("E*.md")):
        if CODE_RE.fullmatch(path.stem):
            pages[path.stem] = Page(path.stem, path.read_text())
    if not pages:
        sys.exit(f"no error pages under {bootstrap / 'docs/errors'}")
    return pages


def read_themes():
    themes = []
    for n, line in enumerate(THEMES.read_text().split("\n"), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("["):
            m = THEME_RE.match(line)
            if not m:
                sys.exit(f"{THEMES}:{n}: malformed theme header")
            themes.append({"key": m[1], "title": m[2], "chap": m[3], "codes": []})
        elif not themes:
            sys.exit(f"{THEMES}:{n}: code outside any theme")
        else:
            for code in line.split():
                if not CODE_RE.fullmatch(code):
                    sys.exit(f"{THEMES}:{n}: not a code: {code}")
                themes[-1]["codes"].append(code)
    return themes


def read_chapters():
    """Title of each chapter of the book, by label: the appendix is built apart
    from the book, so it names the chapters rather than referencing them."""
    titles = {}
    for path in (BOOK_ROOT / "chapters").rglob("*.tex"):
        m = CHAPTER_RE.search(path.read_text())
        if m:
            titles[m["label"]] = m["title"]
    return titles


def check_themes(themes, live, chapters):
    seen = {}
    errors = []
    for theme in themes:
        for code in theme["codes"]:
            if code in seen:
                errors.append(f"{code} is in both [{seen[code]}] and [{theme['key']}]")
            elif code not in live:
                errors.append(f"{code} in [{theme['key']}] is not a live code")
            seen[code] = theme["key"]
    errors += [f"{code} has no theme" for code in sorted(live) if code not in seen]
    errors += [f"[{t['key']}] points at {t['chap']}, which is no chapter of the book"
               for t in themes if t["chap"] and t["chap"] not in chapters]
    if errors:
        sys.exit("\n".join(errors) + f"\nfix {THEMES.relative_to(BOOK_ROOT)}")


HEADER = ("%% Generated by tools/gen_error_codes.py from docs/errors/ of the compiler;\n"
          "%% edit the compiler's pages or tools/error_themes.txt, then rerun it.\n")


def theme_tex(theme, pages, conv, chapters):
    codes = sorted(theme["codes"])
    out = [HEADER, r"\clearpage", rf"\section{{{escape(theme['title'])}}}", rf"\label{{sec:codes:{theme['key']}}}", ""]
    if theme["chap"]:
        out += [rf"The book's chapter \textit{{{chapters[theme['chap']]}}} specifies the rules"
                " behind these codes.", ""]
    out += [r"\begin{longtable}{@{}l p{0.78\linewidth} r@{}}",
            r"\toprule Code & Message & Page\\ \midrule \endhead"]
    for code in codes:
        out.append(rf"\hyperref[{label(code)}]{{{code}}} & "
                   rf"{conv.plain(pages[code].message)} & \pageref{{{label(code)}}}\\")
    out += [r"\bottomrule", r"\end{longtable}", ""]
    for code in codes:
        page = pages[code]
        out += [rf"\errorcode{{{code}}}{{{conv.plain(page.message)}}}",
                rf"\label{{{label(code)}}}", "",
                conv.blocks(page.body(), False), ""]
    return "\n".join(out)


def retired_tex(pages, conv):
    out = [HEADER, r"\section{Retired codes}", r"\label{sec:codes:retired}", "",
           "A retired code named a message that was deleted from the compiler. It is",
           "never reused, so an older compiler printing it still means the message",
           "below.", "",
           r"\begin{longtable}{@{}l p{0.4\linewidth} p{0.45\linewidth}@{}}",
           r"\toprule Code & Catalogue entry & Message\\ \midrule \endhead"]
    for code, page in sorted(pages.items()):
        if page.retired:
            out.append(rf"{code} & \texttt{{{escape_breakable(page.entry)}}} & "
                       rf"{conv.plain(page.message)}\\")
    out += [r"\bottomrule", r"\end{longtable}", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bootstrap", type=Path, default=DEFAULT_BOOTSTRAP,
                    help=f"the compiler's bootstrap repository (default {DEFAULT_BOOTSTRAP})")
    args = ap.parse_args()

    pages = read_pages(args.bootstrap)
    live = {c for c, p in pages.items() if not p.retired}
    retired = {c for c, p in pages.items() if p.retired}
    themes = read_themes()
    chapters = read_chapters()
    check_themes(themes, live, chapters)
    conv = Converter(live, retired)

    files = {f"{t['key']}.tex": theme_tex(t, pages, conv, chapters) for t in themes}
    files["retired.tex"] = retired_tex(pages, conv)
    files["index.tex"] = HEADER + "".join(
        rf"\input{{{TEX_DIR}/{name.removesuffix('.tex')}}}" + "\n"
        for name in files)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.tex"):
        if old.name not in files:
            old.unlink()
    for name, text in files.items():
        (OUT_DIR / name).write_text(text)
    print(f"{len(live)} codes in {len(themes)} themes, {len(retired)} retired, "
          f"written to {OUT_DIR.relative_to(BOOK_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
