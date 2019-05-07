#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet foo
test -d ~/tickets/active/foo
test -f ~/tickets/active/foo/notes.md
