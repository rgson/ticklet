#!/bin/sh
#
# Prints 'Hello World!' and lists the files.
# Demonstrates the basics of an opener.
#

echo 'Hello World!'

for file in $@; do
	echo "- $file"
done
