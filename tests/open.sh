#!/bin/sh
set -e
ticklet=${1:-'./ticklet.py'}
export HOME=$(mktemp -d)

# Set up opener
opener_dir=~/.config/ticklet/openers
mkdir -p $opener_dir
expected=$(tr -dc 'a-z' </dev/urandom | head -c 10)
cat >$opener_dir/00-default.sh <<SH
#!/bin/sh
echo "$expected"
SH
chmod +x $opener_dir/00-default.sh

# Create and open
$ticklet foo | grep "$expected"

# Open existing only
$ticklet -o foo | grep "$expected"
! $ticklet -o bar

# Open existing only, with mixed existent and non-existent
! x=$( $ticklet -o foo bar )
echo "$x" | grep "$expected"
