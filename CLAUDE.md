# CLAUDE.md

LaTeX sources for the Ymir book, a beginner course (not a spec) for the Ymir
language. See `README.md` for layout and build commands.

## Commands

- `make`: single `lualatex` pass in `.build/`, copies back `main.pdf`. Use it
  for quick checks. Cross-references and TOC are not resolved.
- `make refs`: full three-pass build. Needed to verify references or glyphs.
- `make check`: static checks, much faster than a build. Run after any edit.
  - `make check-refs`: `tools/check_refs.py` (add `--unused` for orphan labels)
  - `make check-listings [GYC=path]`: `tools/check_listings.py`; add
    `--only SUBSTR`, `--verbose`, or `--dump chapters/spec/flow/section2.tex:LINE`
    to see the reconstructed translation unit for one listing.
- Missing glyphs are only visible in the build log:
  `grep -c "Missing character" .build/main.log` should print 0.

## Reference compiler

`check_listings.py` defaults to `ymirc` (`~/.local/bin/ymirc`). It runs the
in-development `~/ymir/ymir-dev/target/bin/gyc` with its own standard library,
and it is the compiler the book documents. `/usr/bin/gyc` is a different,
**stale** tree. Do not use it to judge whether a listing is correct. If `ymirc`
is missing, ask before substituting another compiler.

The authoritative syntax references are
`~/ymir/ymir-dev/repos/bootstrap/src/ymirc/lexing/keys.yr` (keywords and
attributes) and `.../bootstrap/test_resources/**/*.yr` (current syntax examples).
`~/ymir/bootstrap` is an older checkout.

## BOOK_AUDIT.md

`BOOK_AUDIT.md` records the state of the sources, fixes already applied, open
decisions, and known false positives. Read the relevant section before touching
a failing listing.

- **§2.1 lists book-vs-compiler conflicts that are the author's call** (`do`/`while`,
  brace-less function bodies, list comprehension over tuples, `assert` on
  constants, unused-variable errors). Do not "fix" these in the book unasked.
- §2.3 lists failures that are not defects (narrative fragments, module
  examples, `stale-stdlib`).
- When you fix something the audit tracks, update the audit's numbers and items
  in the same change.

## Conventions

- Structure: `chapters/course/` holds Part I and `chapters/spec/` Part II, one
  directory per chapter, named after the chapter's label topic.
  `chapters/spec/flow.tex` holds the `\chapter`, intro, `\minitoc`, and
  `\input`s of `chapters/spec/flow/sectionM.tex`. Section files are not always
  input in numeric order (e.g. chapter 2). Check the chapter file, not the
  filename. Figures live in the chapter's `figures/` directory and are
  `\input`, not `\includegraphics`.
- Labels: `kind:topic:name`, with kind one of `chap`, `sec`, `fig`, `tab`, `lst`
  and topic the chapter's directory name (`basics types scalars flow compound
  memory global compr error lazy`), e.g. `sec:global:extern_var`. A chapter
  label is the topic alone (`chap:scalars`).
  Never put a chapter number in a label. See `BOOK_STYLE.md` § Labels.
- A reference to material that is not written yet goes in
  `tools/pending_labels.txt`. Remove the line once the label exists.
- Listing styles (defined in `special_header.tex`):
  - `coloredverbatim`: Ymir code (checked by the harness)
  - `coloredverbatimCorrect`: Ymir code (checked by the harness)
  - `lyilVerb`, `myilVerb`: YIL, the compiler's intermediate language
  - `bashVerb`: shell transcripts

  The style name is case-sensitive: `coloredVerbatim` does not exist.
- Inline code: `\token{...}` (lstinline) or `\tokennolst{...}`. Callouts:
  `\mynotebox`, `\mytipbox`, `\mycautionbox`.
- **Non-ASCII characters in listings do not render.** The `literate` option
  does not work for them. Escape them with `escapechar=@`, e.g.
  `'@\ensuremath{\pi}@'c32`. The checker substitutes a placeholder for an
  escape between quotes.
- Error demos: put `%% check: error` on the line before `\begin{lstlisting}`.
  Use `%% check: skip` for fragments that cannot compile standalone. Older
  listings use `// error`-style comments, which the harness also accepts.
- Prose sometimes cites listing line numbers (e.g. "lines 10, 12 and 14" in
  `spec/error/section1.tex`). Check the surrounding text before adding or
  removing lines in a listing.

## Housekeeping notes

- `progress.org` tracks what is written, chapter by chapter. `BOOK_PLAN.md`
  explains the two-part structure and the chapter order. Update `progress.org`
  when a section lands, and re-export `progress.html` from it.
- `main.tex` gives the chapter order. A new chapter gets a directory named after
  its label topic, under `course/` or `spec/`.
- Build output goes to `.build/` and `main.pdf`, both git-ignored.
- Commit messages use a `[book]`, `[tools]`, … scope prefix.
