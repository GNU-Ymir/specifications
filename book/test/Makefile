PIECES := $(wildcard assets/*.png)

all: test.pdf

## Recut the frames from the drawings in ~/notes/icons.
assets: assets/frames.tex

assets/frames.tex: slice.py
	python3 slice.py > /dev/null

test.pdf: test.tex ymirframe.sty assets/frames.tex
	lualatex -interaction=nonstopmode -halt-on-error test.tex

clean:
	rm -rf test.aux test.log test.out test.pdf test.listing test.maf test.mtc* __pycache__

## Also throws away the cut pieces; `make assets' puts them back.
distclean: clean
	rm -f assets/*.png assets/frames.tex

.PHONY: all assets clean distclean
