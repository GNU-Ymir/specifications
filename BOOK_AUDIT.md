# Ymir book — audit, applied fixes, and roadmap

Audit date: 2026-08-08. Second pass the same day (§1.4 onward, plus the tooling
in §3.4) continued the work left mid-flight. Re-audited with `ymirc` on
2026-09-26 (§1.7, and §2 rewritten against it).

Reference compiler: `ymirc` (`~/.local/bin/ymirc`), which runs the in-development
`~/ymir/ymir-dev/target/bin/gyc` with its own standard library. The book documents
this compiler. **Not** `/usr/bin/gyc`, which is a different, stale tree. Until
2026-09-26 the reference was `~/ymir/gcc/gcc-install/bin/gyc`, which no longer
exists; §1.1 to §1.6 were measured with it.

Authoritative language reference:
`~/ymir/ymir-dev/repos/bootstrap/src/ymirc/lexing/keys.yr` (keyword/attribute
enums) and `~/ymir/ymir-dev/repos/bootstrap/test_resources/**/*.yr` (worked
examples of current syntax).

## Method

Every Ymir listing in `chapters/**/*.tex` is extracted and compiled with
`gyc -c`, and the programs of `examples/` are linked too. Listings mix top-level declarations with loose "inside
main" statements, so the harness splits them and synthesises a `main`.

The first pass used throwaway scripts. They have since been rebuilt as
checked-in tools — see §3.4 — so the numbers below are now reproducible:

```
make check          # both checkers
make check-refs     # cross-references only
make check-listings # compile every listing
make check GYC=/path/to/gyc   # override the reference compiler
```

### Current numbers

With `ymirc`, after Part I *Functions* (2026-09-27, §1.9):

```
222/228 plain listings compile; 96/96 error demos fail as intended; 355 skipped.
failures by cause:
     6  undefined-symbol
```

*Functions* added 25 listings, 20 of them read from `examples/`, 9 error demos
and 1 skipped fragment. The 6 failures are those of §2.3. The figures below are
from before it.

With `ymirc`, after the compiler error codes were added (2026-09-27):

```
197/203 plain listings compile; 87/87 error demos fail as intended; 354 skipped.
failures by cause:
     6  undefined-symbol
```

The 340 new skipped listings are those of `chapters/appendix/codes/`, generated
from the compiler's `docs/errors/`. Each is a `test_resources/` case that the
compiler's own suite already checks, and many are not standalone units. The
figures below are from before them.

With `ymirc`, after Part I *Control flow* and the Part II *Control flows*
rewrite (2026-09-26, §1.8):

```
197/203 plain listings compile; 87/87 error demos fail as intended; 14 skipped.
failures by cause:
     6  undefined-symbol
```

Every failure is accounted for:

| Class | Count | What it is | Where |
|---|---|---|---|
| `undefined-symbol` | 6 | narrative fragments, relying on code shown earlier in the prose | §2.3 |

Part I *Control flow* added 31 listings and 7 error demos, and the Part II
rewrite 6 listings and 3 error demos. The rewrite also made the 4
`undefined-symbol` fragments of *Control flows* self-contained, hence 6 failures
where there were 10. The figures below are from the re-audit, before either.

With `ymirc`, re-audited 2026-09-26:

```
156/166 plain listings compile; 77/77 error demos fail as intended; 14 skipped.
failures by cause:
    10  undefined-symbol
```

Before this re-audit the harness reported 98/162 with `ymirc`. The twelve
listings gained were all harness artefacts (§1.7): `ymirc` rejects the
`use std::io;` the harness prepends whenever the listing does not need it. One
listing moved from the error demos to the plain listings, where it belongs
(§1.7), hence 163 and 78. Then the book was brought in line with the
compiler on mutable lazy globals (§2.1 item 6): one error demo became a valid
listing, and one listing was added, hence 165 and 77. Last, every
book-vs-compiler conflict was fixed in the book (§2.1): the listings now read
their variables and assert at compile time what the compiler knows, and 43
failures went (53 to 10), for 156/166.

The last classified run with the old compiler (2026-08-09):

```
89/165 plain listings compile; 71/71 error demos fail as intended; 3 skipped.
failures by cause:
    42  unused
    23  undefined-symbol
     5  const-assert
     3  stale-stdlib
     3  other
```

`tools/check_refs.py`:

```
605 labels, 514 distinct references; 0 broken, 17 pending (unwritten material), 0 duplicated.
```

Measured after *Functions* (§1.9). `chap:layout` joined the pending list, cited
for the call stack, and the checker now reads the labels of `\lstinputlisting`
too. The counts below are from before the error-code appendix.

```
202 labels, 141 distinct references; 0 broken, 16 pending (unwritten material), 0 duplicated.
```

`sec:pattern_matching` left the pending list as `sec:flow:pattern_matching`
(§1.8). The paragraphs below describe earlier counts.

`sec:lazy:global_variable` was added with the lazy globals fix (§2.1 item 6).
The §2.1 fixes removed the do-while listing and figure, with the figure's only
reference, and added `sec:flow:loop_at_least_once`, its listing, and
`sec:global:assertions`.
After the Part II split (2026-09-26): `chap:Error_handling` left the pending list
as the new `chap:error`, and `sec:flow:dispose_block` and `sec:flow:thread_sync`
went with their sections. The figures below are from before it.

Measured 2026-09-26, after the `fix/tipos` commits were cherry-picked. The
label count fell with the topic-label sweep (`BOOK_STYLE.md` § Labels), and
`sec:external_decls` left the pending list: chapter 5 now defines
`sec:global:external_decls`.

The totals moved with chapter 1's editorial pass (`BOOK_REVIEW.md`): a duplicate
listing was removed, four were added, and the labels and references of the new
§1.1 came with them. The failure breakdown is unchanged.

On 2026-08-08, the 19 pending labels of the time matched the 19 undefined
references in a real three-pass `make refs` build exactly, so the static
checker is trustworthy — and it is far faster than a build.

**The listing totals are not comparable to the first pass's `101/233` and
`113/233`.** The denominator changed for good reasons: the harness now
recognises every error-demo marker the book actually uses (so 70 listings moved
out of "failing" into "correctly failing"), and it counts only listings in Ymir
styles. What is comparable is the failure breakdown, which is now classified
rather than a flat count of 71 "unexplained".

Progress on the LaTeX side:

| | first pass | now |
|---|---|---|
| LaTeX missing glyphs | ~600 → 4 | **0** *(measured by `make refs`, 2026-09-26)* |
| duplicate labels | 1 → 0 | 0 |
| undefined references | 46 → 37 | **0** (+19 for unwritten material) |

---

## 1. Fixes already applied

### 1.1 Language drift in code listings

These were verified one by one against the compiler before changing.

| What | Was | Now | Sites |
|---|---|---|---|
| Class instantiation | `A::new (x)` | `copy A (x)` | 13 |
| Float literals | `8.f`, `12.f` | `8.0f`, `12.0f` | 16 |
| Record declaration | `struct Range {T}` | `record Range {T}` | 1 |
| Union declaration | `@union struct` | `@overlaid record` | 1 |
| Range field | `.contain` | `.contains` | 6 |
| Option field | `let set : bool` | `let hasValue : bool` | 1 |
| `throws` operand | `&EmptyErrOption` | `EmptyErrOption` | 1 |

Notes:

- `struct` is **no longer a keyword at all**. `record` replaced it.
- Unions are now expressed as an `@overlaid record`; there is no `@union`
  attribute (`Attributes` in `keys.yr` is `abstract, final, field, thread,
  overlaid, packed, unsafe, inline`).
- `throws` takes *class types*, not object-instance types, so the `&` is
  rejected. The book was already correct everywhere else (`throws AssertError`).
- Option field naming now matches the surrounding prose, which already said
  `hasValue`.

### 1.2 Genuine typos

- `spec/global/section5.tex` — `println ("In bar")` was missing its `;`.
- `spec/compound/section7.tex` — `let v : i32? = foo ()` was missing its `;`.
- `spec/flow/section3.tex` — `else if count = 10` used assignment, not `==`.
- `course/types/section6.tex` — the comment `// to import \to\` rendered literally
  as `\to\` in the PDF (the listing's `escapechar` is `@`, so the backslashes
  were never LaTeX). Now `// to import 'to'`.

### 1.3 LaTeX build

- **Missing glyphs (~600 → 4).** `\usepackage{times}` selected the legacy Type1
  `ptm` family, which has no glyph for `’` (U+2019), `—` (U+2014) or `‑`
  (U+2011) — all common in the prose. Replaced with a fontspec-selected
  Unicode-complete Times clone (`\setmainfont{TeX Gyre Termes}`,
  `\setsansfont{TeX Gyre Heros}`).
- **`~` rendered blank in 62 places.** `\mtilde` and the `coloredverbatim`
  listing style mapped `~` to `\texttildelow`, i.e. U+02F7, which the mono font
  lacks. Both now use `\textasciitilde`. This affected every shell prompt
  (`alice@dev:~$`) and every use of Ymir's `~` concatenation operator.
- **Duplicate label.** A stray `\label{tab:integer_ranges}` in
  `course/types/section5.tex` (copy-paste into the float-representation table, which
  already carries `tab:(chap2):float_mem_repr_ex` in its caption).
- **π dropped in prose.** `\tokennolst` sets its argument in `\ttfamily` with no
  `literate` mapping; changed that call site to `\ensuremath{\pi}`.
- **Missing chapter labels.** Added `chap:compound` (ch4), `chap:variables` and
  `chap:memory_management` (ch6), `chap:control_flows` (ch7). These were
  referenced but only `chap:chapN` labels existed.

### 1.4 Second pass — cross-references (was §2.1)

All eight repairs listed as "mid-flight when interrupted" are applied:

| File | Change |
|---|---|
| `spec/compr/section1.tex` | Added `label=lst:(chap7):compr_two_loops` to the "Using two loops" listing |
| `spec/compr/section1.tex` | Caption of `list_compr_tuple_create_yil` now cross-refs `list_compr_tuple_create`, not `..._iter` |
| `spec/flow/section4.tex` | `lst:simple_do_while_loop` → `lst:(chap7):simple_do_while_loop` |
| `spec/flow/section4.tex` | `lst:while_let_rewritten` → `lst:(chap7):while_let_rewritten` |
| `spec/flow/section5.tex` | Added `\label{sec:for_loops}` beside `\label{sec:for_loop}` |
| `spec/memory/section4.tex` | Ref `lst:result_copy_v_ref_array` → `lst:(chap6):...` |
| `spec/memory/figures/ref_param_array.tex` | Def `fig:example_call_ref_array` → `fig:(chap6):...` |
| `spec/compound/section5.tex` | Ref `fig:data_repr_array` → `fig:(chap4):...` |

Also normalised the singular/plural split flagged in the old §3.1:
`chap:custom_type` → `chap:custom_types` (2 sites, `spec/global.tex` and
`spec/compound/section7.tex`). **Plural is now the one true spelling.**

Result: **zero** broken references. The only unresolved ones are the 19 that
point at unwritten chapters and sections, now listed explicitly in
`tools/pending_labels.txt` so the checker can distinguish "not written yet"
from "typo".

### 1.5 Second pass — listing and markup fixes

- **`style=coloredVerbatim` was never defined.** Five listings
  (`course/types/section2.tex` ×2, `course/types/section3.tex`, `course/types/section5.tex`
  ×2) asked for a style with a capital V; only `coloredverbatim` exists in
  `special_header.tex`. Corrected. This was silently costing those five
  listings their syntax highlighting.
- **`@union` in the highlighter.** `special_header.tex` still listed `@union`
  as a keyword after §1.1 removed it from the language. Now `@overlaid`.
- **`spec/error/section1.tex`** — the scope-guard example declared
  `fn foo ()-> i32 throws AssertError` with a body of only `// ...`, so it
  returned void *and* never threw. Body is now
  `throw copy AssertError ("foo failed");`, which satisfies both. Kept to one
  line deliberately: the surrounding prose refers to lines 10, 12 and 14 of that
  listing, so the line count must not shift.
- **`spec/compound/section5.tex`** — `[foo () for i in 0 .. 4]` → `for _ in`. See the
  compiler bug in §2.2 item 5: the unused `i` poisoned the whole expression's
  type to `error`, so the following `a [0]` failed to index. `_` is correct
  current style regardless of whether that bug is fixed.
- **`spec/compound/section7.tex`** — the polymorphic-option example bound
  `Ok (a : &A)` inside `match a`, shadowing the `a` it was matching on. Renamed
  the binding to `x`.
- **`spec/compound/section7.tex`** — one error demo was marked `// no, inner value is
  not mutable`, a spelling nothing else in the book uses. Now `// not allowed,
  ...`, so the harness recognises it.

### 1.6 Second pass — the remaining π glyphs, root-caused

The first pass guessed the listings `literate` mapping for π "is not firing in
every context". The real cause is worse and worth writing down:

**`listings`' `literate` does not fire for *any* non-ASCII character in this
setup.** It was verified with a minimal document (`listings` + `fontspec` only,
no book preamble): with replacements set to plain ASCII text, neither `π` nor
`Ω` is substituted. `Ω` merely *looked* like it worked because Latin Modern Mono
happens to contain Ω, so no "missing character" was ever logged. ASCII literate
entries — including the `~` fix in §1.3 — do work.

Ruled out along the way: entry ordering, `extendedchars=true`, `$\pi$` vs
`\ensuremath{\pi}`, `siunitx`, and a codepoint mismatch (both source and key are
byte-identical `cf 80`).

All three logged π misses came from the single listing at
`spec/scalars/section3.tex:80`; the `\token{'π' + 501u32}` in the prose at l. 232
already rendered fine, because `\lstinline` tokenises its argument in the
surrounding text font, which has π.

The fix uses the convention the book already established for exactly this
problem in `course/types/section6.tex` — an `escapechar` escape:

```latex
\begin{lstlisting}[style=coloredverbatim, escapechar=@]
let d = '@\ensuremath{\pi}@'c32;
```

Verified to render with zero missing characters in isolation, and confirmed by
a full `make refs` rebuild on 2026-09-26. That rebuild also caught a missing
`;` (U+003B) in `nullfont` that was not a font problem at all: a stray `;`
after the `\gearicon` call in `course/basics/figures/compilation_chain.tex`, typeset
as text inside the `tikzpicture`. Removing it brought the count to 0.

`tools/check_listings.py` understands this convention: an escape between single
quotes is replaced with a placeholder character rather than deleted, so
`'@\ensuremath{\pi}@'c32` still extracts as a valid character literal.

**This makes the mono-font question in the old §2.3 more pressing, not less.**
Since `literate` cannot rescue non-ASCII glyphs at all, every such character in
a listing must be hand-escaped forever, or the mono font must be changed. A
global `\setmonofont{DejaVu Sans Mono}` would cover π, Ω *and* the box-drawing
characters in `bashVerb` (currently hand-mapped to `\textSF*`) — but it changes
the look of every listing in the book. That is an aesthetic call for the author.

### 1.7 Re-audit with `ymirc` (2026-09-26)

Harness (`tools/check_listings.py`):

- **Its own `use std::io;` is dropped when unused.** The harness prepends it
  so that listings can call `println` without importing it; `ymirc` rejects a
  `use` that resolves nothing (E3038), which failed 12 listings that print
  nothing. When the compiler reports that line, the unit is rebuilt without it.
  A `use` the listing writes itself is still checked, as class `unused-use`.
- **An escape inside a string literal keeps its text.**
  `"@\korean{\color{...} 안녕하세요 세계}@"` has nested braces, so the escape
  was deleted and the string became `""`, which made
  `assert(utf8_str.len == 22)` fail at compile time (`course/types/section6.tex`
  l. 168). The book's 22 bytes and 8 characters are right.
- **Error demos are recognised by their style only.** See §2.3.

Book:

- `spec/compound/section7.tex` l. 28: a valid listing badged *Invalid Ymir*
  since the 2026-08-09 conversion (commit `cfd1c43`), because its comment
  `// create an error option value` matched the old `// error` marker. Back to
  `style=coloredverbatim`. It compiles once its variables are used.
- `spec/memory/section2.tex` l. 96: `mod foo;` opened a listing meant as the
  module `foo`, which is `in foo;` everywhere else in the book. `mod foo;`
  declares a *child* module, and the compiler rejected the file as importing
  itself, before reaching the shadowing error the listing demonstrates. With
  `in foo;` it gives that error (E4199).
- `spec/lazy/section1.tex` l. 165: the error demo's `fn main() {}` closed
  `main` before its body. Now `fn main() {`; both highlighted lines still fail
  as shown (E4154).
- Mutable lazy globals: §2.1 item 6.

### 1.8 Control flow, both parts (2026-09-26, BOOK-7)

Part I gained *Control flow* (`chapters/course/control`, `chap:control`), and
Part II *Control flows* was rewritten as a specification. Every Part I listing
was compiled **and run** with `ymirc`; the terminal transcripts in the chapter
are its output. Every claim of the Part II rewrite, and every diagnostic code in
its tables, was checked by a direct test.

Harness (`tools/check_listings.py`):

- **A highlight with escaped braces lost its text.** `@\hb{if c \{ 1 \}}@`
  did not match the escape pattern, which allowed no brace in the argument, so
  the whole escape was deleted, and the listing lost the code it highlights. A
  correction such as `@\hcb{else \{ ... \}}@` then made a valid solution fail
  (`course/control/section9.tex`), and an error demo could fail for the wrong
  reason. The argument may now hold `\{`, `\}`, `\%`, `\_`, `\&`, `\#`, `\$`,
  which are unescaped. No other listing changed outcome.

Book:

- New listing style `grammarVerb`, badged *Grammar*, for grammar productions
  (`BOOK_STYLE.md` § Listings). The two productions of
  `spec/memory/section2.tex` moved to it from `bashVerb`.
- `spec/flow/section6.tex` (was `section5.tex`): the prose cited the loops of
  `lst:flow:ref_value_iter_ex` as lines 2, 5, 10 and 13; they are on lines 2,
  6, 11 and 15.
- The 4 `undefined-symbol` fragments of *Control flows* (`cond`, `foo`, `x`)
  now declare what they use.
- `\token` dropped the space after a closing string quote: `"no" \}` printed
  as `"no"}`, and `"zero" - 1` in `spec/flow/section7.tex` as `"zero"- 1`. The
  argument reaches `\lstinline` already tokenized; `keepspaces=true` in the
  macro fixes every occurrence.

Compiler behaviour found while writing, for the compiler's authors. The book
documents each as it is, and none blocks a listing.

- **`[x]` in a pattern is `x`.** Square brackets around a single pattern with
  no comma group it, as parentheses do, so `[x]` binds the whole value and no
  pattern matches an array of exactly one element. `(x,)` exists for tuples;
  arrays have no equivalent. Probably unintended.
- **A single-expression match arm reads into the next arm.** In
  `match t { (0, _) => 0 (x, y) => x + y }` the body `0` and the next pattern
  parse as the call `0(x, y)`; a pattern starting with `-` continues the body as
  a subtraction. The grammar has no separator between arms, so the fix is a
  block or a `;`. Documented in `sec:flow:pattern_matching`.
- **An irrefutable `while let` pattern** reports E4100, "infinite loop with
  always true test", where `if let` reports E4268. Consistent in effect, but the
  message names a test the source does not have.
- **Code after a `loop` with no `break`** is not reported as unreachable, where
  code after `break` or `return` is (E4260).
- **`std::io::read!i32`** returns `0` when the input is not a number, and on end
  of input. A loop that reads until a condition holds then spins forever when
  stdin closes. Part I says the first; the second is only a hazard for anyone
  scripting the chapter's programs.

### 1.9 Part I *Functions* (2026-09-27, BOOK-17)

Part I gained *Functions* (`chapters/course/functions`, `chap:functions`), and
the book gained `examples/`: the complete programs of the course, read by the
book with `\lstinputlisting` and published as a zip archive with each release.
Every listing was compiled **and run** with `ymirc`, and every error demo was
checked to fail on the error its prose names.

Harness:

- `tools/check_listings.py` checks a `\lstinputlisting` with the file it reads,
  reports a missing one as `missing-file`, and compiles each example file that
  no listing shows.
- It honours any `escapechar`, not only `@`. A listing that shows a parameter
  declared `@name` escapes with `|`, since `@name: i32, @` reads as an escape
  (`BOOK_STYLE.md` § Listings). The Part II listings escaped with `$` are now
  stripped as well; no outcome changed.
- `tools/check_refs.py` reads the `label=` of a `\lstinputlisting`.
- `tools/check_listings.py` compiles with `gyc -c` instead of `-fsyntax-only`,
  so the errors raised after validation are caught too, and links each program
  of `examples/`. No outcome changed.

Compiler behaviour found while writing, for the compiler's authors. The book
documents each as it is.

- **A parameter with a default value is passed by name only**, and one declared
  `@name` must be named (`function/test22.yr`, `test23.yr`). Part I says both;
  Part II `sec:global:function_parameters` does not mention `@name`, nor that a
  positional argument never fills a defaulted parameter.
- **A suffixed literal adapts to any parameter.** `describe(12i64)` calls
  `describe(x: i32)`, and `show(12u16)` is ambiguous between `show(x: i64)` and
  `show(x: u64)`, while a variable must have the parameter's type exactly.
  Probably unintended; the book shows only unsuffixed literals.
- **Overloads that differ only by their result type** report E4023, colliding
  definitions, and each call E4280, multiple candidates.
- **Unbounded recursion** is not diagnosed. It ends in a segmentation fault
  (about 130,000 frames for a `println` and a call), and output buffered for a
  pipe is lost; on a terminal the lines printed before the crash are shown.

---

## 2. Conflicts, drift and non-issues

### 2.1 Book vs. compiler — all resolved (2026-09-26)

**The compiler is the source of truth** (author's decision, 2026-09-26): where
the book and `ymirc` disagree, the book is wrong. Every conflict found by the
audits was a case of the book documenting behaviour `ymirc` does not have, each
confirmed by direct test. All are now fixed in the book.

1. **`do`/`while` loops do not exist** (`do` is not a keyword). The do-while
   subsection of `spec/flow/section4.tex` and its figure are gone; a
   subsection *Loops entered at least once* shows the `loop` + `break` form
   instead, and §While loop value no longer mentions do-while. The Part I
   keyword list (`course/types/section1.tex`) is now the compiler's
   `ForbiddenKeys`: `do` removed; `_`, `async`, `await`, `continue`, `self`,
   `super`, `template`, `yield` added.
2. **Brace-less function bodies are rejected.** `spec/global/section2.tex`
   §Body now says a body is a block, braces mandatory.
3. **List comprehension over a tuple** — implemented by the compiler; nothing
   to change.
4. **`assert` on a compile-time constant is an error** (E4269, "useless runtime
   assertion"). The compiler's own advice is `cte assert` for a compile-time
   check. `spec/global/section3.tex` gains §Assertions
   (`sec:global:assertions`), which specifies both, and the 5 listings now use
   `cte assert`, or `println` in Part I, which has not met `cte`. The YIL after
   `spec/compound/section3.tex` l. 218 lost its runtime `abort` lines
   accordingly.
5. **An unused variable is a fatal error** (E4038), and so is a `use` that
   resolves nothing (E3038). The spec already said so
   (`sec:memory:unused_variables`: `_a_`, `_`, or a statement using the
   variable). Part I now says it too, in `course/types/section2.tex`. The 33
   listings read their variables, mostly by printing them; the two `use`
   listings of `spec/global/section1.tex` now use what they import. Where a
   binding was only there to show a pattern, it became `_`
   (`spec/compound/section7.tex`, polymorphic option). One listing prints
   `typeof(x)::typeid` to show the type of a loop value
   (`spec/flow/section3.tex`).
6. **Mutable lazy globals are allowed.** Fixed in the book earlier the same day:
   `spec/lazy/section1.tex`, `spec/global/section5.tex`, `section6.tex`,
   `spec/memory/section2.tex`.
7. **Mutable iterators are allowed in comprehensions.** The error demo of
   `spec/compr/section1.tex` §Mutable and reference value iterators is now a
   valid listing of a mutable iterator, and the rule follows `for` loops.

Still a compiler bug, reported here for the compiler's authors: an unused
iterator poisons the type of the enclosing expression. In
`let a = copy [foo () for i in 0 .. 4]; a [0]` the unused `i` makes `a`'s type
`error`, and the first error reported is "the index operator is not defined for
type error and {i32}", on the wrong line.

### 2.2 Standard library drift — resolved (2026-09-26)

`ymirc` ships its own standard library, so the stale `/usr/include/ymir/1.2/`
problem of the first audit is gone; the `stale-stdlib` class is still in the
harness but matches nothing.

The one listing using an API that no longer exists, the exit guard closing a
`File` (`spec/error/section1.tex`), now imports `std::fs::{file, path, errors}`,
creates the file from a `Path`, and calls `write` and `close` with `:.`, which
the prose introduces in one sentence and defers to Custom types. Run with
`ymirc`: the write after `close` throws `FsError (FILE_CLOSED)`, as the comment
says.

### 2.3 Known non-issues

For future audits, these all *look* like failures but are not:

- **6 listings** fail with `undefined symbol` because they are narrative
  fragments referring to symbols defined earlier in the prose (`foo`, `bar`,
  `cond`). Annotate these with `%% check: skip` as you touch them; that is the
  only way the harness can tell them from real breakage. They are the only
  failures left.
- **An error demo can fail for the wrong reason.** The harness only checks
  that it fails. Each error demo was checked by hand on 2026-09-26: all but
  the following fail on the error they show.
  - `course/types/section6.tex` l. 33: the emoji inside `'...'` is an escape,
    replaced by the placeholder `?`, so the harness sees a valid literal and
    only an unused variable. The real character gives the intended E4115
    "malformed literal, number of c8 is 4".
  - `spec/error/section1.tex` l. 76 fails on the fragment symbol `foo`, and
    once `foo` is declared, on the unused `a`: both stop the compiler before the
    intended error. With `a` used inside the guarded scope, it gives the error
    it shows, `a` undefined in the exit guard.
  - `spec/compr/section1.tex` l. 62 failed only on an unused variable; the
    error it showed no longer exists, and it is now a valid listing (§2.1
    item 7).
- Module examples (`in foo;`) require the file to actually be named `foo.yr`,
  and `in` must precede everything — including any `use` a harness prepends.
  The harness handles this by naming its temp file after the declared module;
  a module in a *subdirectory* (`spec/global/section1.tex` l. 48) still cannot be
  checked and is marked `%% check: skip`.
- **Error-demo markers are standardised** (2026-08-09). A listing whose code
  must not compile carries `style=coloredverbatimError`, which is also what puts
  the *Invalid Ymir* badge on it in the PDF; all 71 were converted. The old
  spellings (`// error`, `// not allowed`, `// forbidden`, the captions
  `Invalid` and `Ymir program with errors`) remain useful on the *line* that is
  at fault. See `BOOK_REVIEW.md`. Since 2026-09-26 the harness no longer reads
  them: the conversion had badged one valid listing whose comment mentions an
  "error option value" (`spec/compound/section7.tex` l. 28), and matching the
  old spellings kept counting it as an error demo.
- The keyword list in `course/types/section1.tex` matches the compiler's
  `ForbiddenKeys` since 2026-09-26 (§2.1 item 1).

### 2.4 YIL listings are not checked

The YIL listings (`lyilVerb`, `myilVerb`) are written in an older form of YIL
than `ymirc` emits (`frame : main::main` where `ymirc` writes mangled names,
e.g. `frame: _Y6test114mainFZv` in the compiler's `global/test11.yil`), and
nothing compares them with the compiler's output. They illustrate the lowering
rather than reproduce it, but a reader who runs `-fdump-ymir` will not find the
same text. Unchanged by this audit.

---

## 3. Roadmap — what the book is missing

### 3.1 Chapters the book already promises but does not contain

These are live `\ref`s that resolve to nothing, so the book itself names them.
The list is maintained as `tools/pending_labels.txt`; delete a line there when
the material lands and `check_refs.py` starts enforcing it.

| Label | Refs | Subject |
|---|---|---|
| `chap:conditional_compilation` | 3 | `__version`, `cte`, `__pragma` |
| `chap:custom_types` | 4 | user-defined types (spelling now normalised, see §1.4) |
| `chap:structures` | 2 | `record` / `entity` |
| `chap:std_and_core_runtime` | 2 | the standard library and runtime |
| `chap:templates` | 3 | `{T}` templates, `of` / `over` / `impl` specialisation |
| `chap:macros` | 1 | `macro`, the macro rule keys |
| `chap:documentation` | 1 | doc comments, `-fdoc` |
| `chap:layout` | 1 | memory layout and execution: the call stack, cited by Part I *Functions* |
| `chap:type_and_values` | 1 | "all expressions and statements" — ambiguous, may map to an existing chapter |

`chap:Error_handling` (4 refs) left this table on 2026-09-26: the Part II split
created the chapter as `chap:error`, from the scope-guard and exception sections
of *Control flows*.

Unresolved section refs pointing at unwritten material:
`sec:impl_lazy_closure` (3), `sec:pragmas`,
`sec:string_lit`, `sec:function_overloading`, `sec:mutable_parameter`,
`sec:mut_ret_param`, `sec:class_override_for_loop`,
`sec:class_override_lst_compr`.

### 3.2 Language features implemented but undocumented

Found by diffing `keys.yr` against the book's keyword list:

- **`async` / `await` / `yield`** — present in the compiler
  (`syntax/expression/control/await_.yr`, `syntax/expression/instruction/yield_.yr`).
  Entirely absent from the book. Needs a concurrency chapter alongside the
  existing `spawn` / `atomic` / `future` keywords, which are also only listed,
  never taught.
- **`:.`** — the alias operator: calls a method that mutates its receiver
  (`file:.write (...)`). Used once (`spec/error/section1.tex`, §2.2) with a
  one-sentence explanation that defers to Custom types, where it belongs.
- **`@name` parameters** — a parameter that can only be passed by name.
  Taught by Part I *Functions* (`sec:functions:named_arguments`) since
  2026-09-27; Part II does not mention it yet.
- **`typeid`** — `T::typeid` names a type as a string. Used once, to show the
  type of a loop value (`spec/flow/section3.tex`); see Compile-time reflection
  below.
- ~~**`continue`**~~ — documented since 2026-09-26: Part I *Control flow*
  § Repeating, Part II *Control flows* § Infinite loop (`sec:flow:continue`).
- **`self` / `super`** — reserved, and needed for the classes/inheritance
  material that chapter 7 already uses (`class B over A`).
- **`template`** — reserved; relates to `chap:templates`.
- **`_`** — reserved (wildcard); used in listings but never introduced. This is
  now more urgent: §1.5 introduced another use of it, and if §2.1 item 5 is
  resolved in the compiler's favour, `_` becomes the standard answer throughout
  the book and *must* be taught early.
- **Attributes** — `abstract`, `final`, `field`, `thread`, `overlaid`, `packed`,
  `inline`. Only `@field` and (now) `@overlaid` appear in examples; none are
  documented.
- **Compile-time reflection** — `field_infos`, `typeinfo`, `typeid`, `size`,
  and the `NativeTypeAttribute` set (`epsilon`, `mant_dig`, `max_10_exp`, …).
  Partially used in property tables, never explained.

### 3.3 Chapter status

Chapter status is tracked in `progress.org`, rewritten on 2026-09-26 to follow
the two-part structure of `BOOK_PLAN.md`. The items that concern this audit:

| Part | Chapter | Source | Open item |
|---|---|---|---|
| I | Fundamental types, constants and variables | `course/types` | keyword list still has `do` (§2.3) |
| II | Control flows | `spec/flow` | rewritten as a specification (§1.8); editorial pass still owed |
| II | Global constructions | `spec/global` | §function-body needs the §2.1-item-2 decision |

Possible content duplication, noticed but not investigated: `course/types/section6`
("Character and String types") and `spec/scalars/section3` both cover character
types, and both define a table captioned "Escape characters"
(`tab:types:escape_chars` and `tab:scalars:escape_chars`). Worth a look.

### 3.4 Tooling

**Built** (this pass):

- **`tools/check_listings.py`** — compiles every Ymir listing and classifies
  each failure (`unused`, `unused-use`, `undefined-symbol`, `const-assert`,
  `stale-stdlib`, `other`), so a run says *why* rather than just *how many*. Supports
  `--only SUBSTR`, `--verbose`, and `--dump FILE:LINE` to print the
  reconstructed translation unit for one listing — the fastest way to tell a
  harness artifact from a real defect. Understands two source annotations,
  placed on the line above a listing:

  ```latex
  %% check: skip  -- narrative fragment / not compilable standalone
  %% check: error -- must fail to compile
  ```

- **`tools/check_refs.py`** — undefined references, duplicate labels, and
  (with `--unused`) labels nothing points at. Skips LaTeX comments, so a
  commented-out `\label` no longer reads as a duplicate. Reads
  `tools/pending_labels.txt` to separate "not written yet" from "typo".

- **`make check`** wires both in, ahead of the `main`/`refs` build targets.

**Still worth doing**, in rough priority order:

1. **Run `make check` in CI.** Both tools exit non-zero on failure and are
   already wired up. The listing checker needs the reference compiler on the
   box; `make check GYC=...` overrides its path.
2. ~~**Standardise one error-demo marker.**~~ **Done** (2026-08-09), by
   `style=coloredverbatimError` rather than by a comment: it marks the listing
   for the harness *and* badges it as invalid in the PDF, so the two cannot drift
   apart. 71 listings converted; see §2.3.
3. **Annotate the 10 narrative fragments** with `%% check: skip`. Once done,
   every remaining listing failure is real, and the checker can be made
   blocking.
4. **Fail the build on missing glyphs.** The `~` regression was invisible in
   the PDF (blank space) and sat in 62 places; the π one survived a full audit
   pass. `grep -c "Missing character" .build/main.log` is the whole check.
5. **Enforce the `(chapN):` label prefix convention.** §1.4 normalised the
   stragglers; a check in `check_refs.py` would stop it drifting again.
