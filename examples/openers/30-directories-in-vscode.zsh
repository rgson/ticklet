#!/bin/zsh
#
# Opens the files and their containing directories in Visual Studio Code
#

files=$(for file in $@; do echo $file; done)
directories=$(xargs <<<$files -r -n1 dirname)
xargs <<<$files <<<$directories -r code -n
