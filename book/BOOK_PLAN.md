# Ymir book — structural plan

Companion to `BOOK_AUDIT.md` (technical correctness) and `BOOK_REVIEW.md`
(editorial consistency). This file is about **shape**: what the book is, what
order it goes in, and what is still missing. It supersedes `progress.org`, which
is stale (see `BOOK_AUDIT.md` §3.3) but whose design intent is preserved below.

Drafted 2026-08-09. The two-part split described here **landed the same day**;
everything below the "Landed" heading is still to do.

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

Part II follows the order of Part I, chapter for chapter.

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
  parts, and `chapters/chapter1/structure.tex` §How this book is structured
  rewritten to describe parts rather than interleaved page colors.

Verified after the split: 182 pages, 0 missing glyphs, 0 multiply-defined
labels, 163 labels with 0 broken references, listings unchanged at 113/162 with
80/80 error demos failing as intended.

### Still owed by the split

**Chapter directories are still named by number** (`chapters/chapter5/` is now
chapter 7). Renaming them by topic — `chapters/spec/global_constructions/` —
would finish the job and stop the drift, but it touches every `\input`, both
audit documents, and every path cited in them. Deliberately left out of the
structural change so the diff stayed reviewable; worth doing before Part I grows,
because every new tutorial chapter makes it bigger.

**`main.tex` is still titled "Ymir language specification 1.2"**, which now
names only the second half. Something like "The Ymir Programming Language — a
course and a specification, version 1.2" covers both.

## Part I — Learning Ymir

For readers with no computer science background (`README.md`). Narrative prose,
concrete examples, exercises with solutions at the end of every chapter.

| # | Chapter | Status | Covers |
|---|---|---|---|
| 1 | Fundamentals | **drafted, reviewed** | toolchain, source layout, YIL, Gyllir, first program |
| 2 | Fundamental types, constants and variables | **drafted, reviewed** | identifiers, variables, operators, int/bool/float/char |
| 3 | Control flow | *missing* | `if`/`else`, loops, `match` introduction, scope |
| 4 | Functions | *missing* | declaration, parameters, return, UCS, optional parameters, overloading |
| 5 | Compound types and collections | *missing* | arrays, slices, tuples, ranges, options |
| 6 | Memory, mutability and references | *missing* | `copy`/`alias`/`dcopy`, `mut`/`dmut` levels, references, laziness |
| 7 | Structures and custom types | *missing* | records, classes, methods, traits, inheritance |
| 8 | Error handling | *missing* | exceptions, options, `catch`, scope guards |
| 9 | Program structure | *missing* | modules, packages, visibility, unit tests, shipping with Gyllir |
| 10 | Concurrency | *optional* | threads, synchronization |

**Chapter 9 is the tutorial counterpart of Part II's Global constructions.** A
reader needs modules only once they have a program big enough to split, which is
after functions, types and error handling — not before them.

Two ordering notes where this departs from `progress.org`:

- `progress.org` puts *Compound types and basic collections* before *Fundamental
  control flow*. This plan reverses them: `if` and `while` over scalars let a
  reader write something that does anything, whereas an array you cannot loop
  over is inert. Iterating a collection is then the payoff for `for`.
- Memory and mutability (6) lands after collections (5), because borrowing
  cannot be motivated before there is something worth borrowing — but before
  custom types (7), which lean on it heavily.

## Part II — Language specification

Judged on template uniformity and completeness, not on how it reads
(`BOOK_REVIEW.md`, "What is left" item 2).

| Chapter | Status |
|---|---|
| Native scalar types | **drafted, reviewed** |
| Control flows | drafted, **not reviewed** |
| Native compound types | **drafted, reviewed** |
| Variables and memory management | drafted, **not reviewed** |
| Global constructions | **drafted, reviewed** |
| Custom types | *missing* — promised by `chap:custom_types` (4 sites) |
| Templates | *missing* — promised by `chap:templates` |
| Macros | *missing* — promised by `chap:macros` |
| Conditional compilation and pragmas | *missing* — promised by `chap:conditional_compilation` (3 sites), `sec:pragmas` |
| Error handling | *missing* — promised by `chap:Error_handling` |
| Documentation | *missing* — promised by `chap:documentation` |
| Standard library and runtime | *missing* — promised by `chap:std_and_core_runtime` |
| Types and values | *missing* — promised by `chap:type_and_values`, the exhaustive expression/statement list |

None of these are inventions: each is already referenced by name from drafted
prose. `make check-refs` reports **18 pending references** — 9 of them the
chapter names above, 9 of them sections inside chapters that are themselves
unwritten (`sec:pattern_matching`, `sec:function_overloading`, `sec:string_lit`,
`sec:pragmas`, `sec:impl_lazy_closure`, `sec:mutable_parameter`,
`sec:mut_ret_param`, `sec:class_override_for_loop`,
`sec:class_override_lst_compr`).

## Open decisions

- **Is Part II's *Global constructions* one chapter or two?** Its §Modules and
  §Global variables are program-structure topics pairing with Part I ch. 9,
  while §Functions is 45% of the chapter and pairs with Part I ch. 4. Splitting
  it into *Functions* and *Modules and packages* would make Part II mirror Part
  I exactly, which is the whole point of the new order. This is the one place
  the mirroring currently breaks.
- **Does `chap:structures` mean *Custom types*, or a separate chapter on
  records?** Referenced from the scalar and compound type chapters.
- **Does `chap:Error_handling` want a chapter or a section?** Part II's *Control
  flows* already has §Handling exceptions and §Scope guards.

## Suggested order of work

1. Editorial pass on Part II's two unreviewed chapters (*Control flows*,
   *Variables and memory management*) — the last of the drafted material, and
   the `BOOK_REVIEW.md` backlog.
2. Decide the *Global constructions* split, and do it while the chapter is fresh
   from its review.
3. Write Part I chapters 3 and 4 (*Control flow*, *Functions*). They unblock the
   most: every later tutorial chapter needs both, and Part II already has the
   reference material to point at.
4. Write Part II *Custom types*. It is the most-referenced missing chapter and
   blocks Part I ch. 7.
5. Everything else, in Part I order.
