#!/usr/bin/env bash

set -e

# Bash 4.3 - 4.4 because of arbitrary need to pick a single standard.

if [ "${BASH_VERSINFO[0]}" != "4" ] || ( [ "${BASH_VERSINFO[1]}" != "3" ] &&  [ "${BASH_VERSINFO[1]}" != "4" ] ) ; then
  echo "this script requires bash 4.3 or 4.4" >&2
  exit 1
fi

CDPATH= cd "$(dirname "$0")"

cat brace-cases.txt | \
  while read case; do
    if [ "${case:0:1}" = "#" ]; then
      continue;
    fi;
    b="$($BASH -c 'for c in '"$case"'; do echo "[$c]"; done')"
    echo "$case"
    echo -n "$b><><><><";
  done > brace-results.txt
