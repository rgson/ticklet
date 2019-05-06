#!/bin/zsh
#
# Opens Git repository root directories in Gnome Terminal
#

for file in $@; do echo $file; done |
	xargs -r -n1 dirname |
	xargs -r -n1 -I {} git -C {} rev-parse --show-toplevel 2>/dev/null |
	sort | uniq |
	sed 's/^/--tab --working-directory /' |
	xargs -r gnome-terminal
