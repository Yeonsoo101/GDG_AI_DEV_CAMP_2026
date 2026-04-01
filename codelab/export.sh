#!/usr/bin/env bash
set -euo pipefail
export PATH=$PATH:$(go env GOPATH)/bin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CODELAB_DIR="$SCRIPT_DIR/content-creation-studio-adk"

cd "$SCRIPT_DIR"
claat export codelab.md

python3 "$SCRIPT_DIR/scripts/inject_about.py" "$CODELAB_DIR/index.html"

# Copy to root /docs — GitHub Pages serves from there
ROOT_DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"
mkdir -p "$ROOT_DOCS_DIR"
cp -r "$CODELAB_DIR/." "$ROOT_DOCS_DIR/"

echo "✅ Export complete → $ROOT_DOCS_DIR"
