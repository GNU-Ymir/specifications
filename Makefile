main: build
	cd .build ; lualatex main
	cp .build/main.pdf .

refs: build
	cd .build ; lualatex main
	# cd .build ; bibtex main
	# cd .build ; bibtex main
	cd .build ; lualatex main
	cd .build ; lualatex main
	cp .build/main.pdf .

build:
	rm -rf ./.build
	mkdir -p ./.build
	rsync -av --exclude='.build' ./* .build/

clean:
	rm -rf .build

# Consistency checks over the sources; see BOOK_AUDIT.md.
# GYC overrides the reference compiler, e.g. `make check GYC=/path/to/gyc`.
check: check-refs check-listings

check-refs:
	python3 tools/check_refs.py

check-listings:
	python3 tools/check_listings.py $(if $(GYC),--compiler $(GYC),)

.PHONY: main refs build clean check check-refs check-listings
