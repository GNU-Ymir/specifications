# Ymir book — editorial review

Companion to `BOOK_AUDIT.md`. That file tracks *technical* correctness (do the
listings compile, do the references resolve, does LaTeX build clean). This file
tracks *editorial* consistency and clarity: places where the book contradicts
itself, states a rule it then breaks, or depends on something it never taught.

Reviewed chapter by chapter. Each item is either **FIXED** (applied, book
rebuilds clean) or **OPEN** (needs an author decision).

---

## Chapter 1 — Fundamentals

Review date: 2026-08-08. Second pass 2026-08-09: everything numbered below is
now closed. Overall: the prose is plain and the progression
(write → compile → run → structure → toolchain) is sound. The problems below
are internal contradictions, not factual errors — the one factual claim worth
checking, that `gyc` also compiles C source files, was verified true
(`gyc t.c -o tc` compiles and runs).

**Section numbering shifted.** A new §1.1 (*How this book is structured*) was
added, so the sections named below moved down by one: the old §1.1 *A first
program* is now §1.2, §1.2 *Structure of a simple Ymir program* is §1.3, §1.3
*YIL language* is §1.4, §1.4 *Gyllir* is §1.5. The old numbering is kept in the
items below, since that is what the review found; file paths are unchanged and
are the reliable reference.

### 1. §1.3 denies using both YIL levels together, then does it — FIXED

`chapters/chapter1/section3.tex:15`

> "In general it won't be necessary to distinguish between the two levels of
> representation, as they won't be used at the same time"

The next thing on the page was the same `hello.yr` dumped to M-YIL and L-YIL in
two adjacent listings. The claim was contradicted before the section ended.

Now reads "as they are rarely needed together".

### 2. §1.2.2 stated a spacing rule that §1.5 broke — FIXED

The rule said parameter operators are "always spaced as follows
`foo (a, b, c)`", but Exercise 3 used `fn pause()` / `pause()`, presented as
ordinary code rather than as a bad-layout example.

Resolved by **inverting the rule** (author decision): the attached form
`foo(a, b, c)` is now the standard, and the type-annotation colon attaches to
the name it annotates — `fn foo(a: i32)-> i32`, not `fn foo(a : i32)-> i32`.

`chapters/chapter1/section2.tex` §1.2.2 now reads:

> Spaces surround the binary operators, but the parameter operators `()` and
> `[]` are attached to the name that precedes them, as in `foo(a, b, c)`. In the
> same way, the colon introducing a type is attached to the name it annotates
> and followed by a space, as in `fn foo(a: i32)-> i32`.

Every Ymir listing in chapter 1 was updated to match. Three categories were
deliberately left alone:

- the **YIL dumps** in §1.3 — verbatim `gyc -fdump-ymir` output, not Ymir
  source; the compiler really does print `println (a(#8h) : [c8])`, and
  changing it would make the book misquote the tool;
- the **"arbitrary code layout" example** (`section2.tex:62`) — its point is
  that the compiler accepts any spacing;
- **shell listings.**

**Follow-up — the book-wide sweep. DONE.** Applied across all seven chapters in
one mechanical pass: **653 lines in 34 files**, 809 individual edits. The tool
is checked in as `tools/restyle_listings.py` (`--apply` to write, no argument
for a dry-run diff).

The three rules it enforces, and the exceptions:

| rule | example | not applied to |
|---|---|---|
| call / parameter list attaches | `foo (a)` → `foo(a)` | `if (cond)`, `let (a, b)`, `mut (i32, f32)` — a condition, a destructuring pattern and a tuple type, none of them parameter lists |
| index attaches | `a [0]` → `a[0]` | `copy [1,2]`, `dcopy [..]`, `dmut [i32]`, `mut [i32]`, `let [i,j,k]`, `in [1,2,3]` — array literals, types and patterns |
| type colon attaches | `x : i32` → `x: i32` | nothing; all 190 occurrences were type annotations |

Also applied to the 15 prose `\token{}` uses (`cast!T(V)`, `foo(expand a)`,
`bar(a[0], a[1])`, `ident: T`, …). `\token{mut (mut T)?}` and
`\token{if (out) panic;}` correctly kept their spaces.

Left verbatim, deliberately:

- **`myilVerb` / `lyilVerb` listings** (106 occurrences) — compiler output.
- **`bashVerb` listings** — terminal output.
- **§1.2.1's "Arbitrary code layout example"** — its whole point is that spacing
  is free. Now carries a `%% restyle: skip` marker, honoured by the tool. Use
  that marker for any future listing whose spacing is deliberate.

Verification, in order of strength:

1. **No non-whitespace content changed anywhere.** Every one of the 809 edits
   was checked to be whitespace deletion or `' : '` → `': '`; comparing each
   changed line with all whitespace removed gives a byte-identical result.
   Literals are masked before substitution, so `println("X : ", x)` keeps its
   string intact, and `//` and `/* */` comments are excluded.
2. **`make check-listings` output is byte-identical before and after** —
   87/163 plain listings compile, 70/70 error demos still fail as intended,
   same failure classification. Note this proves nothing got *mangled*, not
   that the style is right: Ymir is whitespace-insensitive, so a wrong
   substitution would still compile. Rule 1 above is where the judgement lives.
3. **`make check-refs`**: 160 labels, 0 broken, 19 pending — unchanged.
4. **`make refs`**: builds clean, 165 pages, 0 missing characters.

### 3. Three different indent widths for Ymir code in one chapter — PARTLY FIXED

§1.1 and §1.2 used 2 spaces, §1.3's `hello.yr` used 4, §1.5's exercises used 3
(while §1.5's own Exercise 1 solution used 2). Book-wide the de-facto standard
is 2 spaces — 655 listing lines at two, 144 at four, 19 at three.

**Fixed:** §1.5 normalised to 2 spaces throughout.
**Fixed:** §1.2.2 now fixes the *width*, not just the alignment: "each level of
depth adding an indentation of two spaces".
**Fixed:** the 4-space `hello.yr` at `section3.tex:27` went away with the
duplicate listing (item 4).
**Open — approved, not yet applied:** the book-wide sweep of the remaining
listings at 3 and 4 spaces. This one is *not* safely mechanisable the way item 2
was — re-indenting cannot be verified by "no non-whitespace changed", and
listings whose prose refers to specific line numbers must not shift. To be done
chapter by chapter, leaving `myilVerb`/`lyilVerb` (compiler output) alone.

### 4. The same listing appears twice with the same caption — FIXED

`chapters/chapter1/section1.tex:21` and `chapters/chapter1/section3.tex:23`

Both were `hello.yr`, both captioned *"Source file hello.yr"*, two pages apart,
differing only in indentation (see item 3).

The §1.1 listing now carries `label=lst:hello_world`, and §1.3 refers to it
(*"the hello.yr source file presented in Listing~\ref{lst:hello_world}"*)
instead of repeating it.

### 5. §1.1 teaches raw `gyc`; §1.4 assumes Gyllir — FIXED

`chapters/chapter1/section4.tex:7`

> "the Gyllir tool is used to manage the source code, and it is assumed that
> you will use it as well"

Nothing reconciled this with §1.1, which compiles by hand with
`gyc hello.yr -o hello`. A reader who took §1.4 at its word had no way to obtain
the `-fdump-ymir` output that §1.3 depends on.

§1.4 now says which tool is used where: `gyc` directly for the short single-file
examples and whenever the intermediate representations are examined, Gyllir as
soon as a program has several source files or an external dependency. Exercise 2
now names the tool as well ("compile the program with `gyc`").

### 6. The compilation-step sentence is circular — FIXED

`chapters/chapter1.tex:15`

Three steps were listed; step 2 *was* invoking the compiler. The paragraph then
ended "The second and third steps are generally performed automatically when
invoking the compiler." The intended point is that **linking** happens
automatically in the same invocation.

Now: "In practice, a single invocation of the compiler performs both the
compilation and the linking steps."

### 7. The compilation-chain figure shows files the text never mentions — FIXED

`chapters/chapter1/figures/compilation_chain.tex:35,47`

- `lib.a` — a static library, appearing nowhere in the prose. The three-step
  narrative never mentioned libraries at all.
- `prog.exe` — a Windows-style extension, while every shell listing in the
  chapter is Linux (`alice@dev:~$ ./hello`).

`prog.exe` is now `prog`. `lib.a` was kept, and the prose it illustrates now
introduces it: "The linker also pulls in the code of the libraries that the
program uses, such as the standard library, which are distributed as archives of
already compiled object files."

---

## Also noted in chapter 1

Not part of the numbered list, but found in the same pass.

### Structural gap — the book never explains its own structure — FIXED

The chapter opened by promising it "presents the basics of how this book is
structured", but no section did that. The colour legend sat at
`chapters/chapter1/section3.tex:20`, buried inside a section titled *"YIL
language"*, and it was incomplete: it defined yellow (Ymir), teal (M-YIL) and
green (L-YIL), but never the shell style, the error-listing style, or the
corrected-listing style — all of which appear in this same chapter. The grey
specification pages were explained separately, in the preamble.

Resolved by **a new opening section** (author decision):
`chapters/chapter1/structure.tex`, §1.1 *How this book is structured*. It states
the reading order and the exercise/solution structure, explains the white and
light-grey pages, and carries the complete legend — every listing style with its
badge and its background colour, plus the `\hb`/`\hcb` highlights used in
error demos. The partial legend was deleted from §1.3, which now only refers to
the new section. Everything is described in one place, and the chapter's opening
promise is delivered.

### Listing badges — colour is no longer the only cue — NEW, DONE

The legend above rests entirely on background colour, which does not survive a
black and white print and is hard to read for a colour blind reader. Every
display listing now also carries a **badge in its top right corner**: a small
glyph plus the name of the language.

| badge | style | listings |
|---|---|---|
| sheet `Y` — *Ymir* | `coloredverbatim`, `coloredverbatimCorrect` | source code |
| sheet `M` — *M-YIL* | `myilVerb` | compiler output |
| sheet `L` — *L-YIL* | `lyilVerb` | compiler output |
| terminal `$_` — *Terminal* | `bashVerb` | shell sessions |
| warning triangle — *Invalid Ymir* | `coloredverbatimError` | code that must not compile |

The shapes differ (sheet, box, triangle), so the distinction holds in
greyscale; the label carries it even if the icon is missed.

Implementation, in `special_header.tex`, above the style definitions:

- a listings key, `badge=`, set **inside each style**, so no call site had to
  change for the four existing styles;
- an `Init` hook that typesets the badge flush with the right edge of the band
  of colour (`\linewidth + \lst@xleftmargin`), in a zero-height box, so the
  listing itself does not move;
- guarded by `\lst@ifdisplaystyle`. This matters: `\token{}` is
  `\lstinline[style=coloredverbatim]`, used hundreds of times in the prose, and
  without the guard every inline token would grow a badge.

### The error-demo marker is now standardised — NEW, DONE

`BOOK_AUDIT.md` §3.4 item 2 asked for one spelling instead of five. The badge
work supplies it: a listing whose code must not compile uses
`style=coloredverbatimError` (identical presentation to `coloredverbatim`, only
the badge differs). All **71** error demos were converted, and
`tools/check_listings.py` now treats that style as the marker — the old inline
spellings (`// error`, `// not allowed`, …) are still accepted for the comments
that explain *which* line is at fault, which is a separate job.

The conversion is mechanical and was driven by the checker's own
`expects_error()`, so exactly the listings it already classified as error demos
were rewritten. `check-listings` reports the same 71/71 before and after.

This also fixed the item below: Exercise 2's broken program was set in
`bashVerb`, the shell style, contradicting the legend. It is now
`coloredverbatimError`, and reads as what it is — invalid Ymir. Its stray
comment-opening `/*` is wrapped in an `escapechar` escape so that `listings`
does not treat the rest of the program as a comment.

### Terminology — FIXED

- **"symbol" is load-bearing and never defined.** It was the first noun of §1.1
  (`section1.tex:3`, "composed of symbols of different types") and of §1.2
  (`section2.tex:3`). A beginner had no way to know what it means. §1.1 now
  defines it in the sentence that follows: "A symbol is a named entity declared
  in a source file, such as a function, a variable or a type; the name is what
  the rest of the program uses to refer to it."
- The output device was called **"the console"** (§1.1), **"console output"**
  (Exercise 1) and **"the screen"** (Exercise 3). Now "the console" everywhere.
- "white characters" → *whitespace characters*, "line returns" → *line breaks*.
  Both spellings occurred twice in total, only in chapter 1, while chapter 2
  already said "line breaks"; converted rather than kept.
- Lowercase `ymir` in prose: the two survivors in `chapter4/section5.tex` and
  `chapter5/section1.tex` are fixed. None left.

### Exercises depend on material the chapter never taught — FIXED

- **Exercise 3** turned entirely on `print` (only `println` had been introduced)
  and on the `\n` escape (never mentioned). §1.2 now introduces both, in the
  paragraph that follows the `hello.yr` listing: `println` ends its text with a
  line break, `print` does not, and `\n` writes one inside a literal.
- **Exercise 2** expected the reader to know that `'you got it right'` is wrong
  because single quotes denote a character literal — character literals arrive
  in chapter 3. The same paragraph now says that a string literal is enclosed in
  double quotes, single quotes being reserved for character literals, and points
  at chapter~3 for both those and the escape sequences.
- **Exercise 2's broken program was set in `bashVerb`** — see the error-demo
  section above.

### Three sections had no exercise — FIXED

Layout, YIL and Gyllir were untested. Three exercises were added, with
solutions, in the existing format:

- **Exercise 4** — a correct program written in a deliberately bad layout, to be
  rewritten following §1.3. Carries `%% restyle: skip`, since its layout is the
  point.
- **Exercise 5** — an M-YIL dump of a two-function program: name the file it was
  written to, the command line that produced it, and what the program prints.
  The dump was taken from the real `gyc -fdump-ymir` output for an equivalent
  source file, then simplified the way the book's other YIL listings are.
- **Exercise 6** — create a project with Gyllir that prints a given line: which
  commands, and which file to edit.

The three new Ymir listings compile (`check-listings`, chapter 1: 7/8 plain, the
one failure being the pre-existing "arbitrary layout" fragment that calls an
undefined `bar`).

Also fixed while there: `\section*{Exercises}` and `\section*{Solutions}` left
the running head of the previous section on their pages (*"1.4. GYLLIR"* above
the exercises). Both now set it with `\markright`.

### Typos fixed in this pass

Applied directly, no decision needed. Grammar and agreement throughout
(`This chapters presents`, `developement`, `uppon invokation`, `writting`,
`comas`, `arbitry`, `Prefered`, `Everyting`, `reprensentation`, `to form a an
executable file`, lowercase `ymir`, …), plus:

- `chapters/chapter1/figures/compilation_chain.tex:48` — a stray `;` after
  `\gearicon{…}`, typeset in `nullfont`. This was the book's **last**
  missing-character warning; the build is now at zero.
- `chapters/chapter1/section4.tex` — `\japan{└──~\color{teal}{…}` never closed
  its brace, swallowing the rest of the line into the CJK font.
- `chapters/chapter1/section4.tex` — the `tree` listing reported "3 directories,
  3 files" for a tree containing 2 directories.
- `chapters/chapter1/section5.tex` — Exercise 2's solution silently rendered
  `fn main () {` while marking every *other* correction with `\hcb{}`. The
  added `()` is now highlighted like the rest.

### Compiler bug found while checking chapter 1

`gyc -fdump-ymir` prints the entry-point frame as

```
_yrt_run_main(argc(#1), argc(#2), &_Y5hello4mainFZv);
```

passing `argc` twice, though `argv(#2)` is declared on the line above. The book
reproduced this faithfully. Cause is one wrong string literal in
`gcc/ymir/bootstrap/src/ymirc/lint/expander/frame.yr:213`:

```ymir
let argvRef = copy YILVar(EOF_WORD, "argc", argsT[1], argIds[1]);
```

The variable *id* is correct, so code generation is unaffected — it is purely
the dump's label. The book now says `argv(#2)`; **the compiler still needs the
one-word fix.**

Related, same listing: today's dumper has drifted from what chapter 1 shows in
three more ways — `frame:` with no space before the colon, `T_9` in place of the
spelled-out `(len-> u64, ptr-> *(u8))`, and an extra `blk_info-> 0` in the slice
literal. **Resolved on the book's side** (author decision): the idealised form is
kept, and §1.3 now says so — "The YIL listings of this book are simplified for
readability: they follow the structure of what the compiler actually prints, but
omit some of the internal annotations it emits." Exercise 5's new M-YIL listing
follows the same convention.

### Gyllir, not the book

`chapters/chapter1/section4.tex` faithfully reproduces two rough edges in
Gyllir's own output:

- the project template emits `Hello World !` with a space before the `!`
  (`Gyllir/src/gyllir/repo/defaults.yr:26`), the only such spelling in the book;
- `gyllir run` prints "Compiling 1 modules" and "among 1 changed files of 1".

Better fixed in Gyllir than in the book.

### Version numbers disagree — FIXED

The title page said *"Ymir language specification 1.0"*; `chapters/preamble.tex`
said *"the initial stable release of Ymir, designated version 1.1"* with
libmidgard on "the same version number"; the stdlib installed on this machine is
`/usr/include/ymir/1.2/`.

**1.2** is the book's target. `main.tex` (title and PDF metadata) and the
preamble now both say so. Gyllir stays at 1.0, which is its own version.

---

## State of the book after this pass

Measured on 2026-08-09, after every change above:

| | |
|---|---|
| `make refs` | 169 pages, builds clean |
| missing characters | **0** |
| `make check-refs` | 163 labels, 0 broken, 19 pending (unwritten material), 0 duplicated |
| `make check-listings` | 89/165 plain listings compile, **71/71** error demos fail as intended, 3 skipped |

The 76 plain listings that do not compile are unchanged in cause and count by
this pass, and are `BOOK_AUDIT.md`'s subject, not this file's: 42 `unused`,
23 `undefined-symbol`, 5 `const-assert`, 3 `stale-stdlib`, 3 `other`.

## What is left

In order of how much they block other work:

1. **The indentation sweep** (item 3). Approved, not yet applied: the listings
   still at 3 and 4 spaces, chapter by chapter, leaving compiler-output and
   shell listings alone.
2. **The `argc`/`argv` one-word fix in the compiler**
   (`lint/expander/frame.yr:213`). The book is already correct; the compiler is
   not.
3. **Chapters 2 to 7 have not had an editorial pass.** Only their technical
   audit exists. Chapter 1's pass found seven contradictions in five sections,
   so the others should not be assumed clean.
4. **Exercises for chapters 2 to 7.** Chapter 1 now has six with solutions;
   every other chapter has none, and `progress.org` still lists them as TODO.
5. **`progress.org` is stale** — it describes chapters 3 to 7 as `TODO`/`START`
   though all seven are drafted. See `BOOK_AUDIT.md` §3.3.
