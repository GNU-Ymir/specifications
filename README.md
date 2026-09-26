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

## Continuous integration and releases

The workflows in `.github/workflows` run on the organisation's self-hosted
runners (`[self-hosted, linux, x64]`) and build the book inside the Docker image
described by `Dockerfile`. That image is Ubuntu 26.04 with TeX Live and the
fonts that `special_header.tex` declares. To reproduce the CI build locally:

```
$ docker build --target export --output type=local,dest=out .   # -> out/main.pdf
```

- `ci.yml`, on every pull request and every push to `master`: `make check-refs`
  and `make refs`. It fails on a broken reference, a LaTeX error or a missing
  glyph, and uploads the PDF as the `ymir-book` artifact. `check-listings` is
  not run, because it needs the reference `gyc`.
- `release.yml`, run by hand: publishes the GitHub release `<version>`, where
  the version is read from `VERSION`, with `ymir-book_<version>.pdf` attached.
  The release notes list the pull requests merged since the previous release.
  Only titles of the form `[BOOK-N][kind] Text` are listed. The workflow
  refuses a version that is already released, so bump `VERSION` first.
- `release-preview.yml`, run by hand on any branch: replaces the rolling
  `preview` pre-release and its `ymir-book_preview.pdf`.

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
Dockerfile            CI build environment (see above); VERSION is the next release number
frames/, test/        draft of hand-drawn listing frames, not used by the book yet
BOOK_AUDIT.md         audit of the sources: applied fixes, open decisions, roadmap
BOOK_PLAN.md          structure of the book: the two parts, chapter order, open decisions
BOOK_REVIEW.md        editorial review: contradictions found and fixed
BOOK_STYLE.md         house style: markup, labels, register
progress.org          what is written, chapter by chapter (progress.html is its export)
```

Current chapters:

Part I, Learning Ymir:

1. Fundamentals
2. Fundamental types, constants and variables

Part II, Language specification:

3. Native scalar types
4. Control flows
5. Native compound types
6. Variables and memory management
7. Global constructions

Chapters 3 to 10 of Part I are planned; see `progress.org`.

## Contributing

- Check each code listing against a current `gyc` before committing, and run
  `make check`.
- `BOOK_AUDIT.md` lists the known discrepancies between the book and the
  compiler, and the chapters still to be written. Read it before changing a
  listing that fails to compile, because the fix may belong in the compiler.
