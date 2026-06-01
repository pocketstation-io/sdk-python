#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Building pocketstation distribution..."
python -m build "$REPO_ROOT"

if [ "$DRY_RUN" = true ]; then
  echo "Dry-run: checking distribution with twine..."
  python -m twine check "$REPO_ROOT/dist/"*
  echo "Dry-run complete. No package was uploaded."
else
  echo "Uploading pocketstation to PyPI..."
  python -m twine upload "$REPO_ROOT/dist/"*
  echo "Uploaded successfully."
fi
