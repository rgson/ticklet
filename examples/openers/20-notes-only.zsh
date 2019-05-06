#!/bin/zsh
#
# Opens the notes file in an editor (on Debian, at least)
#

sensible-editor ${@[(r)*/notes.md]}
