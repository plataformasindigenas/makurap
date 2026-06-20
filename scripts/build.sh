#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
echo "=== Makurap Build ==="
echo ""
# Regenerate source data from the BILingo deck + sibling-platform photos
python3 scripts/prepare_dictionary.py
python3 scripts/prepare_fauna_flora.py
echo ""
# terradoc build writes into docs/ but does not create it; ensure it exists so a
# fresh checkout (docs/ is git-ignored) builds cleanly on CI / Cloudflare Pages.
mkdir -p docs/fonts docs/images docs/videos
terradoc build --config terradoc.yaml
echo ""
# Stage self-hosted media (source of truth: media/). These are committed so the
# build is self-contained and does not need the sibling repos at deploy time.
mkdir -p docs/videos docs/images
cp -f media/videos/*.mp4 docs/videos/ 2>/dev/null && \
  echo "  Staged $(ls media/videos/*.mp4 | wc -l) videos to docs/videos/"
cp -f media/images/*.jpg docs/images/ 2>/dev/null && \
  echo "  Staged $(ls media/images/*.jpg | wc -l) reused photos to docs/images/"
cp -f media/images/*.svg docs/images/ 2>/dev/null && \
  echo "  Staged logo/favicon to docs/images/"
echo ""
echo "Open docs/index.html in your browser to preview the site."
