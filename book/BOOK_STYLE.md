# Ymir book — house style

Fourth companion to `BOOK_AUDIT.md` (technical correctness), `BOOK_REVIEW.md`
(editorial consistency) and `BOOK_PLAN.md` (shape). This file is about
**surface**: the markup and the typography. It records the conventions the
sources follow, so that a new chapter looks like the ones around it, and so that
a reviewer can tell a deviation from a decision.

Written 2026-08-10, alongside the style pass that made the book conform to it.
Every rule below is the majority practice that already existed; the pass moved
the minority to match, and the counts under each rule are what the sweep found.

## Inline code

| Write | For | Notes |
|---|---|---|
| `\token{...}` | a fragment of Ymir source in running prose | goes through `\lstinline`, so it gets the language's keyword colouring |
| `\tokennolst{...}` | the same, when the fragment contains a character TeX reads specially | `%`, `^`, `~`, `\`; the argument is ordinary LaTeX, so write `\%` and `\textasciicircum{}` |
| `\texttt{...}` | machine text that is *not* Ymir source | bit patterns, and text inside a listing's `escapechar` region |
| `\textit{...}` | file and directory names, a term of art at first use | `\textit{hello.yr}`, `\textit{rvalue}`, `\textit{do-while}` |

**Never `\verb` or `\Verb`.** They were used in four table cells to write `^^`,
`>>` and `<<`, which also forced the surrounding expression to be split into
three chips with gaps between them, unlike every other row of the same tables.

`\token` is unbreakable, so a long one — `\token{foo::bar::pubFuncInBar}` — has
only the line positions the surrounding words leave it. `\emergencystretch` in
`special_header.tex` is what buys the room to place it; do not add `\allowbreak`
around chips, which opens an empty first line when a chip starts a table cell.

*The sweep converted 292 `\texttt` to `\token`/`\tokennolst` and removed all 8
`\verb`. 57 `\texttt` remain, all of them legitimately in the last two rows of
the table above.*

## Asides

Five callout commands, all tinted, distinguished only by their icon:

```
\notebox{}  \tipbox{}  \cautionbox{}  \warningbox{}  \importantbox{}
```

There used to be a second set — `\mynotebox`, `\mytipbox`, `\mycautionbox` —
which differed by laying a grey tint behind the text. Which set an aside got was
a matter of which chapter it was written in. The tint now lives in the five
commands themselves and the `my*` aliases are gone.

*7 call sites moved; 19 asides in the book.*

## Listings

| Style | For | Badge |
|---|---|---|
| `coloredverbatim` | Ymir source | Ymir |
| `coloredverbatimError` | Ymir source that deliberately does not compile | Invalid Ymir |
| `cVerb` | C source, for interoperability | C |
| `myilVerb` / `lyilVerb` | compiler-generated intermediate representations | M-YIL / L-YIL |
| `bashVerb` | a terminal session, and program output | Terminal |

There was a sixth, `coloredverbatimCorrect`, used by the two listings that carry
a green correction highlight. It was a copy of `coloredverbatim` that had
drifted: it still highlighted `struct` and `@union`, the spellings that became
`record` and `@overlaid`, and had missed twenty keywords added to the main style
since. The correction highlight comes from `escapechar` at the call site, not
from the style, so both listings now use `coloredverbatim` and the fork is gone.

**Known deviation, not yet resolved.** `bashVerb` carries a terminal badge and
is used for three different things: real shell sessions, program output, and the
two grammar productions in `chapters/chapter6/section2.tex`. A grammar
production labelled "Terminal" is misleading. Two productions did not seem worth
a sixth style; if more are written, they should get one.

## Labels

`kind:topic:name`, where *kind* is one of `chap`, `sec`, `fig`, `tab`, `lst` and
*topic* is one of the seven the book is organised by:

```
basics  types  scalars  compound  memory  flow  global
```

Chapter labels are the topic alone: `\label{chap:scalars}`.

The point of the topic segment, per `BOOK_PLAN.md`, is that a label encoding a
*chapter number* is wrong the moment anything moves, and `make check-refs`
cannot detect a stale-but-resolving prefix. The convention had landed for
figures (22/22) and listings (39/41) but not for sections (5/58); the sweep
renamed the remaining 53 section labels, 2 tables, 2 listings and 4 chapters,
rewriting 124 occurrences. `make check-refs` reports 0 broken before and after.

Also removed: 26 `\label{sec:org409c2d8}`-style labels, left behind by an
org-mode export and referenced by nothing.

Chapter 6 carried two labels for the same chapter, `chap:variables` and
`chap:memory_management`; both are now `chap:memory`. Six sections had no label
at all and now have one, so every division of the book can be referenced.

`sec:types:chap2_char_lit` was the last label naming a chapter number; it is
`sec:types:char_literal`. No label anywhere now contains one.

## Cross-references

The referring word matches the kind of label: `Chapter~\ref{chap:...}`,
`Section~\ref{sec:...}`, `Figure~\ref{fig:...}`, `Table~\ref{tab:...}`,
`Listing~\ref{lst:...}`, all capitalised, all with a non-breaking space.

Four references said "Chapter" while pointing at a `sec:` label, and two were
lowercase. A reference whose word contradicts its label is not caught by
`make check-refs`, which only checks that the label resolves — so it is worth
grepping for `Chapter~\ref{sec:` after any move.

## Heads and captions

- `\section{Title}` — no space before the brace. *(50 fixed.)*
- `\caption{\label{...} Text}` — the label first, inside the caption. 27 of 31
  captions already did this.
- Part, chapter and section heads are set by `titlesec` in `special_header.tex`,
  in the sans face; no chapter-style package is loaded.
- Nothing in `chapters/` adjusts the space under a chapter head. Chapters 1 to 3
  each carried a `\vspace{-50pt}` tuned against the old `fncychap` heads, and
  chapters 4 to 7 did not, so the two halves of the book opened differently.

## Register

The prose is impersonal: it describes what the language and the compiler do,
rather than what "we" will see. `we` still appears where it means the author and
the reader together, but not as padding in front of a statement of fact.

The constructions the pass removed, and that new prose should avoid:

| Instead of | Write |
|---|---|
| the cast operator can be used to convert X | the cast operator converts X |
| the `.` operator is used to access Y | the `.` operator accesses Y |
| it is important that A and B are the same type | A and B must be the same type |
| in that chapter will be presented Z | that chapter also covers Z |
| as we will see in Section~n | Section~n presents |

*46 occurrences of "is/are/can be used to" became verbs; 9 remain, all of them
places where the passive is the accurate voice.*

## Part II section templates

Part II is judged on uniformity, not on how it reads, so each chapter runs its
types through the same subsections in the same order.

- **Chapter 3** (scalars): Literals, Properties, Casting, Unary operators,
  Binary operators, Overflowing. Characters and Boolean had Properties before
  Literals and now do not; the escape-character table moved out of the section
  preamble into Characters' Literals, which is what it documents.
- **Chapter 4** (compound): Literals, Mutability and memory alignment,
  Properties, Binary operators, then whatever the type adds, then Implicit
  casting. Pointers legitimately differ: they have Construction, and their
  casting is Explicit.

A type that genuinely has nothing to say under a heading omits it — Boolean has
no Overflowing — rather than carrying an empty one.

## Typography

Set once in `special_header.tex`; nothing in `chapters/` should override it.

- **Measure** 15cm on a 21.5cm page, about 85 characters. It was 18.4cm — some
  110 characters, half again what a reader tracks comfortably, and the reason
  the body read like a web page.
- **Paragraphs** are block-style: no indent, elastic space between. The space
  was a rigid 10pt, which gave the page-breaker nothing to work with.
- **Links** are a dark desaturated blue, not boxed in red. The table of contents
  and the per-chapter mini-tables set theirs in black.
- **Figures** that need scaling use `\adjustbox{scale=k, max width=\linewidth}`,
  never a bare `\scalebox{k}`: a hard scale factor is tuned against one measure
  and overruns the margin as soon as that changes. *(9 converted.)*
- **Callout boxes** need `\aweboxleftmargin` wide enough for a `\Huge` icon;
  0.05\linewidth was not, and every aside in the book ran into the margin.

The book builds with **0 missing glyphs and 0 overfull boxes**; both should stay
at zero. `make refs` reports them, and a diff of the counts is the cheapest
review a change to `special_header.tex` can get.

## Open, needs an author decision

1. **Table rules.** Part II sets tables as `{|c|lll|}` with `\hline` and a
   doubled `\hline` under the header; the chapter 2 figures use `p{}` columns
   with booktabs' `\toprule`/`\midrule`. Both appear in the same book, and some
   tables mix the two — `\toprule[0.6pt]` used as a header separator,
   `\midrule[0.2pt]` used as a bottom rule. Roughly 45 tables; a sweep to
   booktabs (no vertical rules) would be uniform but is a visible change to
   every one of them.
2. **`\vfill\pagebreak` at the end of every section file.** Every section
   therefore starts on a fresh page, and a section that ends two lines into one
   leaves most of a page blank — see the page after §2.4 and the one after
   §1.2.1. Deliberate for a reference work, expensive for a course.
3. **The title on the title page** still reads "Ymir language specification
   1.2", which `BOOK_PLAN.md` records as one of the three things the book used
   to say about itself. The two-part split resolved the other two; this one is
   still the pre-split wording.
