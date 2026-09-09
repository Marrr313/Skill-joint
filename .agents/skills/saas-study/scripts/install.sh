#!/usr/bin/env bash
# Create a virtualenv for the saas-study Python dependencies.
#
# Usage:
#   bash scripts/install.sh [venv-path]
#
# Default venv path is ./.venv in the current working directory.
# Everything here is optional convenience: if you already have trafilatura,
# beautifulsoup4, lxml and jinja2 available, just run the scripts with that
# interpreter instead.
set -euo pipefail

VENV="${1:-$PWD/.venv}"
REQ="$(cd "$(dirname "$0")" && pwd)/requirements.txt"

if [ ! -d "$VENV" ]; then
  echo "Creating venv at $VENV"
  python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install --upgrade pip >/dev/null
"$VENV/bin/pip" install -r "$REQ"

echo
echo "saas-study environment ready at $VENV"
echo "  Interpreter: $VENV/bin/python3"
echo "  Run scripts with: $VENV/bin/python3 <path-to-skill>/scripts/<script>.py"
echo
echo "Optional (screenshot redaction via --redact):"
echo "  $VENV/bin/pip install pillow pytesseract   # plus a system 'tesseract' binary"
