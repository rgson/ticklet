#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

test_list() {
	test "$($ticklet -l | wc -l)" -eq "$1"
	test "$($ticklet -k | wc -l)" -eq "$2"
}

# No tickets => no output
test_list 0 0

# Single active ticket
$ticklet foo
test_list 1 1

# Single archived ticket
$ticklet -a foo
test_list 0 1

# One of each
$ticklet bar
test_list 1 2
