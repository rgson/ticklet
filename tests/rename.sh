#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet foo bar

# Rename
$ticklet -r foo baz
test ! -d ~/tickets/active/foo
test -d ~/tickets/active/baz

# Attempt to rename to existing ID
! $ticklet -r bar baz
test -d ~/tickets/active/bar
