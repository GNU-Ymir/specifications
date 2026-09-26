# Ymir book — structural plan

Companion to `BOOK_AUDIT.md` (technical correctness) and `BOOK_REVIEW.md`
(editorial consistency). This file is about **shape**: what the book is, what
order it goes in, and what is still missing. `progress.org` tracks progress
against this plan, section by section; it was rewritten to follow this plan on
2026-09-26.

Drafted 2026-08-09. The two-part split described here **landed the same day**.
On 2026-09-26 the chapter order was revised ("Advanced control flow moved out of
the early chapters") and applied to Part II. Part I chapter 3 landed the same
day, with Part II *Control flows* rewritten as a specification (BOOK-7); Part I
chapters 4 to 14 are still to write.

## Why the book was split

The book used to say three different things about what it is.

| Where | What it said |
|---|---|
| `README.md` | "It's not a specification — but a training course." |
| `main.tex` title | "Ymir language specification 1.2" |
| `chapters/preamble.tex` | light gray pages "are not intended to be read during the initial reading" |

Those can all be true at once, but only if the two kinds of material are
separated. They were interleaved, and the proportions had drifted: chapters 1
and 2 were white with exercises, chapters 3 to 7 all light gray. A reader who
followed the preamble's own instruction read two chapters, was told the
remaining five were not for the initial reading, and found nothing after them.
**71% of the book was marked "come back later", with no later to come back to.**

That is also why chapter 5 did not read like a tutorial: it was not one. It was
specification sitting in a position that implied otherwise.

## Landed

```
Part I  — Learning Ymir           white, course, read in order
Part II — Language specification  light gray, consulted rather than read
```

Part II followed the order of Part I, chapter for chapter, until 2026-09-26,
when the rule was dropped (see "Part II — Language specification").

| Part | # | Chapter | Was | Pairs with |
|---|---|---|---|---|
| I | 1 | Fundamentals | ch. 1 | — |
| I | 2 | Fundamental types, constants and variables | ch. 2 | II-3 |
| II | 3 | Native scalar types | ch. 3 | I-2 |
| II | 4 | Control flows | ch. 7 | I-3 *(missing)* |
| II | 5 | Native compound types | ch. 4 | I-5 *(missing)* |
| II | 6 | Variables and memory management | ch. 6 | I-6 *(missing)* |
| II | 7 | Global constructions | ch. 5 | I-4 and I-9 *(missing)* |

Mechanically, this was:

- `\part{}` in `main.tex`, with the page color set once at each part boundary
  instead of per chapter. Every `\pagecolor`/`\nopagecolor` in
  `chapters/chapter*.tex` is gone.
- **Label prefixes renamed by topic.** 33 labels encoded a chapter number
  (`fig:(chap5):file_hierarchy`), referenced 74 times; they were wrong the
  moment anything moved, and `make check-refs` cannot detect a *stale but
  resolving* prefix. Now `basics`, `types`, `scalars`, `compound`, `memory`,
  `flow`, `global` — immune to future reordering. The chapter labels
  `chap:chapN` went the same way (`chap:scalars`, `chap:global_constructions`),
  and the three that already had a topic alias (`chap:compound`,
  `chap:variables`, `chap:control_flows`) simply lost the numbered duplicate.
- The preamble's color-coding paragraph replaced by two sentences naming the two
  parts, and `chapters/course/basics/structure.tex` §How this book is structured
  rewritten to describe parts rather than interleaved page colors.

Verified after the split: 182 pages, 0 missing glyphs, 0 multiply-defined
labels, 163 labels with 0 broken references, listings unchanged at 113/162 with
80/80 error demos failing as intended.

### Still owed by the split

**Chapter directories were named by number** (`chapters/chapter5/` was chapter
7). Done 2026-09-26: they are named by part and label topic, `chapters/course/`
for Part I and `chapters/spec/` for Part II (`chapters/spec/global/`).

**`main.tex` was still titled "Ymir language specification 1.2"**, which named
only the second half. Done: the title page now reads "The Ymir Programming
Language: A Guided Tour", and the PDF title is "The Ymir Book".

## Part I — Learning Ymir

For readers with no computer science background (`README.md`). Narrative prose,
concrete examples, exercises with solutions at the end of every chapter.

| # | Chapter | Status | Covers | Payoff |
|---|---|---|---|---|
| 1 | Fundamentals | **drafted, reviewed** | toolchain, source layout, YIL, Gyllir, first program | a program that runs |
| 2 | Fundamental types, constants and variables | **drafted, reviewed** | identifiers, variables, operators, int/bool/float/char | computing with values |
| 3 | Control flow | **drafted**, not reviewed | `if`/`else`, `loop`, `break`, `continue`, `while`, `for` over ranges, blocks as values, a first look at `match` on scalars | programs that decide and repeat |
| 4 | Functions | *missing* | declaration, parameters, return, UCS, optional parameters, overloading, lambdas and function pointers | code that can be reused |
| 5 | Compound types and collections | *missing* | arrays, slices, tuples, ranges, options; `for` over each | looping over real data |
| 6 | Memory, mutability and references | *missing* | `copy`/`alias`/`dcopy`, `mut`/`dmut`, references, `for ref`/`for mut` iterators | changing data in place |
| 7 | Program structure | *missing* | modules, packages, visibility, global variables, unit tests, Gyllir | a multi-file project with tests |
| 8 | Comprehensions | *missing* | list comprehension, filters, nested `for`, `ref`/`mut` iterators, map comprehension | one expression instead of a loop |
| 9 | Structures and custom types | *missing* | records, classes, methods, traits, inheritance; making a type iterable (`begin`/`end`/`next`) | your own types work in `for` and in comprehensions |
| 10 | Error handling | *missing* | exceptions, `throws`, `catch`, scope guards, options revisited | failure handled, cleanup guaranteed |
| 11 | Laziness and generators | *missing* | `lazy` values, parameters and globals, how they are built as closures, `yield` functions | values computed only when needed |
| 12 | Memory layout and execution | *missing* | stack and heap, call frames, what a function call does, where each type lives (scalars and tuples inline, static arrays, slices as pointer and length, class instances on the heap), the garbage collector, size and alignment (`size`, `@packed`), what a closure, a lazy value and a generator keep in memory, read through YIL | knowing what the machine does with your program |
| 13 | Asynchronous programming | *missing*, blocked on `await` | `async` functions and lambdas, `async-> T`, `await` | waiting without blocking |
| 14 | Concurrency | *missing* | threads: `spawn`, `future`, `.value`, `.finished`, `await` on a future; shared data: `atomic` blocks, `@thread` globals, synchronization; threads against coroutines | work done in parallel |

Two ordering notes from the first version of this plan still hold:

- `progress.org` used to put *Compound types and basic collections* before
  *Fundamental control flow*. This plan reverses them: `if` and `while` over
  scalars let a reader write something that does anything, whereas an array you
  cannot loop over is inert. Iterating a collection is then the payoff for `for`.
- Memory and mutability (6) lands after collections (5), because borrowing
  cannot be motivated before there is something worth borrowing — but before
  custom types (9), which lean on it heavily.

Chapters 7 to 14 were reordered on 2026-09-26; the reasons are in "Advanced
control flow moved out of the early chapters", below.

## Part II — Language specification

Judged on template uniformity and completeness, not on how it reads
(`BOOK_REVIEW.md`, "What is left" item 2). Each chapter pairs with a Part I
chapter, but Part II is ordered by the language, not by the course: a chapter
comes after the ones it relies on. *Control flows* therefore follows *Native
compound types*, whose types its `for` iterates over, although Part I teaches
control flow first. Part II opens with *Notation*, the conventions of the whole
part, and ends with reference chapters that have no Part I counterpart.
Mirroring Part I was the rule until 2026-09-26 (BOOK-7 review), and was dropped
because the course order, set by what a newcomer needs first, is not the
order of the language.

| Chapter | Directory | Pairs with | Status |
|---|---|---|---|
| Notation | `spec/notation` | — | drafted, **not reviewed** |
| Native scalar types | `spec/scalars` | I-2 | **drafted, reviewed** |
| Native compound types | `spec/compound` | I-5 | **drafted, reviewed** |
| Control flows | `spec/flow` | I-3 | rewritten as a specification, **not reviewed** |
| Variables and memory management | `spec/memory` | I-6 | drafted, **not reviewed** |
| Global constructions | `spec/global` | I-4 and I-7 | **drafted, reviewed** |
| Comprehensions | `spec/compr` | I-8 | drafted, **not reviewed**; filters and map comprehension missing |
| Custom types | — | I-9 | *missing* — promised by `chap:custom_types` (4 sites); holds `sec:class_override_for_loop` and `sec:class_override_lst_compr` |
| Error handling | `spec/error` | I-10 | drafted, **not reviewed** |
| Laziness | `spec/lazy` | I-11 | drafted, **not reviewed**; generators missing |
| Memory layout and execution | — | I-12 | *missing* — holds `sec:impl_lazy_closure`; *Native compound types* §Pointers may move here |
| Asynchronous programming | — | I-13 | *missing* |
| Concurrency | — | I-14 | *missing* |
| Templates | — | — | *missing* — promised by `chap:templates` |
| Macros | — | — | *missing* — promised by `chap:macros` |
| Conditional compilation and pragmas | — | — | *missing* — promised by `chap:conditional_compilation` (3 sites), `sec:pragmas` |
| Documentation | — | — | *missing* — promised by `chap:documentation` |
| Standard library and runtime | — | — | *missing* — promised by `chap:std_and_core_runtime` |
| Types and values | — | — | *missing* — promised by `chap:type_and_values`, the exhaustive expression/statement list |

`make check-refs` reports **16 pending references**: 8 chapter labels
(`chap:structures` besides the chapters above) and 8 sections inside chapters
that are themselves unwritten (`sec:function_overloading`, `sec:string_lit`, `sec:pragmas`,
`sec:impl_lazy_closure`, `sec:mutable_parameter`, `sec:mut_ret_param`,
`sec:class_override_for_loop`, `sec:class_override_lst_compr`).

## Advanced control flow moved out of the early chapters

Decided 2026-09-26. Applied to Part II the same day: the chapter directories
were renamed by topic, the `with` section deleted, and *Comprehensions*,
*Error handling* and *Laziness* split out of *Control flows* and *Variables and
memory management*. Listings unchanged at 98/162 with `ymirc`; 79/79 error
demos, one fewer with `with`.

### The problem

Part II *Control flows* is the counterpart of Part I ch. 3, the reader's first
contact with loops. It held five sections that a ch. 3 reader cannot use yet:

| Section | Needs first | Now |
|---|---|---|
| §6 List comprehension | collections (I-5); `ref`/`mut` iterators (I-6); functions for the element expression (I-4) | *Comprehensions* |
| §7 Scope guards | exceptions (I-10) | *Error handling* §1 |
| §8 Handling exceptions | exception *classes* (I-9) | *Error handling* §2 |
| §9 Threads synchronization | threads, which the book never introduces (it was a heading and a label) | deleted; comes back with *Concurrency* |
| §10 Disposing scope declaration | nothing: the `with` scope is a relic the compiler no longer has (`with` survives only in constructors, `self (x: i32) with x = x`) | deleted |

Part II *Variables and memory management* §5 Laziness had the same problem. It
lived in the memory chapter because `lazy` is a variable modifier, but it cites
`sec:impl_lazy_closure`, how lazy values are built as closures. Closures are
functions, not memory. It is now *Laziness* §1.

The compiler also has features the book never mentions that belong with these
chapters (checked against `~/ymir/ymir-dev/repos/bootstrap/test_resources`,
2026-09-26):

- `yield` functions (generators), consumed by `for` and by comprehensions
  (`generators/`)
- filtered comprehensions `[f (x) for x in r if p (x)]` and map comprehensions
  `[x => f (x) for x in r]` (`for_loops/lst_compr/test24.yr`, `for_loops/map_compr/`)
- `spawn`, `future-> T`, `.value`, `.finished` (`concurrency/`)
- `async` functions and lambdas, of type `async-> T`: stackless coroutines
  (`src/ymirc/semantic/generator/type/native/scalar/async_.yr`). `await` parses
  but is rejected in 1.6 with E4282 "not supported" (`docs/errors/E4282.md`,
  `syntax/test15.yr`)
- `atomic { }` blocks (`control_flow/test23.yr`) and `@thread` globals
  (`global/test8.yr`)

### The principle

Each chapter uses only what an earlier chapter taught, and ends on something
the reader could not do before. A feature goes in the first chapter where the
reader can both write it and see why it exists. It does not go in the first
chapter where it merely parses.

### Why this order

- **Comprehensions come right after the reader has had enough loops.** In
  ch. 3–6 a reader writes the same shape over and over: create an empty array,
  loop, append. Ch. 8 turns that shape into one expression. Taught in ch. 3, a
  comprehension is only syntax. By ch. 8 it replaces code the reader has
  already written by hand.
- **Comprehensions come before custom types** because ch. 9's best payoff is
  "make your class iterable, and `for` *and* comprehensions accept it". The
  pending labels `sec:class_override_for_loop` and `sec:class_override_lst_compr`
  already say this; they only make sense if both constructs are known.
- **Program structure comes before comprehensions**, so that every topic moved
  out of the early chapters arrives after it. This reverses the plan's earlier
  reasoning, which put modules after custom types and error handling ("a reader
  needs modules only once they have a program big enough to split"). After six
  chapters, the reader has such a program. From ch. 7 on,
  every exercise can be a Gyllir project whose unit tests check the solution.
  Module visibility also comes before member visibility in ch. 9, which is the
  natural order.
- **Error handling stays after custom types**: exceptions are classes. Scope
  guards go with it because their main use is cleanup when an exception is
  thrown.
- **Laziness gets its own chapter, with `yield`**: both describe computation
  that is deferred. A `lazy` value is computed once, the first time it is read.
  A generator produces a sequence one element at a time, as the consumer asks
  for it. The chapter needs closures (4), `dmut` lazy values (6), lazy globals
  (7), and generators that feed comprehensions (8) and yield records (9).
- **Memory layout comes after laziness and before async and concurrency.** Until
  ch. 12 the book explains memory in terms of values: copy, alias, mutable or
  not (ch. 6). Ch. 12 explains it in terms of the machine. It has to come after
  ch. 11, because its best examples are the ones that looked like magic: where a
  closure's captured variables live, what a lazy value stores before it is
  computed, how a generator resumes after `yield`. It has to come before
  ch. 13 and 14: a stackless coroutine only means something to a reader who
  knows what a stack is, and every thread has its own stack and shares one
  heap. That shared heap is what makes synchronization necessary.
- **Asynchronous programming comes before concurrency**, in a chapter of its
  own, because it is the simpler of the two. An `async` function is a stackless
  coroutine: it suspends like a generator (11) and keeps no stack of its own
  (12). Everything still runs on one thread, so there is no data race and
  nothing to synchronize. The reader learns to reason about work that is
  interleaved before dealing with work that happens at the same time.
- **Concurrency is last**, because it is the hardest: several threads, one
  heap, and races the reader must prevent. It follows from laziness, layout and
  async. A `future` is a value computed on another thread, where a `lazy` value
  is computed later on the same one. `await` is already known from ch. 13 and
  now applies to a future. `@thread` globals need ch. 7, and synchronization
  needs mutation (6) and error handling (10). The chapter closes by comparing
  threads with the coroutines of ch. 13.

### Frictions to settle before writing

1. ~~**`throws AssertError` appears from ch. 2 on**~~ **Settled** 2026-09-26:
   `course/types/section7.tex` now says what `assert` does, and tells the
   reader to treat `throws AssertError` as part of the formula until
   *Error handling* (`chap:error`) explains it.
2. **Maps are taught nowhere.** Part II *Native compound types* has no map
   section. Map comprehension needs maps, so either ch. 5 gains a map section
   (preferred, since maps are a collection) or ch. 8 introduces them.
3. **Part I label topics.** A topic names one chapter and one directory
   (`BOOK_STYLE.md` § Labels), and Part II already uses `flow`, `compound`,
   `memory`, `compr`, `error` and `lazy`. Part I chapters 3 to 14 need topics of
   their own, chosen before the first of them is written. Ch. 3 is `control`
   (2026-09-26); ch. 4 to 14 are still to choose.
4. **Part I must follow `ymirc`, as Part II now does** (`BOOK_AUDIT.md`
   § 2.1). No do-while; braces around every function body; a variable or `use`
   that is never read does not compile, so listings print what they declare;
   `assert` on a value the compiler knows does not compile either. Mutable
   lazy globals and mutable comprehension iterators are allowed.
5. ~~**Pattern matching** is still unplaced.~~ **Settled** 2026-09-26: the full
   treatment is Part II *Control flows* § Pattern matching
   (`sec:flow:pattern_matching`). Part I teaches it in steps: integers in 3
   (`sec:control:match`), tuples and options in 5, classes in 9.
6. **Ch. 12 and the earlier YIL listings.** Chapters 1 to 11 already show YIL
   without explaining the stack. Ch. 12 is where the reader can finally read
   those listings in full, so it should point back to a few of them rather than
   start from new examples.
7. **Ch. 13 depends on the compiler.** `await` raises E4282 in 1.6. Write
   ch. 13 when `await` validates, and until then refer to it through
   `chap:async` in `tools/pending_labels.txt`. Ch. 14 can be written first: the
   thread material stands without it, apart from `await` on a future and the
   closing comparison, which wait for ch. 13.

## Proposed: a part on programming in general

Proposed by the author on 2026-09-26. **Idea only**: no chapter is written, no
directory or label exists, and nothing below is scheduled.

The book would have three parts instead of two:

```
Part I   — Learning Ymir               white, course, read in order
Part II  — Programming                 course, not tied to Ymir
Part III — Language specification      light gray, consulted (today's Part II)
```

The new Part II teaches programming beyond the language itself: material a
reader needs whatever language they write in, with Ymir as the language of the
examples and exercises. The first candidate is a chapter on **algorithms**,
for example:

- sorting (insertion, merge, quick sort), and why their costs differ;
- searching, including binary search on a sorted collection;
- graphs: representation, traversal (breadth-first, depth-first), shortest
  paths;
- the travelling salesman problem (TSP): an exact search, why it does not scale,
  and heuristics that give a good tour quickly;
- enough complexity analysis to compare all of the above.

Other chapters in the same spirit could follow (data structures, dynamic
programming, testing, …); which ones is part of the decision.

### What it would take

- **Prerequisites.** Algorithms on collections need Part I ch. 4 (functions),
  5 (collections) and 6 (mutation in place); graphs are more natural with
  ch. 9 (custom types). The new part therefore comes after Part I in full, or at
  least after ch. 9, and cannot be written before those chapters exist.
- **Renaming "Part II".** Every mention of the specification as Part II would
  become Part III: `chapters/preamble.tex`, `chapters/course/basics/structure.tex`
  (which describes the parts and their page colours), the `\part` headings in
  `main.tex`, `README.md`, `CLAUDE.md`, `progress.org` and these `BOOK_*` files.
  Labels are not affected: they name topics, not parts.
- **Layout.** A third directory under `chapters/` (for example
  `chapters/programming/`), and label topics distinct from those of the other
  two parts (`BOOK_STYLE.md` § Labels).
- **Page colour.** Part I is white and the specification light gray; the new
  part needs a colour of its own, or shares Part I's, since it is also a course
  read in order, with exercises.
- **Pairing.** Each specification chapter pairs with a Part I chapter. The new
  part has no specification counterpart, and does not change that rule.

## Open decisions

- **Is Part II's *Global constructions* one chapter or two?** Its §Modules and
  §Global variables are program-structure topics pairing with Part I ch. 7,
  while §Functions is 45% of the chapter and pairs with Part I ch. 4. Splitting
  it into *Functions* and *Modules and packages* would give each of the two
  Part I chapters a counterpart of its own. This is the one place a Part II
  chapter pairs with two Part I chapters.
- **Does `chap:structures` mean *Custom types*, or a separate chapter on
  records?** Referenced from the scalar and compound type chapters.
- **Should the book gain a part on programming in general** (algorithms first),
  moving the specification to Part III? See "Proposed: a part on programming in
  general". To decide: which chapters, where the part starts relative to Part I,
  and its page colour.

## Suggested order of work

1. Editorial pass on Part II's unreviewed chapters (*Control flows*, *Variables
   and memory management*, and the three split out of them) — the last of the
   drafted material, and the `BOOK_REVIEW.md` backlog.
2. Decide the *Global constructions* split, and do it while the chapter is fresh
   from its review.
3. ~~Choose the Part I label topics (friction 3), then write Part I chapter 3
   (*Control flow*)~~ — done 2026-09-26. Next, chapter 4 (*Functions*). With
   chapter 3 it unblocks the most: every later tutorial chapter needs both, and
   Part II already has the reference material to point at.
4. Write Part II *Custom types*. It is the most-referenced missing chapter and
   blocks Part I ch. 9.
5. Everything else, in Part I order.
