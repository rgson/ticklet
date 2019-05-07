#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet -h >/dev/null
