#!/usr/bin/env python3
"""Cut the two frame drawings into nine-slice pieces.

A code listing is as tall as the code inside it, so a frame drawn once at one
size cannot simply be scaled: scaling it to a taller box would make the border
thicker at the same time.  The classic answer is the nine-slice (or "nine-patch"):
the drawing is cut into four corners, four edges and a centre.  The corners are
drawn at a fixed size, the edges are repeated or stretched along the one axis
they run in, and the centre is a flat fill.

This script produces the eight border pieces of that grid for each frame, plus
`assets/frames.tex', which tells the LaTeX side how big each piece is *relative
to the width of the frame* -- every length in the frame art scales with the
width of the text block, and only the middle bands stretch with the height.

Everything outside the frame is made transparent, so a framed listing can sit
on the tinted pages of part II without carrying a white halo around with it.

Run `make frames' from the book directory after changing any
of the numbers below.
"""

import json
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "frames")

#% ---------------------------------------------------------------------------
#% Frame definitions.  All coordinates are pixels in the *source* image, with
#% the origin at its top left corner.
#%
#%   crop    the frame proper, white page margins removed
#%   slice   how much of the cropped drawing each corner keeps, (l, r, t, b)
#%   pad     the padding between the outer edge of the frame and the code,
#%           (l, r, t, b).  The top padding also has to clear the badge, which
#%           hangs above the first line of code without occupying any height.
#%   mode    what the two vertical edges do when the listing is not the height
#%           the drawing was made at.  `stretch' pulls the middle of the
#%           drawing to fit -- right for a border that is a plain rule, wrong
#%           for one whose hatching would smear into streaks.  `tile' repeats
#%           it instead; see the mirroring below for how the repeats join.
#%
#% The edges themselves are not sampled from anywhere in particular: each one
#% is the whole of the drawing between the two corners it runs between.  A
#% listing is always as wide as the text block, so the horizontal edges are
#% only ever scaled uniformly and cannot distort at all; it is the height that
#% varies, and only the two vertical edges have to answer for it.
#% ---------------------------------------------------------------------------

FRAMES = {
    "broken": {
        "src": os.path.expanduser("~/notes/icons/text broken.png"),
        "crop": (60, 140, 2120, 608),
        "slice": (140, 220, 115, 120),
        "pad": (115, 235, 165, 115),
        "mode": "tile",
    },
    "plate": {
        # The two rivets on either side sit outside the plate; the crop drops
        # them, because a rivet caught in a stretched edge would be drawn as an
        # oval whose eccentricity depended on how long the listing was.
        "src": os.path.expanduser("~/notes/icons/text_solid.png"),
        "crop": (50, 145, 2060, 600),
        "slice": (78, 78, 78, 78),
        "pad": (72, 72, 80, 48),
        "mode": "stretch",
    },
}

#% ---------------------------------------------------------------------------
#% Tinted plates.
#%
#% The book says what language a listing is in twice over: with the colour
#% behind the code, and -- for a black and white print, and for a reader who
#% cannot tell the colours apart -- with the badge in its corner.  Framing every
#% listing on the same cream plate would have thrown the first of the two away,
#% so the plate is also cut in the three other tints, matching the colours the
#% unframed listings used.
#%
#% The recolouring is a multiply: each pixel is scaled by target/paper.  The
#% paper becomes the target exactly, and the ink, being near zero to begin with,
#% stays as dark as it was rather than being washed towards the tint.
#% ---------------------------------------------------------------------------

TINTS = {
    "plateteal": ("plate", (230, 242, 242)),    # teal!10,  M-YIL
    "plateolive": ("plate", (242, 242, 230)),   # olive!10, L-YIL
    "plategray": ("plate", (242, 242, 242)),    # gray!10,  shell transcripts
}


def cut_out_page(im):
    """Return `im' with the page it was drawn on made transparent.

    The transparent region is grown from the corners of the image rather than
    selected by colour, so that the cream of the listing's own background --
    which is close enough to white to be caught by any colour threshold loose
    enough to catch the page -- is left alone.
    """
    rgb = np.array(im.convert("RGB")).astype(np.int16)
    h, w, _ = rgb.shape

    # Flood the page from all four corners.  PIL's flood fill works on an
    # image, so the mask is built by filling a copy with a colour that cannot
    # occur in the drawing and then testing for it.
    probe = im.convert("RGB").copy()
    from PIL import ImageDraw

    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(probe, seed, (255, 0, 255), thresh=6)
    outside = np.all(np.array(probe) == (255, 0, 255), axis=2)

    alpha = np.where(outside, 0, 255).astype(np.uint8)

    # The pencil lines are anti-aliased, so the two or three pixels between the
    # flooded page and the line proper are a pale grey that the flood did not
    # reach.  Left opaque they would draw a light halo around the frame on a
    # tinted page.  They are faded out in proportion to how dark they are.
    grown = Image.fromarray((outside * 255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(7))
    fringe = (np.array(grown) > 0) & ~outside
    lum = rgb.mean(axis=2)
    soft = np.clip((250.0 - lum) / 20.0, 0.0, 1.0)
    alpha[fringe] = (soft[fringe] * 255).astype(np.uint8)

    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    return out


def blank_interior(frame, flat):
    """Paint out the code the frame was drawn around.

    The drawings are mock-ups: they were made by putting a border round a real
    listing, so every piece cut from them still carries a piece of `let dmut a'
    and of the line numbers.  Those have to go, or they would be printed as
    ghosts behind whatever code the frame is actually wrapped around.

    What is erased is the region enclosed by the border, holes and all: the
    paper inside the frame is found by flooding outwards from the middle, and
    the glyphs sitting on it are exactly the holes in the region so found.  The
    border art itself is never part of that region, so its soft inner edge
    survives untouched.
    """
    from PIL import ImageDraw

    w, h = frame.size
    rgba = np.array(frame)

    #% Flooding works on colours, so the transparent page is first painted a
    #% colour that occurs nowhere in the drawing: it then stops the flood as
    #% surely as an ink line would, should the border have a gap in it.
    #% `.copy()' throughout: an image built by `Image.fromarray' wraps the
    #% array's buffer read-only, and a flood fill into one silently does
    #% nothing at all.
    probe = Image.fromarray(np.where(rgba[..., 3:4] < 128,
                                     np.array([255, 0, 255], np.uint8),
                                     rgba[..., :3]).astype(np.uint8),
                            "RGB").copy()
    ImageDraw.floodfill(probe, (w // 2, h // 2), (0, 255, 0), thresh=45)
    paper = np.all(np.array(probe) == (0, 255, 0), axis=2)

    #% Holes: everything not paper, flooded from the edge of the image.  What
    #% that flood cannot reach is enclosed by paper -- the glyphs.
    hole_probe = Image.fromarray((paper * 255).astype(np.uint8), "L").copy()
    ImageDraw.floodfill(hole_probe, (0, 0), 128)
    for seed in ((w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(hole_probe, seed, 128)
    enclosed = np.array(hole_probe) == 0

    fill = paper | enclosed
    rgba[fill] = (*flat, 255)
    return Image.fromarray(rgba, "RGBA")


def interior_colour(rgb, crop, slice_):
    """The flat colour used for the centre of the grid.

    Sampled from the drawing itself rather than taken from the book's
    `background!40', so that the join between the stretched edges and the flat
    centre is invisible.
    """
    x0, y0, x1, y1 = crop
    l, r, t, b = slice_
    patch = rgb[y0 + t + 20:y1 - b - 20, x0 + l + 20:x1 - r - 20]
    #% The listing carries text and coloured line numbers, so the mean would be
    #% dragged grey; the mode of each channel is the paper.
    return tuple(int(np.bincount(patch[..., c].ravel(), minlength=256).argmax())
                 for c in range(3))


def retint(frame, paper, target):
    """The same drawing on tinted paper.  See TINTS above."""
    rgba = np.array(frame).astype(np.float64)
    scale = np.array(target, np.float64) / np.array(paper, np.float64)
    rgba[..., :3] = np.clip(rgba[..., :3] * scale, 0, 255)
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def emit(name, spec, frame=None, flat=None):
    if frame is None:
        src = Image.open(spec["src"])
        rgb = np.array(src.convert("RGB")).astype(np.int16)
        flat = interior_colour(rgb, spec["crop"], spec["slice"])
        frame = blank_interior(cut_out_page(src).crop(spec["crop"]), flat)
    frame.save(os.path.join(OUT, f"{name}-whole.png"), dpi=(72, 72))
    w, h = frame.size
    l, r, t, b = spec["slice"]

    pieces = {
        "tl": (0, 0, l, t),
        "tr": (w - r, 0, w, t),
        "bl": (0, h - b, l, h),
        "br": (w - r, h - b, w, h),
        "t": (l, 0, w - r, t),
        "b": (l, h - b, w - r, h),
        "l": (0, t, l, h - b),
        "r": (w - r, t, w, h - b),
    }
    for key, box in pieces.items():
        piece = frame.crop(box)
        #% pdfTeX and LuaTeX read the pHYs chunk to work out how big a PNG is;
        #% saving at 72 dpi makes one pixel one big point, which keeps the
        #% numbers written into frames.tex meaningful.
        piece.save(os.path.join(OUT, f"{name}-{key}.png"), dpi=(72, 72))
        #% Each vertical edge is also saved upside down.  Stacking the two
        #% alternately is what lets a repeated edge join up: the bottom of one
        #% copy and the top of the next are then always the same line of the
        #% drawing, whatever the drawing happens to do there.
        if key in ("l", "r"):
            piece.transpose(Image.FLIP_TOP_BOTTOM).save(
                os.path.join(OUT, f"{name}-{key}m.png"), dpi=(72, 72))

    return {
        "w": w, "h": h,
        "slice": spec["slice"], "pad": spec["pad"], "mode": spec["mode"],
        "interior": flat, "frame": frame,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {name: emit(name, spec) for name, spec in FRAMES.items()}
    for name, (base, target) in TINTS.items():
        meta[name] = emit(name, FRAMES[base],
                          frame=retint(meta[base]["frame"],
                                       meta[base]["interior"], target),
                          flat=target)

    lines = [
        "%% Generated by tools/slice_frames.py -- do not edit.",
        "%% Every length is a fraction of the *width* of the frame, so that the",
        "%% whole drawing scales with the text block and only the middle bands",
        "%% stretch with the height of the listing.",
        "",
    ]
    for name, m in meta.items():
        w = float(m["w"])
        l, r, t, b = m["slice"]
        pl, pr, pt, pb = m["pad"]
        red, green, blue = m["interior"]
        lines += [
            f"\\definecolor{{ymirframe@{name}@interior}}{{RGB}}{{{red},{green},{blue}}}",
            f"\\def\\ymirframe@{name}@mode{{{m['mode']}}}",
        ]
        #% The shortest box the frame may be drawn round: tall enough for its
        #% own two caps, and for one line of code between the paddings.
        minh = max(t + b, pt + pb + 70)
        for key, px in (("wl", l), ("wr", r), ("ht", t), ("hb", b),
                        ("padl", pl), ("padr", pr), ("padt", pt), ("padb", pb),
                        ("minh", minh), ("bandh", m["h"] - t - b)):
            lines.append(f"\\def\\ymirframe@{name}@{key}{{{px / w:.6f}}}")
        lines.append(f"\\def\\ymirframe@{name}@aspect{{{m['h'] / w:.6f}}}")
        lines.append("")
    with open(os.path.join(OUT, "frames.tex"), "w") as fh:
        fh.write("\n".join(lines))

    for m in meta.values():
        m.pop("frame")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
