#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
echo "=== Makurap Build ==="
echo ""
# data/ is SOURCE: nothing here may rewrite it (see scripts/seed/README.md).
# terradoc build writes into docs/ but does not create it; ensure it exists so a
# fresh checkout (docs/ is git-ignored) builds cleanly on CI.
mkdir -p docs
terradoc build --config terradoc.yaml
echo ""
# static/ is copied verbatim into the site root (static/images -> /images,
# static/audio -> /audio). It holds self-hosted media and is tracked in git.
cp -r static/. docs/
echo "  Copied static/ into docs/ ($(find static -type f | wc -l) files)"
echo ""
echo "Open docs/index.html in your browser to preview the site."
