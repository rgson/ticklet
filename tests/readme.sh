#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

diff \
	<($ticklet -h) \
	<(sed '/## Usage/,/## Installation/!d' README.md |
		sed '/```/,/```/!d' | sed '1d;$d')
