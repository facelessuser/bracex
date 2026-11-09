#!/usr/bin/env bash

set -e

# Bash 5.3 changed how brace groups that look like sequences are validated (invalid candidates are skipped
# and later braces are still expanded), so results differ from 5.2 and earlier. Generate against 5.3 only.
if [[ "${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]}" != "5.3" ]]; then
  echo "this script requires bash 5.3" >&2
  exit 1
fi

CDPATH= cd "$(dirname "$0")"

cat brace-cases.txt | \
  while read case; do
    if [ "${case:0:1}" = "#" ]; then
      continue;
    fi;
    # The case is evaluated as an argument so it can end with a backslash, which would otherwise escape what follows.
    b="$($BASH -c 'eval "set -- $1"; for c in "$@"; do echo "[$c]"; done' _ "$case")"
    echo "$case"
    echo -n "$b><><><><";
  done > brace-results.txt
