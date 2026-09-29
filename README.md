# Ymir Book

The sources of the Ymir presentation book. It is written for new developers,
including people with no prior computer science background, who want to learn
the [Ymir](https://github.com/GNU-Ymir) language. It is a training course, not a
language specification.

## Requirements

- `lualatex` (TeX Live) with the packages loaded in `special_header.tex`
  (`fontspec`, `listingsutf8`, `tcolorbox`, `awesomebox`, `minitoc`, `tikz`, …)
- `rsync`, used to stage the sources into the build directory
- Optional, for the consistency checks: `python3` and `ymirc`, the in-development `gyc` driver

## Building the book

```
$ make        # quick single-pass build: no table of contents, unresolved refs
$ make refs   # full three-pass build with table of contents and cross-references
$ make clean  # remove the .build directory
```

Sources are copied to `.build/`, compiled there, and the result is copied back
as `main.pdf`.

## Compiler error codes

The compiler error codes are a separate document, `error_codes.pdf`, with one
page per code. It is built only on request:

```
$ make error-codes      # full build of error_codes.pdf
$ make gen-error-codes  # regenerate its sources from the compiler
```

`tools/gen_error_codes.py` converts the compiler's own pages,
`docs/errors/E*.md` of the bootstrap repository
(`~/ymir/ymir-dev/repos/bootstrap`, `BOOTSTRAP=path` overrides it), into
`chapters/appendix/codes/`. Do not edit those files by hand. The codes are
grouped by the themes of `tools/error_themes.txt`. The generator refuses to run
while a live code has no theme there, or a theme lists a code that is not live.

The versions of `gyc` and Gyllir that the book documents are Makefile
variables, `GYC_VERSION` and `GYLLIR_VERSION`. They are typeset through the
`\gycversion` and `\gyllirversion` macros. Override them on the command line:

```
$ make refs GYC_VERSION=1.3 GYLLIR_VERSION=1.1
```

## Examples

`examples/` holds the complete programs of the course, one file per program,
grouped by chapter (`examples/functions/`). The book reads them with
`\lstinputlisting`, so a listing and its file cannot drift apart. They are
published with each release as a zip archive:

```
$ make examples   # -> examples.zip
```

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
  compilable unit and compiles it with `gyc -c`. A `\lstinputlisting` is
  checked with the file it reads, and an example file that no listing shows is
  compiled as is; the programs of `examples/` are linked too. Listings that
  deliberately show an error or are not standalone can be annotated on the line
  above `\begin{lstlisting}`:

  ```latex
  %% check: error   -- must fail to compile
  %% check: skip    -- narrative fragment, not compilable on its own
  ```

  Use `--only SUBSTR`, `--verbose` or `--dump FILE:LINE` to investigate a
  single listing.

## Releases

The book is built only when a release is triggered. The release workflows in
`.github/workflows` are run by hand from the Actions tab. They run on the
organisation's self-hosted runners (`[self-hosted, linux, x64]`) and build the
book inside the Docker image described by `Dockerfile`. That image is Ubuntu
26.04 with TeX Live and the fonts that `special_header.tex` declares. The build
runs `make check-refs`, `make refs`, `make error-codes` and `make examples`, and fails on a
broken reference, a LaTeX error or a missing glyph. `check-listings` is not run, because it needs
the reference `gyc`. To reproduce the release build locally:

```
$ docker build --target export --output type=local,dest=out .   # -> out/main.pdf, out/error_codes.pdf, out/examples.zip
```

- `release.yml`: publishes the GitHub release `<version>`, where the version
  is read from `VERSION`, with `ymir-book_<version>.pdf` and
  `ymir-error-codes_<version>.pdf` and `ymir-book-examples_<version>.zip`
  attached. The release
  notes list the pull requests merged since the previous release. Only titles
  of the form `[BOOK-N][kind] Text` are listed. The workflow refuses a version
  that is already released, so bump `VERSION` first.
- `release-preview.yml`, on any branch: replaces the rolling `preview`
  pre-release and its `ymir-book_preview.pdf`, `ymir-error-codes_preview.pdf`
  and `ymir-book-examples_preview.zip`.

## Layout

```
main.tex              entry point, includes the chapters in order
error_codes.tex       entry point of the separate error-code document
special_header.tex    preamble: packages, fonts, listing styles, macros
chapters/
  preamble.tex        introduction to the book
  course/             Part I, one chapter per label topic (basics, types, control,
                      functions, collections)
  spec/               Part II (notation, scalars, flow, compound, memory, global,
                      compr, error, lazy)
    flow.tex          chapter title, intro text, and \input of its sections
    flow/sectionM.tex
    flow/figures/     TikZ figures, \input from the sections
  appendix/codes.tex  compiler error codes; codes/ is generated, see above
examples/             complete programs of the course, read by the book and zipped for release
tools/                consistency checkers, error-code generator
Dockerfile            release build environment (see above); VERSION is the next release number
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
3. Control flow
4. Functions
5. Compound types and collections

Part II, Language specification:

4. Native scalar types
5. Control flows
6. Native compound types
7. Variables and memory management
8. Global constructions
9. Comprehensions
10. Error handling
11. Laziness

Chapters 6 to 14 of Part I are planned, and so are their missing Part II
counterparts; see `BOOK_PLAN.md` and `progress.org`.

## Contributing

- Check each code listing against a current `gyc` before committing, and run
  `make check`.
- `BOOK_AUDIT.md` lists the known discrepancies between the book and the
  compiler, and the chapters still to be written. Read it before changing a
  listing that fails to compile, because the fix may belong in the compiler.
