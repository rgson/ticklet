#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet foo

# Archive
$ticklet -a foo
test -d ~/tickets/archive/foo
test -f ~/tickets/archive/foo/notes.md
test ! -d ~/tickets/active/foo
test ! -f ~/tickets/active/foo/notes.md

# Unarchive
$ticklet -u foo
test ! -d ~/tickets/archive/foo
test ! -f ~/tickets/archive/foo/notes.md
test -d ~/tickets/active/foo
test -f ~/tickets/active/foo/notes.md
