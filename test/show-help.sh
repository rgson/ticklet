#!/usr/bin/env bash

fail() { echo "Fail: $1" >&2; exit 1; }

"${1:-.}/ticklet.py" -h >/dev/null || fail 'Cannot show help message'
