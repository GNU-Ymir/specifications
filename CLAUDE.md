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


## Policy

Consice comment:
- only describe what the functions do, not what the current work is adding
- don't write comment inside a code unless it's absolutely necessary for understanding
- a comment of more than 3 lines is generally too verbose

Commit policy:
- split work in logical commits
- rewrite history when a new commit it modifying something that was introduced by another commit of the same branch
- There's no need for tests to pass, and code to compile between commits as long as the last commit of the branch compiles and test succeed
- don't add co-authors
- commit message are just one line long


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

- **The compiler is the source of truth.** When the book and `ymirc` disagree,
  the book is wrong. Confirm the behaviour with `ymirc` and the compiler's
  `test_resources` (their comments often state the intent), then fix the book.
  §2.1 records the conflicts fixed so far. Two rules shape every listing: an
  unused variable or `use` is a fatal error, so listings read what they declare
  (printing it, usually); and `assert` on a condition the compiler already knows
  is an error, so such checks are written `cte assert` (Part II) or printed
  (Part I).
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
  and topic the chapter's directory name (`basics types control notation scalars
  flow compound memory global compr error lazy`), e.g. `sec:global:extern_var`. A chapter
  label is the topic alone (`chap:scalars`).
  Never put a chapter number in a label. See `BOOK_STYLE.md` § Labels.
- A reference to material that is not written yet goes in
  `tools/pending_labels.txt`. Remove the line once the label exists.
- Listing styles (defined in `special_header.tex`):
  - `coloredverbatim`: Ymir code (checked by the harness)
  - `coloredverbatimCorrect`: Ymir code (checked by the harness)
  - `lyilVerb`, `myilVerb`: YIL, the compiler's intermediate language
  - `bashVerb`: shell transcripts and program output
  - `grammarVerb`: Part II grammar productions (not checked)

  The style name is case-sensitive: `coloredVerbatim` does not exist.
- Tool versions: write `\gycversion` and `\gyllirversion`, never a literal
  number. The Makefile sets them (`GYC_VERSION`, `GYLLIR_VERSION`).
- Inline code: `\token{...}` (lstinline) or `\tokennolst{...}`. Callouts:
  `\mynotebox`, `\mytipbox`, `\mycautionbox`.
- **Non-ASCII characters in listings do not render.** The `literate` option
  does not work for them. Escape them with `escapechar=@`, e.g.
  `'@\ensuremath{\pi}@'c32`. The checker substitutes the placeholder `?` for an
  escape between single quotes, and keeps the text of one between double
  quotes (a string literal).
- Error demos use `style=coloredverbatimError`, which badges them "Invalid Ymir"
  and tells the harness they must fail. `// error` comments mark the faulty
  line for the reader only; the harness ignores them. Use `%% check: skip` on
  the line before `\begin{lstlisting}` for fragments that cannot compile
  standalone.
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
