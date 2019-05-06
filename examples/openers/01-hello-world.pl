#!/usr/bin/env perl
#
# Implements the 'Hello World' opener in Perl.
# Openers are just general executables of any kind.
#

use feature 'say';

say 'Hello World!';
say "- $_" for @ARGV;
