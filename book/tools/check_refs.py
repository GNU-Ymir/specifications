#!/usr/bin/env python3
"""Report `\\ref`s with no matching `\\label`, and labels nobody references.

LaTeX only warns about these, and the warning scrolls past in a normal build, so
they accumulate silently.  Labels defined as an `lstlisting` option
(`label=lst:...`) count too -- `listings` registers them the same way.

Chapters that are planned but not yet written are expected to be referenced, so
`--allow FILE` reads a list of label prefixes/names (one per line, `#` comments)
that are known-pending and reported separately instead of as errors.

Usage:
    tools/check_refs.py [--allow tools/pending_labels.txt] [--unused]
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

BOOK_ROOT = Path(__file__).resolve().parent.parent

LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
LST_OPTS_RE = re.compile(r"\\begin\{lstlisting\}\[([^\]]*)\]")
LST_LABEL_RE = re.compile(r"label=([^,\]]+)")
REF_RE = re.compile(r"\\(?:ref|autoref|pageref|nameref|cref|Cref)\{([^}]*)\}")
# An unescaped `%` comments out the rest of the line; blank it so commented-out
# labels neither count as definitions nor collide with the live ones.
COMMENT_RE = re.compile(r"(?<!\\)%.*")


def decomment(text):
    return "\n".join(COMMENT_RE.sub("", line) for line in text.split("\n"))


def collect():
    labels = defaultdict(list)
    refs = defaultdict(list)
    sources = sorted(BOOK_ROOT.rglob("*.tex"))
    for path in sources:
        if ".build" in path.parts:
            continue
        text = decomment(path.read_text(encoding="utf-8", errors="replace"))
        rel = path.relative_to(BOOK_ROOT)

        def lineno(pos):
            return text[:pos].count("\n") + 1

        for m in LABEL_RE.finditer(text):
            labels[m.group(1)].append((rel, lineno(m.start())))
        for m in LST_OPTS_RE.finditer(text):
            for lm in LST_LABEL_RE.finditer(m.group(1)):
                labels[lm.group(1).strip()].append((rel, lineno(m.start())))
        for m in REF_RE.finditer(text):
            refs[m.group(1)].append((rel, lineno(m.start())))
    return labels, refs


def load_allow(path):
    if not path:
        return []
    out = []
    for line in Path(path).read_text(encoding="utf-8").split("\n"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow", default=str(BOOK_ROOT / "tools" / "pending_labels.txt"))
    ap.add_argument("--unused", action="store_true", help="also list labels nothing references")
    args = ap.parse_args()

    labels, refs = collect()
    allow = load_allow(args.allow if Path(args.allow).exists() else None)

    broken, pending = {}, {}
    for name, sites in refs.items():
        if name in labels:
            continue
        (pending if name in allow else broken)[name] = sites

    for name in sorted(broken):
        for rel, line in broken[name]:
            print(f"{rel}:{line}: reference to undefined label '{name}'")

    dupes = {k: v for k, v in labels.items() if len(v) > 1}
    for name in sorted(dupes):
        sites = ", ".join(f"{r}:{l}" for r, l in dupes[name])
        print(f"duplicate label '{name}' defined at {sites}")

    if args.unused:
        for name in sorted(set(labels) - set(refs)):
            rel, line = labels[name][0]
            print(f"{rel}:{line}: label '{name}' is never referenced")

    print(
        f"\n{len(labels)} labels, {len(refs)} distinct references; "
        f"{len(broken)} broken, {len(pending)} pending (unwritten material), "
        f"{len(dupes)} duplicated."
    )
    return 1 if (broken or dupes) else 0


if __name__ == "__main__":
    sys.exit(main())
