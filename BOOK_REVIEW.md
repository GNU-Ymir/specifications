# Ymir book — editorial review

Companion to `BOOK_AUDIT.md`. That file tracks *technical* correctness (do the
listings compile, do the references resolve, does LaTeX build clean). This file
tracks *editorial* consistency and clarity: places where the book contradicts
itself, states a rule it then breaks, or depends on something it never taught.

Reviewed chapter by chapter. Each item is either **FIXED** (applied, book
rebuilds clean) or **OPEN** (needs an author decision).

---

## Chapter 1 — Fundamentals

Review date: 2026-08-08. Overall: the prose is plain and the progression
(write → compile → run → structure → toolchain) is sound. The problems below
are internal contradictions, not factual errors — the one factual claim worth
checking, that `gyc` also compiles C source files, was verified true
(`gyc t.c -o tc` compiles and runs).

### 1. §1.3 denies using both YIL levels together, then does it — OPEN

`chapters/chapter1/section3.tex:15`

> "In general it won't be necessary to distinguish between the two levels of
> representation, as they won't be used at the same time"

The next thing on the page is the same `hello.yr` dumped to M-YIL and L-YIL in
two adjacent listings. The claim is contradicted before the section ends.

**Fix:** soften to "they are rarely needed together", or drop the clause.

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

§1.1 and §1.2 used 2 spaces, §1.3's `hello.yr` uses 4, §1.5's exercises used 3
(while §1.5's own Exercise 1 solution used 2). Book-wide the de-facto standard
is 2 spaces — 655 listing lines at two, 144 at four, 19 at three.

**Fixed:** §1.5 normalised to 2 spaces throughout.
**Open:** `chapters/chapter1/section3.tex:27` is still at 4.
**Open:** §1.2.2 mandates alignment by scope depth but never fixes the *width*.
Since the section exists to enforce uniformity, it should say "two spaces".
This one is *not* safely mechanisable the way item 2 was — re-indenting cannot
be verified by "no non-whitespace changed", and listings whose prose refers to
specific line numbers must not shift. Worth doing by hand, chapter by chapter.

### 4. The same listing appears twice with the same caption — OPEN

`chapters/chapter1/section1.tex:21` and `chapters/chapter1/section3.tex:23`

Both are `hello.yr`, both captioned *"Source file hello.yr"*, two pages apart,
differing only in indentation (see item 3).

**Fix:** have §1.3 `\ref` back to the §1.1 listing instead of repeating it, or
give the two captions distinct wording.

### 5. §1.1 teaches raw `gyc`; §1.4 assumes Gyllir — OPEN

`chapters/chapter1/section4.tex:7`

> "the Gyllir tool is used to manage the source code, and it is assumed that
> you will use it as well"

Nothing reconciles this with §1.1, which compiles by hand with
`gyc hello.yr -o hello`. A reader who takes §1.4 at its word has no way to
obtain the `-fdump-ymir` output that §1.3 depends on. Exercise 2 says "compile
the program to test your corrections" without saying with which tool.

**Fix:** state explicitly which toolchain the reader is expected to use for the
rest of the book, and show the Gyllir equivalent of the `gyc` invocations, or
say that both are used and when.

### 6. The compilation-step sentence is circular — OPEN

`chapters/chapter1.tex:15`

Three steps are listed; step 2 *is* invoking the compiler. The paragraph then
ends "The second and third steps are generally performed automatically when
invoking the compiler." The intended point is that **linking** happens
automatically in the same invocation.

**Fix:** something like "In practice, a single invocation of the compiler
performs both the compilation and the linking steps."

### 7. The compilation-chain figure shows files the text never mentions — OPEN

`chapters/chapter1/figures/compilation_chain.tex:35,47`

- `lib.a` — a static library, appearing nowhere in the prose. The three-step
  narrative never mentions libraries at all.
- `prog.exe` — a Windows-style extension, while every shell listing in the
  chapter is Linux (`alice@dev:~$ ./hello`).

**Fix:** either introduce libraries in the paragraph that the figure
illustrates, or drop `lib.a` from the figure; and rename `prog.exe` to
something matching the shell listings (`prog`, or `hello`).

---

## Also noted in chapter 1

Not part of the numbered list, but found in the same pass.

### Structural gap — the book never explains its own structure

The chapter opens by promising it "presents the basics of how this book is
structured", but no section does that. The colour legend sits at
`chapters/chapter1/section3.tex:20`, buried inside a section titled *"YIL
language"*, and it is incomplete: it defines yellow (Ymir), teal (M-YIL) and
green (L-YIL), but never the shell style, the error-listing style, or the
corrected-listing style — all of which appear in this same chapter. The grey
specification pages are explained separately, in the preamble.

**Decision needed:** collect all of it in one place — either a short opening
section in chapter 1, or entirely in the preamble beside the grey-page
explanation.

### Terminology

- **"symbol" is load-bearing and never defined.** It is the first noun of §1.1
  (`section1.tex:3`, "composed of symbols of different types") and of §1.2
  (`section2.tex:3`). A beginner has no way to know what it means. One sentence
  would fix it.
- The output device is called **"the console"** (§1.1), **"console output"**
  (Exercise 1) and **"the screen"** (Exercise 3).
- "white characters" → *whitespace characters*; "line returns" → *line breaks*.
  Non-standard English, but used consistently, so it is a decision rather than
  an error.
- Lowercase `ymir` in prose still survives at `chapters/chapter4/section5.tex:338`
  and `chapters/chapter5/section1.tex:261`. Chapter 1's instances are fixed.

### Exercises depend on material the chapter never taught

- **Exercise 3** turns entirely on `print` (only `println` was introduced) and
  on the `\n` escape (never mentioned). Both are the point of the exercise, but
  nothing in the chapter gives the reader a way in.
- **Exercise 2** expects the reader to know that `'you got it right'` is wrong
  because single quotes denote a character literal — character literals arrive
  in chapter 3.
- **Exercise 2's broken program is set in `bashVerb`**, the shell style,
  contradicting the colour legend established in §1.3.
- Three of the chapter's five sections (layout, YIL, Gyllir) have no exercise.

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
literal. **OPEN:** regenerate the listing against the current compiler, or keep
the idealised form and say somewhere that YIL listings are simplified.

### Gyllir, not the book

`chapters/chapter1/section4.tex` faithfully reproduces two rough edges in
Gyllir's own output:

- the project template emits `Hello World !` with a space before the `!`
  (`Gyllir/src/gyllir/repo/defaults.yr:26`), the only such spelling in the book;
- `gyllir run` prints "Compiling 1 modules" and "among 1 changed files of 1".

Better fixed in Gyllir than in the book.

### Version numbers disagree — OPEN

The title page says *"Ymir language specification 1.0"*; `chapters/preamble.tex`
says *"the initial stable release of Ymir, designated version 1.1"* with
libmidgard on "the same version number"; the stdlib installed on this machine is
`/usr/include/ymir/1.2/`. Which version is the book's target?
