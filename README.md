# Ymir Book

The sources of the Ymir presentation book. It is written for new developers,
including people with no prior computer science background, who want to learn
the [Ymir](https://github.com/GNU-Ymir) language. It is a training course, not a
language specification.

## Requirements

- `lualatex` (TeX Live) with the packages loaded in `special_header.tex`
  (`fontspec`, `listingsutf8`, `tcolorbox`, `awesomebox`, `minitoc`, `tikz`, …)
- `rsync`, used to stage the sources into the build directory
- Optional, for the consistency checks: `python3` and a `gyc` compiler

## Building the book

```
$ make        # quick single-pass build: no table of contents, unresolved refs
$ make refs   # full three-pass build with table of contents and cross-references
$ make clean  # remove the .build directory
```

Sources are copied to `.build/`, compiled there, and the result is copied back
as `main.pdf`.

## Consistency checks

```
$ make check                  # run both checkers
$ make check-refs             # \ref with no \label, duplicate labels
$ make check-listings         # compile every Ymir listing with gyc
$ make check GYC=/path/to/gyc # use a specific compiler
```

- `tools/check_refs.py` reports broken cross-references. References to chapters
  and sections that are planned but not written yet are listed in
  `tools/pending_labels.txt` and reported separately.
- `tools/check_listings.py` extracts every Ymir code listing, wraps it in a
  compilable unit and runs `gyc -fsyntax-only` on it. Listings that
  deliberately show an error or are not standalone can be annotated on the line
  above `\begin{lstlisting}`:

  ```latex
  %% check: error   -- must fail to compile
  %% check: skip    -- narrative fragment, not compilable on its own
  ```

  Use `--only SUBSTR`, `--verbose` or `--dump FILE:LINE` to investigate a
  single listing.

## Layout

```
main.tex              entry point, includes the chapters in order
special_header.tex    preamble: packages, fonts, listing styles, macros
chapters/
  preamble.tex        introduction to the book
  chapterN.tex        chapter title, intro text, and \input of its sections
  chapterN/sectionM.tex
  chapterN/figures/   TikZ figures, \input from the sections
tools/                consistency checkers
BOOK_AUDIT.md         audit of the sources: applied fixes, open decisions, roadmap
progress.org          writing roadmap (kanban); partly out of date, see BOOK_AUDIT.md § 3.3
```

Current chapters:

1. Fundamentals
2. Fundamental types, constants and variables
3. Native scalar types
4. Native compound types
5. Global constructions
6. Variables and memory management
7. Control flows

## Contributing

- Check each code listing against a current `gyc` before committing, and run
  `make check`.
- `BOOK_AUDIT.md` lists the known discrepancies between the book and the
  compiler, and the chapters still to be written. Read it before changing a
  listing that fails to compile, because the fix may belong in the compiler.
