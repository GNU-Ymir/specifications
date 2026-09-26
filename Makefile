# Versions of the tools the book documents, typeset through \gycversion and
# \gyllirversion. Override on the command line, e.g. `make refs GYC_VERSION=1.3`.
GYC_VERSION ?= 1.8.0
GYLLIR_VERSION ?= 1.8.0

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
	printf '%s\n' '\newcommand{\gycversion}{$(GYC_VERSION)}' \
		'\newcommand{\gyllirversion}{$(GYLLIR_VERSION)}' > .build/versions.tex

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
