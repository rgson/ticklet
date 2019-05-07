#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

# Actual help message
tmp_a=$(mktemp)
$ticklet -h >$tmp_a

# Help message in README
tmp_b=$(mktemp)
sed '/## Usage/,/## Installation/!d' README.md |
	sed '/```/,/```/!d' | sed '1d;$d' >$tmp_b

# Must match
diff $tmp_a $tmp_b
