# Ymir book — editorial review

Companion to `BOOK_AUDIT.md`. That file tracks *technical* correctness (do the
listings compile, do the references resolve, does LaTeX build clean). This file
tracks *editorial* consistency and clarity: places where the book contradicts
itself, states a rule it then breaks, or depends on something it never taught.

The book was split into two parts on 2026-08-09 (see `BOOK_PLAN.md`), so
chapter numbers below refer to the **old** numbering: chapters 1 and 2 are now
part I, and old chapters 3, 7, 4, 6, 5 are part II chapters 3 to 7, in that
order.

Chapters 1 to 5 have had an editorial pass; old chapters 6 and 7 have not.
Everything found so far is fixed except the two **OPEN** items below.

## Open

- `chapters/chapter3/section3.tex:66` — `assert(e == b)` on two
  compile-time-constant char literals fails as `const-assert`. Not a chapter 3
  bug: `BOOK_AUDIT.md` §2.1 item 4, 5 listings book-wide. `assert` is the book's
  main idiom for "these two are equal", so changing this one alone would just
  trade one inconsistency for another. Author call: relax the diagnostic, or
  switch the book's idiom to `println` + expected output.
- `chapters/chapter5/section2.tex:304` — §Body still teaches the brace-less
  function body (`fn foo (a: i32)-> i32` then `a + 1` on the next line), which
  the parser rejects: it demands `{` or `;` after the prototype. Already
  `BOOK_AUDIT.md` §2.1 item 2, unchanged; the surrounding prose is built around
  the form, so it needs the author's decision (restore it in the compiler, or
  rewrite the subsection) rather than a local edit.

## State of the book

Measured 2026-08-10, after the style pass (see `BOOK_STYLE.md`):

| | |
|---|---|
| `make refs` | 204 pages, builds clean |
| missing characters | **0** |
| overfull boxes | **0** (19 before the pass) |
| `make check-refs` | 157 labels, 0 broken, 18 pending (unwritten material), 0 duplicated |
| `make check-listings` | 113/162 plain listings compile, **80/80** error demos fail as intended, 14 skipped |

The page count rose from 182 because the text block narrowed from 18.4cm to
15cm; the label count fell from 163 because 26 dead org-export labels went and
six new section labels arrived. The listing figures are unchanged.

The 49 non-compiling plain listings are `BOOK_AUDIT.md`'s subject, not this
file's: 31 `unused`, 11 `undefined-symbol`, 4 `const-assert`, 3 `other`. The
`stale-stdlib` class is empty: the installed standard library now parses under
the reference compiler, the author having fixed the two during the chapter 5
pass.
The three `other` are exactly the three open compiler/book discrepancies of
`BOOK_AUDIT.md` §2.1 (brace-less bodies, `do`/`while`, list comprehension over a
tuple).

## What is left

In order of how much they block other work:

1. **The indentation sweep** (`BOOK_AUDIT.md` item 3). Approved, not applied:
   listings still at 3 and 4 spaces, chapter by chapter, leaving compiler-output
   and shell listings alone.
2. **Editorial pass on the two unreviewed part II chapters** (old 6 and 7). Only their technical audit exists.
   Chapter 1's pass found seven contradictions, chapter 2's four, chapter 3's
   four, chapter 4's eight, chapter 5's seven — do not assume the rest are
   clean. Chapters 3 and 5 to 7 are light gray, i.e. specification: judge them
   on template uniformity and completeness (does every construct get the same
   subsections, does every rule have an entry), not on how they read.

   The style pass of 2026-08-10 covered the *surface* of all seven chapters —
   markup, register, section templates — and rewrote the prose of part I
   chapter by chapter. It did not look for contradictions, which is what this
   item is about, and it changed no technical claim anywhere.
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
- **`.yri` header files are not a thing.** The compiler has no notion of the
  extension; `-I` takes an ordinary source file. Bodiless prototypes survive as
  the mechanism, so a package can still be shipped as prototypes plus a binary —
  but the file has to be named after the module it declares, like any other.

## Gotchas

`tools/check_listings.py` locates a `%% check: skip` annotation by walking back
to the *previous newline*, so it silently fails to attach when
`\begin{lstlisting}` is indented — which is most listings, since they sit inside
an `itemize`. Dedent the `\begin{lstlisting}` line to make the annotation take
effect, or fix the tool.

A `//` comment on the last line of a file is reported by the compiler as
`unterminated comment block` when the file does not end with a newline. Probably
a lexer bug, and worth a look — the harness now always appends the newline, which
is what moved 11 listings out of `undefined-symbol` during the chapter 5 pass.

`escapechar=@` and the `@` of an attribute cannot coexist: `@thread` inside such
a listing is silently eaten and the surrounding lines collapse into each other in
the PDF. Use `escapechar=$`, as `chapter5/section2.tex` §Unsafe function already
does. Book-wide, no other listing mixes the two.

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

### Chapter 4 — Native compound types

Correctness:

- Pointers §Binary operators: the comparison table gave
  `(&a < &a + 1us) == false`, contradicting the `>` row directly above it →
  `== true` (checked against the compiler).
- Pointers §Index operator: the rewrite of `(&a)[7]` was missing a closing
  parenthesis, so the expression it defines does not parse.
- Tuples §Literals: `(1, 'r', false)` was typed `(i32, c32, bool)`. A bare char
  literal is `c8` (the rule confirmed for chapter 3), and the compiler agrees →
  `(i32, c8, bool)`. The §Tuple iteration YIL dump had the same `c32` in three
  places; replaced with the compiler's actual output.
- Tuples §Properties: the table was the pointer table with `init` typed `usize`
  and a *second* `init` row where `typeid` belonged → `typeof(x)` and `typeid`.
  Its intro still said "Pointer type properties".
- Tuples §Binary operators: the access example used `a._0`/`a._1` while the
  section's own text ("the right operand must be of type int"), its YIL dumps and
  chapter 6 all use `a.0`/`a.1`. Both spellings compile; the book now uses one.
- Tuples §Tuple deconstruction: the YIL dump closed a set with `{# … #}` in one
  of the three blocks, `#{ … #}` in the other two.
- Arrays §Properties: the `init` row stopped mid-sentence — "where all inner
  values are set to" — with the value missing.
- Slices §Mutability: `let dmut a: [[i32]] = [[1], [2], [3]]` breaks the rule the
  same section states five lines earlier (an array literal needs `copy` to become
  a slice) and does not compile → `copy [copy [1], copy [2], copy [3]]`.
  Separately, "slices with a mutability of 2 or higher" contradicted the sentence
  above it, which gives slices exactly three levels, 0 to 2.
- Slices §Slice iteration: the YIL dump was for a different program than the
  listing above it (it assigned `elem + 1` where the listing asserts).
- Slices §Dollar operator: `a[$ - 1]` was commented "the second value to the
  last"; it is the last one.
- Slices §Inheritance: the paragraph is about slices but said "an **option**
  value can be implicitly casted from `[B]` to `[A]`", and justified the reverse
  direction by "as for array casting" — arrays have no such section. Now
  self-contained.
- Options §Literals: the `let b: void? = (match …)?` declaration was missing its
  `;` and does not parse without it.
- Options §Binary operators: "divided into four groups", then lists three
  (Access, Comparison, Assignment). The `error` field was glossed "the value
  contained in the option", same as `value`.
- Options §Pattern matching: `(throw AssertError ("failure"))?` — exceptions are
  class instances, so `throw copy AssertError (…)`, as the §Literals listing
  already writes it.
- Pointers and Options both carried a `$^1$` footnote marker on the
  "Greater or equal" / "Lower or equal" rows with no note attached to it.

Naming and clarity: "Affection operators" → "Assignment" (the one the chapter 3
sweep missed, `Affectation` being the spelling it looked for); four spellings of
"memory alignement" → "alignment"; "Inheritence" → "Inheritance"; the pointer
§Unary operators paragraph said "this operation is unsafe" twice in four lines;
`scd` was "the last value" in the range intro and "the second value" in its own
field table. Typos: `implicitely`/`implictely` (nine), `Substraction`, `inboud`,
`dolalr`, `optionnaly`, `inital`, `wether`, `dicard`, `implict`, `iif` (twice),
"the properties are as follows: following:", "operands.Concatenation", plus
"a lvalue"/"a rvalue"/"a unsafe" and several singular/plural slips.

Completeness, second pass. The first pass read chapter 4 as prose; chapter 4 is
a **light gray chapter**, i.e. specification (`chapters/preamble.tex:11`, "not
intended to be read during the initial reading"). Judged as a lookup surface,
what matters is that the per-type template is uniform and that every rule has an
entry — so a second pass fixed the gaps that judgement exposes:

- Slices had **no `\subsection{Literals}`**, the only type in the chapter
  without one, though `copy [1, 2, 3]` is used from the section's third
  paragraph onward. Added, specifying the two forms that *are* slice literals:
  `[]` (borrows nothing, so no `copy`) and the string literal (text segment,
  `[c8]` unsuffixed, `s8`/`s32` suffixes, never mutable without `copy`). All
  checked against the compiler.
- Slices and options had **no `\subsection{Implicit casting}`**, though the
  compiler applies the same `cte`-only rule tuples and arrays already document.
  Added to both, mirroring the array wording.
- Ranges have no such rule — `let a: ..usize = 0 .. 2` is an error, the inner
  type comes only from the operands. Added a short §Implicit casting saying so,
  so that all six types now answer the casting question explicitly rather than
  four answering and two staying silent.
- The casting subsections had **four names for parallel content**: pointers
  "Casting", tuples/arrays "Implicit casting", slices/options "Inheritance and
  casting". Pointers → "Explicit casting", with the missing statement that no
  implicit conversion between pointer types exists.
- Pointers had `\subsection{Mutability}` where every other type has "Mutability
  and memory alignment", and the section never gave a pointer's size. Renamed,
  and the size and alignment of a `usize` stated (verified: `(*i32)::size` is
  `usize::size` is 8).
- **Chapter 4 never cross-referenced chapter 6.** It refers out to `for` loops,
  structures, pragmas, error handling, string literals and custom types, but
  `alias`/`copy`/`dcopy` and mutability levels — which nearly every section
  rests on — pointed nowhere. `chapter6/section7.tex` (*Memory movement without
  variables*) had no label; added `sec:memory_movement`, and referenced it plus
  `sec:variable_mutability` from the chapter 4 preamble and from slice
  §Mutability. `sec:arrays` added for the same reason.
- Register: three first-person hedges out of otherwise neutral spec prose ("a
  bit of cheating going on here", "One can argue that", "For the sake of
  simplicity, we can say").
- "divided into 3 groups" vs "three groups" — words everywhere now, in chapter 3
  as well as chapter 4.

Found while measuring the above, and **fixed beyond the editorial scope** —
revert if the layout is meant to stay abstract. Slices are specified as "a
pointer `*T` … and a `usize`", i.e. two words, but `([i32])::size` is 24. The
compiler's `SliceCtorValue`
(`gcc-src/gcc/ymir/bootstrap/src/ymirc/semantic/generator/value/literal/slice.yr:85-107`)
carries `ptr`, `len` and `blk`, the block metadata used when appending. The
two-word model also made the array §String-literal arithmetic wrong: two slices
are 48 bytes, not the 32 the book computed.

Listings (5 moved out of `failed`, 99 → 104): the array and slice §Index,
§Dollar and §String-literal listings tripped the `unused` check — fixed by
`println`-ing the results, which also shows the reader what the range index and
`$` actually select. The remaining chapter 4 `unused` failures are syntax demos
(`let c: i32 = (23); // int value`) or feed a YIL dump that shows the value
*being* unused, so a `println` would invalidate the dump printed right below.
Two array/slice iteration comments claimed `println(elem)` prints `1 2 3 4` on
one line → `print(elem, ' ')`, as the range section already does.

### Chapter 5 — Global constructions

Correctness (all seven checked against the reference compiler):

- §Functions §The main function: the "most complex main function prototype"
  did not compile, twice over. `args[1].to!{u32}()` gives a `u32` while the
  function returns `i32` (`incompatible types i32 and mut u32`), and `to`
  throws `CastFailure`, which the prototype never declared → `to!{i32}`, and
  `throws AssertError, CastFailure` with `conv::errors` added to the `use`.
  That also gives the chapter its one example of the multi-type `throws` list
  the §Exceptions text introduces.
- §Functions §Unsafe function: "Hence, the `bar` function is actually unsafe"
  — `bar` is the listing's *error* case, the one that calls an unsafe function
  outside an unsafe block. The paragraph is about `baz`, which wraps the call
  and is therefore unsafe without saying so, which is the whole point of the
  `importantbox` above it.
- §Modules §Describing a package: the declaration dump named
  `foo::qux::prvFunctionInQux` / `pubFunctionInQux` where the source listing
  three inches above declares `prvFuncInQux` / `pubFuncInQux`, and ordered
  private before public where the compiler prints public first. Replaced with
  the compiler's actual output.
- §Modules §Using a module: the `use` dump was stale by an entire core library
  — `core, core::array, core::range, core::exception, core::typeinfo,
  core::duplication, core::math` against today's `core::exception,
  core::exception::assertion, core::exception::io, core::exception::option,
  core::types` — and showed a `use` list for modules only, where the compiler
  now prints one per symbol. Replaced, with a note on the elision.
- §Modules §Using a module: `foo::bar:tryAccessToBaz`, one colon short.
- §Unit tests: `assert(true, "A test that succeeds.")` is a hard error
  (`useless runtime assertion`), so the section's own example of a *passing*
  test could not compile → both tests now assert on an `add(1, 2)` call.
- §Name aliases §values: the two line references into the listing were both off
  by one (lines 18 and 19 for calls that sit on 17 and 18); §types §Type
  mutability had the same slip (line 5 for the declaration on line 4).

Obsolete material, confirmed with the author:

- §Functions §Empty function was built entirely on `.yri` header files —
  a `bar/include/bar.yri` "automatically generated by the compiler", passed with
  `-I`. The compiler has no notion of the extension (nothing in `gcc/ymir`
  mentions `yri`); `-I` simply takes a source file. Rewritten around what is
  real: a bodiless prototype declares a function linked in later, `-I` takes the
  declarations and the object file the code. The source-hiding use case survives
  and is kept, with the constraint that actually shapes it — the prototype file
  must still be named after its module, hence a directory of its own.

Completeness. Chapter 5 is a light gray chapter, so the same judgement as
chapter 4 applies: uniform template, every rule with an entry.

- §External declaration was a **two-word stub** ("External variable"), while
  §Functions referenced `sec:external_decls` for the mechanism. Written from the
  compiler's behaviour, verified case by case: linkage (`extern (C)` keeps the
  written name, bare `extern` mangles from the declaring module's path, which is
  also why it cannot reach another package's symbol), `static` vs `lazy`, and
  the three errors that pin the rules down — `static` on a non-external global,
  `@thread` on an external one, and `mut` on a `lazy` that borrows nothing. Ends
  on a worked C interop example that was run, not imagined.
- §Unit tests was the thinnest section of the book (a listing, two sentences,
  and a command line) and said nothing about what running the tests looks like.
  Added the real `-funittest` output, the naming scheme it exposes
  (`main::__test::0`, by declaration order, since a test has no identifier), the
  `====` delimiters around a test's own stdout, and the non zero exit status.
- Section titles: "Global variable" → "Global variables", "Using name alias
  for types/values" → "name aliases", matching every other title in the chapter.

Language: `positionnally`, `predictible`, `recommanded` (twice), `is is`,
`alonside`, `retreived`, `atteignable` (French for "reachable"), `normaly`,
`paramters`, `arguee`, `fro`, "the the", "not a lvalue", "an hidden", "nor a new
copy", "option parameter" for *optional* parameter (twice), "for verbosity" where
brevity was meant, and a dozen subject/verb slips (`describe`, `produce`,
`exit`, `become`, `enforce`, "Exception might", "no exception are"). `figure~` /
`section~` → `Figure~` / `Section~` book-wide (13 sites across chapters 1, 3, 4
and 5; the majority spelling already won 15:6 and 51:7), dropping the article in
"in the Figure~\ref".

Listings (chapter 5 now 32/33, the exception being the open brace-less-body
item): eleven narrative fragments annotated `%% check: skip`, three `unused`
failures fixed by printing the value the listing is about, and the §Recursive
optional parameter listing converted to `coloredverbatimError` — the prose says
"the validation of the function `foo` fails", but it was styled as valid Ymir
and carried no error markers.

Tooling and style, needed by the above:

- `tools/check_listings.py` now terminates the synthesised unit with a newline
  (see the gotcha above). Worth 11 listings book-wide.
- `special_header.tex` gained a `cVerb` listing style, a C badge over the same
  presentation, for the `lib.c` of the interop example. It also keeps the
  listing out of the Ymir checker without a `skip` annotation, since the harness
  selects on style.
