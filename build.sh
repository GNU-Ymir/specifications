find src -name "*.org" -exec sh -c '
  src="$1"
  dst="doc/${src#src/}"
  dst="${dst%.org}.md"
  mkdir -p "$(dirname "$dst")"
  pandoc -f org -t gfm "$src" -o "$dst"
' _ {} \;

