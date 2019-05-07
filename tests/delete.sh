#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet foo

# Don't delete by default (no response to prompt)
echo | $ticklet -d foo
test -d ~/tickets/active/foo

# Delete ticket
echo 'y' | $ticklet -d foo
test ! -d ~/tickets/active/foo
