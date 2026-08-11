# Framed listings — draft

A listing drawn inside one of the two hand-drawn frames in `~/notes/icons`
(`text broken.png`, the cracked slab; `text_solid.png`, the riveted plate),
with the frame growing to whatever height the code needs.

```
make            # cut the pieces if needed, then build test.pdf
make assets     # recut the pieces only
make distclean  # throw the pieces away
```

`test.pdf` shows both frames at one line, at the five lines the drawings were
made at, at twenty-two lines, and on the tinted page colour of part II.

## Using it

```latex
\usepackage{ymirframe}

\begin{brokenlisting}          % cracked slab, badge says "Invalid Ymir"
let dmut a: *i32 = null;
a = &b; // not allowed 'b' is not mutable
\end{brokenlisting}

\begin{solidlisting}           % riveted plate, badge says "Ymir"
let x = 42;
\end{solidlisting}
```

Both take the same optional argument as `lstlisting`, e.g.
`\begin{solidlisting}[language=bash]`.

## How it works

The drawing cannot simply be scaled to the height of the code: that would
thicken its border in the same proportion. `slice.py` cuts it into a
nine-slice instead — four corners, four edges, a centre — and `ymirframe.sty`
reassembles the grid around a `tcolorbox` of any height. The corners are drawn
at a fixed size that depends only on the width of the text block, so they never
distort; the edges take up the slack.

Three things the drawings needed before they could be cut:

- **The page behind them is made transparent**, by flooding inwards from the
  corners rather than by picking a colour, so that the near-white cream of the
  listing's own background is not caught with it. Without this a framed listing
  would carry a white halo onto the tinted pages of part II.
- **The code they were drawn around is painted out.** They are mock-ups: a
  border put around a real listing, so every piece cut from one still carried a
  fragment of `let dmut a` or of the line numbers. What is erased is the region
  enclosed by the border, holes and all — the paper is found by flooding
  outwards from the middle, and the glyphs are exactly the holes in it.
- **The plate's rivets are cropped away.** They sit at two fixed heights, and a
  rivet caught in a stretched edge would be drawn as an oval whose eccentricity
  depended on how long the listing was. Putting them back — at the third points
  of the finished box, drawn rather than cut — is the obvious next step if they
  are wanted.

The two frames answer differently for the height they have to cover. The
plate's border is a pair of parallel rules, so its vertical edges are simply
stretched; a longer rule is still a rule. The slab's border is hatched, and
stretching it four times over would draw the hatching as long grey streaks, so
it is repeated instead — with every other copy upside down, so that the bottom
of one copy always meets its own mirror image and the joins cannot show. That
also fixes the number of copies to an odd one: with an even number the last
copy would end on the drawing's top edge and the join to the bottom corner
would be visible. The copies then share out the height exactly, which for the
nearest odd number is never a stretch of more than about two and usually much
less.

Horizontally there is nothing to decide: a listing is always as wide as the
text block, so the horizontal edges are only ever scaled uniformly.

## The font

None was changed. The mock-ups were made from the book's own listings, so the
face in them is already what `\ttfamily` selects here — Latin Modern Mono, with
its cursive italic for the comments (`LMMono10-Regular` and `LMMono10-Italic`
are what `pdffonts main.pdf` reports). The colours in the drawings are the
existing `coloredverbatim` style's, down to the cream background and the purple
line numbers.

## Rough edges

- **The frames do not break across a page.** `breakable=false`, because a
  nine-slice cut in half mid-page would need a fifth and sixth edge piece. Any
  listing longer than a page has to be split by hand for now.
- **The slab wastes a lot of width on the right.** Its border wanders inwards
  as far as x≈1900 of 2060, so the code has to stop well short of it; that is
  the `padr` in `slice.py`, and it costs about a tenth of the line. Narrowing
  it means redrawing the border, not changing a number.
- **The repeated chips.** The small detached rocks along the slab's edges
  repeat with the tile, which on a long listing reads as a regular pattern.
  Cutting them out of the edge pieces and scattering them by hand around the
  finished box would fix it.
- **Every number in `slice.py` was measured by eye** off a pixel grid. They are
  good enough to look at, not authored to a specification.
