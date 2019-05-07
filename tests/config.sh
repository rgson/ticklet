#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

conf=~/.config/ticklet/config.yaml

$ticklet foo

# Touch config on first run
test -f $conf

# Grid display
! $ticklet -l | grep '^+--' >/dev/null
echo 'display_grid: yes' >$conf
$ticklet -l | grep '^+--' >/dev/null

# Directories
active_dir=$(mktemp -d)
archive_dir=$(mktemp -d)
cat >$conf <<YAML
directory_active: $active_dir
directory_archive: $archive_dir
YAML
$ticklet foo
test -d $active_dir/foo
$ticklet -a foo
test -d $archive_dir/foo
