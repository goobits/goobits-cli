#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTHONPATH=src python3 -m goobits_cli.main build >/dev/null

if ! git diff --quiet; then
  echo "Generated artifacts are out of date."
  echo "Run 'PYTHONPATH=src python3 -m goobits_cli.main build' and commit the resulting changes."
  git status --short
  exit 1
fi

echo "Generated artifacts are up to date."
