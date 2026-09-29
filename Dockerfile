# Build environment for the book, used by the release workflows in .github/workflows.
#
#   docker build --target export --output type=local,dest=out .   # -> out/main.pdf, out/error_codes.pdf, out/examples.zip
#
# Same distribution as the authors' machines (TeX Live 2025), so a build that passes locally
# passes here. `check-listings` is not run: it needs the reference gyc, see CLAUDE.md.

FROM ubuntu:26.04 AS base

ARG DEBIAN_FRONTEND=noninteractive
ARG TWEMOJI_VERSION=15.1.0

# texlive-fonts-extra: fontawesome5 (awesomebox); texlive-science: siunitx;
# texlive-plain-generic: ulem. The font packages back the \setmainfont/\newfontfamily
# declarations of special_header.tex, and Noto Color Emoji is what the emoji package picks.
RUN apt-get update && apt-get install -y --no-install-recommends \
        make rsync python3 ca-certificates curl fontconfig \
        texlive-luatex texlive-latex-base texlive-latex-recommended texlive-latex-extra \
        texlive-pictures texlive-fonts-extra texlive-science texlive-plain-generic \
        lmodern tex-gyre fonts-texgyre fonts-dejavu-core \
        fonts-ipafont-mincho fonts-noto-cjk fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Twitter Color Emoji (\emojiF) is not packaged by Ubuntu; fontspec fails without it.
RUN curl -fsSL "https://github.com/13rac1/twemoji-color-font/releases/download/v${TWEMOJI_VERSION}/TwitterColorEmoji-SVGinOT-Linux-${TWEMOJI_VERSION}.tar.gz" \
        | tar -xz -C /tmp \
    && install -D -m 644 /tmp/TwitterColorEmoji-SVGinOT-Linux-${TWEMOJI_VERSION}/TwitterColorEmoji-SVGinOT.ttf \
        /usr/local/share/fonts/TwitterColorEmoji-SVGinOT.ttf \
    && rm -rf /tmp/TwitterColorEmoji-SVGinOT-Linux-* \
    && fc-cache -f \
    && luaotfload-tool --update

FROM base AS build

WORKDIR /book
COPY . .

# lualatex is interactive by default: with no stdin an error ends the run instead of hanging.
# Each build starts from a fresh .build/, so a log is checked before the next build.
RUN missing_glyphs () { \
      missing="$(grep -c 'Missing character' ".build/$1.log" || true)"; \
      if [ "$missing" != "0" ]; then \
        grep 'Missing character' ".build/$1.log" | sort | uniq -c; \
        echo "error: ${missing} missing glyphs in $1.pdf, see above" >&2; return 1; \
      fi; }; \
    make check-refs \
    && make refs </dev/null && missing_glyphs main \
    && make error-codes </dev/null && missing_glyphs error_codes \
    && make examples

FROM scratch AS export
COPY --from=build /book/main.pdf /main.pdf
COPY --from=build /book/error_codes.pdf /error_codes.pdf
COPY --from=build /book/examples.zip /examples.zip
