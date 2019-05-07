#!/usr/bin/env bash
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

# Set up profile
profile_dir=~/.config/ticklet/profiles/xyz
mkdir -p $profile_dir/openers
cat >$profile_dir/config.yaml <<YAML
display_grid: yes
YAML
expected=$(tr -dc 'a-z' </dev/urandom | head -c 10)
cat >$profile_dir/openers/00-default.sh <<SH
#!/bin/sh
echo "$expected"
SH
chmod +x $profile_dir/openers/00-default.sh

# Opener
! $ticklet foo | grep "$expected"
$ticklet -p xyz foo | grep "$expected"

# Config
! $ticklet -l | grep '^+--' >/dev/null
$ticklet -p xyz -l | grep '^+--' >/dev/null
