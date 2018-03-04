#!/usr/bin/env bash

fail() { echo "Fail: $1" >&2; exit 1; }

t=$(mktemp -d)
trap "{ rm -r $t; }" EXIT

d=$(realpath ${1:-.})
ln -s "$d/ticklet.py" "$t/ticklet"

diff \
	<(python3 "$t/ticklet" -h) \
	<(sed '/## Usage/,/## Installation/!d' "$d/README.md" |
		sed '/```/,/```/!d' | sed '1d;$d') \
	|| fail 'Outdated usage instructions in README'
