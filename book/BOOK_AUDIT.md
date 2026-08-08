# Ymir book — audit, applied fixes, and roadmap

Audit date: 2026-08-08. Second pass the same day (§1.4 onward, plus the tooling
in §3.4) continued the work left mid-flight.

Reference compiler: `/home/emile/ymir/gcc/gcc-install/bin/gyc` (built 2026-08-08
from `~/ymir/gcc/gcc-src`). **Not** `/usr/bin/gyc`, which is a different, stale
tree.

Authoritative language reference used throughout:
`~/ymir/gcc/gcc-src/gcc/ymir/bootstrap/src/ymirc/lexing/keys.yr` (keyword/attribute
enums) and `~/ymir/gcc/gcc-src/gcc/ymir/bootstrap/test_resources/**/*.yr` (worked
examples of current syntax).

## Method

Every Ymir listing in `chapters/**/*.tex` is extracted and compiled with
`gyc -fsyntax-only`. Listings mix top-level declarations with loose "inside
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

`tools/check_listings.py` (2026-08-09):

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
163 labels, 113 distinct references; 0 broken, 19 pending (unwritten material), 0 duplicated.
```

The totals moved with chapter 1's editorial pass (`BOOK_REVIEW.md`): a duplicate
listing was removed, four were added, and the labels and references of the new
§1.1 came with them. The failure breakdown is unchanged.

Those 19 pending labels match the 19 undefined references in a real three-pass
`make refs` build exactly, so the static checker is trustworthy — and it is far
faster than a build.

**The listing totals are not comparable to the first pass's `101/233` and
`113/233`.** The denominator changed for good reasons: the harness now
recognises every error-demo marker the book actually uses (so 70 listings moved
out of "failing" into "correctly failing"), and it counts only listings in Ymir
styles. What is comparable is the failure breakdown, which is now classified
rather than a flat count of 71 "unexplained".

Progress on the LaTeX side:

| | first pass | now |
|---|---|---|
| LaTeX missing glyphs | ~600 → 4 | **0**, verified on a full `make refs` (2026-08-09) |
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

- `chapter5/section5.tex` — `println ("In bar")` was missing its `;`.
- `chapter4/section7.tex` — `let v : i32? = foo ()` was missing its `;`.
- `chapter7/section3.tex` — `else if count = 10` used assignment, not `==`.
- `chapter2/section6.tex` — the comment `// to import \to\` rendered literally
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
  `chapter2/section5.tex` (copy-paste into the float-representation table, which
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
| `chapter7/section6.tex` | Added `label=lst:(chap7):compr_two_loops` to the "Using two loops" listing |
| `chapter7/section6.tex` | Caption of `list_compr_tuple_create_yil` now cross-refs `list_compr_tuple_create`, not `..._iter` |
| `chapter7/section4.tex` | `lst:simple_do_while_loop` → `lst:(chap7):simple_do_while_loop` |
| `chapter7/section4.tex` | `lst:while_let_rewritten` → `lst:(chap7):while_let_rewritten` |
| `chapter7/section5.tex` | Added `\label{sec:for_loops}` beside `\label{sec:for_loop}` |
| `chapter6/section4.tex` | Ref `lst:result_copy_v_ref_array` → `lst:(chap6):...` |
| `chapter6/figures/ref_param_array.tex` | Def `fig:example_call_ref_array` → `fig:(chap6):...` |
| `chapter4/section5.tex` | Ref `fig:data_repr_array` → `fig:(chap4):...` |

Also normalised the singular/plural split flagged in the old §3.1:
`chap:custom_type` → `chap:custom_types` (2 sites, `chapter5.tex` and
`chapter4/section7.tex`). **Plural is now the one true spelling.**

Result: **zero** broken references. The only unresolved ones are the 19 that
point at unwritten chapters and sections, now listed explicitly in
`tools/pending_labels.txt` so the checker can distinguish "not written yet"
from "typo".

### 1.5 Second pass — listing and markup fixes

- **`style=coloredVerbatim` was never defined.** Five listings
  (`chapter2/section2.tex` ×2, `chapter2/section3.tex`, `chapter2/section5.tex`
  ×2) asked for a style with a capital V; only `coloredverbatim` exists in
  `special_header.tex`. Corrected. This was silently costing those five
  listings their syntax highlighting.
- **`@union` in the highlighter.** `special_header.tex` still listed `@union`
  as a keyword after §1.1 removed it from the language. Now `@overlaid`.
- **`chapter7/section7.tex`** — the scope-guard example declared
  `fn foo ()-> i32 throws AssertError` with a body of only `// ...`, so it
  returned void *and* never threw. Body is now
  `throw copy AssertError ("foo failed");`, which satisfies both. Kept to one
  line deliberately: the surrounding prose refers to lines 10, 12 and 14 of that
  listing, so the line count must not shift.
- **`chapter4/section5.tex`** — `[foo () for i in 0 .. 4]` → `for _ in`. See the
  compiler bug in §2.2 item 5: the unused `i` poisoned the whole expression's
  type to `error`, so the following `a [0]` failed to index. `_` is correct
  current style regardless of whether that bug is fixed.
- **`chapter4/section7.tex`** — the polymorphic-option example bound
  `Ok (a : &A)` inside `match a`, shadowing the `a` it was matching on. Renamed
  the binding to `x`.
- **`chapter4/section7.tex`** — one error demo was marked `// no, inner value is
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
`chapter3/section3.tex:80`; the `\token{'π' + 501u32}` in the prose at l. 232
already rendered fine, because `\lstinline` tokenises its argument in the
surrounding text font, which has π.

The fix uses the convention the book already established for exactly this
problem in `chapter2/section6.tex` — an `escapechar` escape:

```latex
\begin{lstlisting}[style=coloredverbatim, escapechar=@]
let d = '@\ensuremath{\pi}@'c32;
```

Verified to render with zero missing characters in isolation, and since
confirmed on a full `make refs` build (2026-08-09): `grep -c "Missing character"
.build/main.log` reports **0**.

`tools/check_listings.py` understands this convention: an escape between single
quotes is replaced with a placeholder character rather than deleted, so
`'@\ensuremath{\pi}@'c32` still extracts as a valid character literal.

**This makes the mono-font question in the old §2.3 more pressing, not less.**
Since `literate` cannot rescue non-ASCII glyphs at all, every such character in
a listing must be hand-escaped forever, or the mono font must be changed. A
global `\setmonofont{DejaVu Sans Mono}` would cover π, Ω *and* the box-drawing
characters in `bashVerb` (currently hand-mapped to `\textSF*`) — but it changes
the look of every listing in the book. That is an aesthetic call for the author.

---

## 2. Fixes still to make

### 2.1 Decisions needed — book vs. compiler

Each of these is a case where the book documents behaviour the current compiler
does not implement. **None were changed**, because the right fix may be to the
compiler rather than the book. Each is confirmed by direct test.

Items 1–3 are precisely the three listings still in the harness's `other`
bucket; everything else in that bucket has been explained or fixed.

1. **`do`/`while` loops do not exist.** `do` is not a keyword in `keys.yr` at
   all, and `do { ... } while c;` is a parse error. `chapter7/section4.tex`
   §`sec:do_while_loop` documents it in full, with a listing
   (l. 36) and a figure (`chapter7/figures/simple_do_while_loop.tex`).
   *Either* restore `do` in the compiler *or* delete the section and its figure.

2. **Brace-less function bodies are rejected.** `chapter5/section2.tex`
   §`sec:function_body` (l. 299) teaches
   ```
   fn foo (a : i32)-> i32
     a + 1
   ```
   The parser now demands `{` or `;` after the prototype. Bodiless prototypes
   (`fn foo ();`) *are* still valid. Decide whether the expression-body form is
   coming back; the surrounding prose is built around it.

3. **List comprehension over a tuple is unimplemented.** `chapter7/section6.tex`
   (l. 109) documents `let b = [i for i in a];` over a tuple, *and* shows the
   YIL it is supposed to produce. The compiler reports "void expression cannot
   be used as a value". The prose promises compile-time unfolding, so this looks
   like a missing compiler feature rather than a book error.

4. **`assert` on a compile-time-constant condition is a hard error**
   ("useless runtime assertion for a test that is always true"). The book uses
   `assert` as its main device for showing what a value is — e.g.
   `assert (a.fst == b.fst)` after literal initialisation. **5 listings** trip
   this, and it constrains how examples can be written going forward.
   Options: relax the diagnostic to a warning, exempt book-style examples, or
   switch the book's idiom to `println` + expected-output blocks.

5. **An unused variable is a fatal error — and this is now the single biggest
   problem in the book.** **42 listings** fail on nothing else.

   ```
   fn main () {
     let x = 12;
   }
   ```
   ```
   Error : when validating u1::main
       ┃ Warning : the symbol x was declared but never used
   ```

   Three things are wrong here, and they are worth separating:

   - The diagnostic calls itself a **Warning** but is **fatal** (exit 1).
   - There is **no way to suppress it**. `-w` and `-Wno-unused-variable` are
     both accepted and both ignored.
   - It **poisons the type of the enclosing expression**. In
     `let a = [foo () for i in 0 .. 4]; a [0]`, the unused `i` makes `a`'s type
     `error`, and the *reported* failure is "the index operator is not defined
     for type error and {i32}" — which points at the wrong line entirely and
     says nothing about `i`. This one is a plain compiler bug whatever is
     decided about the policy.

   The book's whole teaching idiom collides with this. `let x = loop { ... break
   12; };` exists to show that a loop yields a value; binding it and not using
   it is the point. So is declaring a variable purely to show its type.

   This item and item 4 together decide the teaching style of the whole book, so
   they should be settled before more chapters are written. **Recommendation:**
   make the unused-variable diagnostic an actual warning (non-fatal), and fix
   the type-poisoning bug regardless — if the policy stays, `_` is the book-side
   answer, but `_` is itself undocumented (§3.2).

### 2.2 Environment — the installed standard library is stale

`/usr/include/ymir/1.2/` does not parse with the reference compiler:

- `std/conv.yr:311` — `pub fn if (isSigned!{I} && ...)` → "unexpected if"
- `std/fs/path.yr:474` — `pub fn stripExtension(self, ...)` → "read (, but
  expected {"

So **any listing importing `std::conv` or `std::fs` fails for reasons that have
nothing to do with the book** — 3 listings today. `tools/check_listings.py`
classifies these separately as `stale-stdlib` so they never masquerade as book
defects. Reinstalling the stdlib from `gcc-src` should clear them; until then
the classification is the mitigation.

### 2.3 Known non-issues

For future audits, these all *look* like failures but are not:

- **23 listings** fail with `undefined symbol` because they are narrative
  fragments referring to symbols defined earlier in the prose. Annotate these
  with `%% check: skip` as you touch them; that is the only way the harness can
  tell them from real breakage.
- Module examples (`in foo;`) require the file to actually be named `foo.yr`,
  and `in` must precede everything — including any `use` a harness prepends.
  The harness handles this by naming its temp file after the declared module;
  a module in a *subdirectory* (`chapter5/section1.tex` l. 48) still cannot be
  checked and is marked `%% check: skip`.
- **Error-demo markers are standardised** (2026-08-09). A listing whose code
  must not compile carries `style=coloredverbatimError`, which is also what puts
  the *Invalid Ymir* badge on it in the PDF; all 71 were converted. The old
  spellings (`// error`, `// not allowed`, `// forbidden`, the captions
  `Invalid` and `Ymir program with errors`) are still accepted by the harness,
  and remain useful on the *line* that is at fault. See `BOOK_REVIEW.md`.
- The keyword list in `chapter2/section1.tex` is accurate except that it lists
  `do` (see §2.1 item 1). It omits `_`, `async`, `await`, `continue`, `self`,
  `super`, `template`, `yield` — see roadmap.

---

## 3. Roadmap — what the book is missing

### 3.1 Chapters the book already promises but does not contain

These are live `\ref`s that resolve to nothing, so the book itself names them.
The list is maintained as `tools/pending_labels.txt`; delete a line there when
the material lands and `check_refs.py` starts enforcing it.

| Label | Refs | Subject |
|---|---|---|
| `chap:Error_handling` | 4 | exceptions, `throws`, `catch`, scope guards, option/error interplay |
| `chap:conditional_compilation` | 3 | `__version`, `cte`, `__pragma` |
| `chap:custom_types` | 4 | user-defined types (spelling now normalised, see §1.4) |
| `chap:structures` | 2 | `record` / `entity` |
| `chap:std_and_core_runtime` | 2 | the standard library and runtime |
| `chap:templates` | 1 | `{T}` templates, `of` / `over` / `impl` specialisation |
| `chap:macros` | 1 | `macro`, the macro rule keys |
| `chap:documentation` | 1 | doc comments, `-fdoc` |
| `chap:type_and_values` | 1 | "all expressions and statements" — ambiguous, may map to an existing chapter |

Unresolved section refs pointing at unwritten material:
`sec:pattern_matching` (3), `sec:impl_lazy_closure` (3), `sec:pragmas`,
`sec:string_lit`, `sec:function_overloading`, `sec:mutable_parameter`,
`sec:mut_ret_param`, `sec:external_decls`, `sec:class_override_for_loop`,
`sec:class_override_lst_compr`.

### 3.2 Language features implemented but undocumented

Found by diffing `keys.yr` against the book's keyword list:

- **`async` / `await` / `yield`** — present in the compiler
  (`syntax/expression/control/await_.yr`, `syntax/expression/instruction/yield_.yr`).
  Entirely absent from the book. Needs a concurrency chapter alongside the
  existing `spawn` / `atomic` / `future` keywords, which are also only listed,
  never taught.
- **`continue`** — reserved keyword, never mentioned. Chapter 7 covers `break`
  but not `continue`.
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

Existing chapters, against `progress.org`:

| Ch | Title | State |
|---|---|---|
| 1 | Fundamentals | written; exercises still TODO in `progress.org` |
| 2 | Fundamental types, constants and variables | written; exercises TODO; keyword list needs the `do` correction |
| 3 | Native scalar types | written |
| 4 | Native compound types | written; was the densest source of drift |
| 5 | Global constructions | written; §function-body needs the §2.1-item-2 decision |
| 6 | Variables and memory management | written |
| 7 | Control flows | written; §do-while needs the §2.1-item-1 decision |

`progress.org` is stale — it still describes chapters 3–7 as `TODO`/`START` with
empty "List of content" sections, though all seven are drafted. It should be
rewritten against the table above plus §3.1.

Possible content duplication, noticed but not investigated: `chapter2/section6`
("Character and String types") and `chapter3/section3` both cover character
types, and both define a table captioned "Escape characters"
(`tab:(chap2):escape_chars` and `tab:escape_chars`). Worth a look.

### 3.4 Tooling

**Built** (this pass):

- **`tools/check_listings.py`** — compiles every Ymir listing and classifies
  each failure (`unused`, `undefined-symbol`, `const-assert`, `stale-stdlib`,
  `other`), so a run says *why* rather than just *how many*. Supports
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
3. **Annotate the 23 narrative fragments** with `%% check: skip`. Once done,
   every remaining listing failure is real, and the checker can be made
   blocking.
4. **Fail the build on missing glyphs.** The `~` regression was invisible in
   the PDF (blank space) and sat in 62 places; the π one survived a full audit
   pass. `grep -c "Missing character" .build/main.log` is the whole check.
5. **Enforce the `(chapN):` label prefix convention.** §1.4 normalised the
   stragglers; a check in `check_refs.py` would stop it drifting again.
