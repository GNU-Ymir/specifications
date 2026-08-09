# Ymir book — editorial review

Companion to `BOOK_AUDIT.md`. That file tracks *technical* correctness (do the
listings compile, do the references resolve, does LaTeX build clean). This file
tracks *editorial* consistency and clarity: places where the book contradicts
itself, states a rule it then breaks, or depends on something it never taught.

Chapters 1, 2 and 3 have had an editorial pass; chapters 4 to 7 have not.
Everything found so far is fixed except the one **OPEN** item below.

## Open

- `chapters/chapter3/section3.tex:80` — `assert(e == b)` on two
  compile-time-constant char literals fails as `const-assert`. Not a chapter 3
  bug: `BOOK_AUDIT.md` §2.1 item 4, 5 listings book-wide. `assert` is the book's
  main idiom for "these two are equal", so changing this one alone would just
  trade one inconsistency for another. Author call: relax the diagnostic, or
  switch the book's idiom to `println` + expected output.

## State of the book

Measured 2026-08-09, after every change below:

| | |
|---|---|
| `make refs` | 173 pages, builds clean |
| missing characters | **0** |
| `make check-refs` | 163 labels, 0 broken, 19 pending (unwritten material), 0 duplicated |
| `make check-listings` | 99/171 plain listings compile, **72/72** error demos fail as intended, 4 skipped |

The 72 non-compiling plain listings are `BOOK_AUDIT.md`'s subject, not this
file's: 39 `unused`, 22 `undefined-symbol`, 5 `const-assert`, 3 `stale-stdlib`,
3 `other`.

## What is left

In order of how much they block other work:

1. **The indentation sweep** (`BOOK_AUDIT.md` item 3). Approved, not applied:
   listings still at 3 and 4 spaces, chapter by chapter, leaving compiler-output
   and shell listings alone.
2. **Editorial pass on chapters 4 to 7.** Only their technical audit exists.
   Chapter 1's pass found seven contradictions, chapter 2's four, chapter 3's
   four — do not assume the rest are clean.
3. **Exercises for chapters 3 to 7.** Chapters 1 and 2 have them (six and seven,
   with solutions); no other chapter does.
4. **`progress.org` is stale** — lists chapters 3 to 7 as `TODO`/`START` though
   all seven are drafted. See `BOOK_AUDIT.md` §3.3.

## Rules confirmed with the author

Worth keeping; several book errors came from getting these wrong.

- A bare (unsuffixed) char literal is **always** `c8`, with no exception for
  wide characters — so `'π'` does not compile, it needs `'π'c32`.
- A decimal float literal needs **both** parts: `10.` is invalid, write `10.0`.
  Scientific (`3.e-10`) and hexadecimal (`0xA.p4`) notation are unaffected and
  still accept an empty fractional part.
- The operator families are named **Bitwise**, **Comparisons**, **Logical**
  (`&&`/`||` only) and **Assignment**. "Byte", "Logical" for comparisons, and
  "Affectation" were all mistakes and are gone from the book.

## Gotcha

`tools/check_listings.py` locates a `%% check: skip` annotation by walking back
to the *previous newline*, so it silently fails to attach when
`\begin{lstlisting}` is indented — which is most listings, since they sit inside
an `itemize`. Dedent the `\begin{lstlisting}` line to make the annotation take
effect, or fix the tool.

## Fixed

### Chapter 1 — Fundamentals
### Chapter 2 — Fundamental types, constants and variables

Done; see git history (`Review chapter 2`, `fix: first editorial pass`).

### Chapter 3 — Native scalar types

Correctness:

- Integers §Binary operators: `>>` and `<<` were labelled with each other's
  meaning, contradicting their own worked examples.
- Integers §Implicit casting: spelled out why both `foo` overloads match
  (`1u8` converts implicitly to both `i32` and `usize`).
- Floats §Literals: intro promised "three forms" but named two; added
  hexadecimal. Rewrote the decimal item for the `10.0` rule and normalised ~20
  `N.` to `N.0` across tables and prose.
- Floats intro table: `f80` had 16 exponent / 63 mantissa bits; x87 extended is
  1 + 15 + 64 (no implicit bit). The two errors cancelled in the sum.
- Floats §Properties: `min` was defined as `-max`, contradicting the caution box
  right below it and the `float_value_pict` figure → "the smallest positive
  normalized value".
- Floats §Casting: "truncated to the floor value" is wrong for negatives →
  "truncated towards zero", with a negative example. Separately, "Floating point
  values cannot be converted to other types" directly contradicted the cast
  paragraph above it → narrowed to "aside from these two cases".
- Floats arithmetic table: `7. / 3. == 2.333` and `7.23 % 3.09 == 1.05` are
  false as exact equalities → switched to the section's own `<=>`.
- Booleans §Binary operators: unparenthesised examples parsed the wrong way
  (`true && false == false` is `true`) → parenthesised.
- Booleans §Casting: `1u8 == 1u8` is a tautology, not an int→bool example →
  `x != 0u8`.
- Chars §Casting: "not possible to implicitly convert a char to another type",
  contradicted by the §Implicit casting subsection below it → "apart from the
  `cte` case described below".
- Chars §Binary operators: char-as-right-operand holds for `+` only (`-` is
  marked non commutative) → restricted, with the subtraction case spelled out.
- Chars §Literals / §Overflowing: both examples used a bare `'π'`, which cannot
  compile under the `c8` rule → §Literals now uses `'a'` (pointing at the
  chapter's `c32` listing for the rest), §Overflowing uses `'π'c32 + 501u32` so
  it reaches the runtime case it illustrates.
- Chars: missing semicolon on `assert(a == 'l')`; added a comment noting
  `'\u{10}'` is decimal, which is what makes the `'\n'` assert hold.

Naming, book-wide (all three confirmed with the author, see rules above):

- "Byte" → "Bitwise": chapter 2 §3 prose and precedence table, seven
  occurrences in chapter 3 §Integers. None in chapters 4–7.
- "Logical" → "Comparisons" for the comparison groups in chapter 3 §§1–3
  (§Boolean's real `&&`/`||` group untouched); chapter 4 §Pointers' `\item
  Logical: Comparison operators…` → "Comparison"; chapter 2 §3's operator-family
  bullet, which contradicted its own next bullet and precedence table.
- "Affectation" → "Assignment", all 22 occurrences: chapter 2's precedence
  table, chapter 3 §§1–4, chapter 4 §§2–7, chapter 6 §2, chapter 7 §2. Chapter 2
  prose already said "assignment".

Clarity: chars intro now states that a `c8`/`c16` is an encoding *unit*, not
necessarily a whole character (the premise §Overflowing rests on); integers
§Overflowing reworded so the compile-time/runtime split reads as one rule; the
`<=>` description ("equal to the right operand delta the epsilon value") was
unparseable. Typos: `implicitely`, `Exponant`, "Rest of the division" →
"Remainder", "0 byte" → "0 bytes", and several singular/plural slips.

Listings (4 moved out of `failed`, 4/9 → 7/8): three casting listings and one
`Implicit casting` listing tripped the `unused` check — fixed by `println`-ing
the values, which also shows the reader the actual result instead of a bare type
annotation. The `&&`/`||` short-circuit example calls an undefined `foo()` by
design (a narrative stand-in), so it got `%% check: skip` per `BOOK_AUDIT.md`
§2.3 — see the gotcha above.
