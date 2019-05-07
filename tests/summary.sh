#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

expected=$(tr -dc 'a-z' </dev/urandom | head -c 10)

$ticklet foo

# Before
! $ticklet -l | grep "$expected"
! grep "$expected" ~/tickets/active/foo/notes.md

$ticklet -m "$expected" foo

# After
$ticklet -l | grep "$expected"
grep "$expected" ~/tickets/active/foo/notes.md
