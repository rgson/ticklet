#!/usr/bin/env bash

me=$(basename $0)
fail() { echo "$me: fail: $1" >&2; exit 1; }
ticklet=${1:-'./ticklet.py'}

diff \
	<($ticklet -h) \
	<(sed '/## Usage/,/## Installation/!d' README.md |
		sed '/```/,/```/!d' | sed '1d;$d') \
	|| fail 'Outdated usage instructions in README'
