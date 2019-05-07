#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

$ticklet --version
