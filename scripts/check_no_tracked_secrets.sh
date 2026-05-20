#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository."
  exit 1
fi

if [ -z "$(git ls-files)" ]; then
  echo "No tracked files to scan."
  exit 0
fi

if git grep --cached -n -E "(Onefiancalocaticia@|On3fi|177\\.7\\.39\\.70)" -- \
  ':!scripts/check_no_tracked_secrets.sh'; then
  echo "Potential tracked secret found."
  exit 1
fi

echo "No tracked secret patterns found."
