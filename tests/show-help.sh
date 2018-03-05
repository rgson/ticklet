#!/usr/bin/env bash

me=$(basename $0)
fail() { echo "$me: fail: $1" >&2; exit 1; }
ticklet='/usr/bin/env python3 -m ticklet'

$ticklet -h >/dev/null || fail 'Cannot show help message'
