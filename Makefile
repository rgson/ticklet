#!/usr/bin/make -f

SHELL := /bin/sh

prefix      := /usr/local
exec_prefix := $(prefix)
bindir      := $(exec_prefix)/bin
datarootdir := $(prefix)/share
mandir      := $(datarootdir)/man
man1dir     := $(mandir)/man1
man1ext     := .1

srcdir := .
outdir := build

ifeq (,$(wildcard VERSION))
version := $(shell git describe --tags --always \
	--match 'v[0-9]*\.[0-9]*\.[0-9]*' | tail -c +2)
else
version := $(shell cat VERSION)
endif

.SUFFIXES:
.DELETE_ON_ERROR:

################################################################################

.PHONY: all
all: $(outdir)/ticklet $(outdir)/man/ticklet$(man1ext)

$(outdir)/ticklet: $(srcdir)/ticklet.py
	mkdir -p $(dir $@)
	cp $^ $@
	sed -i "s,^\(__version__ *= *\)'.*'$$,\1'$(version)'," $@
	chmod +x $@

$(outdir)/man/ticklet$(man1ext): $(outdir)/ticklet $(srcdir)/man/ticklet.h2m
	mkdir -p $(dir $@)
	help2man -i $(word 2,$^) -o $@ $<
	sed -ni '1,/usage:/{/usage:/!p}; /arguments:/,$$p' $@

################################################################################

.PHONY: install
install: $(DESTDIR)$(bindir)/ticklet \
         $(DESTDIR)$(man1dir)/ticklet$(man1ext)

$(DESTDIR)$(bindir)/ticklet: $(outdir)/ticklet
	mkdir -p $(dir $@)
	install -m 0755 $^ $@

$(DESTDIR)$(man1dir)/%$(man1ext): $(outdir)/man/%$(man1ext)
	mkdir -p $(dir $@)
	install -m 0644 $^ $@

################################################################################

.PHONY: uninstall
uninstall:
	rm $(DESTDIR)$(bindir)/ticklet
	rm $(DESTDIR)$(man1dir)/ticklet$(man1ext)

################################################################################

.PHONY: clean
clean:
	rm -rf $(outdir)

################################################################################

.PHONY: check
check:
	@for test in tests/*; do \
		echo "=== $$test" ;\
		./$$test || exit $$? ;\
	done

################################################################################

.PHONY: installcheck
installcheck:
	@for test in tests/*; do \
		echo "=== $$test" ;\
		./$$test $(DESTDIR)$(bindir)/ticklet || exit $$? ;\
	done

################################################################################

.PHONY: dist
dist: VERSION
	tar cvzf ../ticklet_$(version).tar.gz \
		--exclude-vcs \
		--exclude-vcs-ignores \
		--exclude $(outdir) \
		--exclude debian \
		--exclude .travis.yml \
		--transform 's|^.|ticklet|' \
		.

.INTERMEDIATE: VERSION
VERSION:
	echo $(version) >$@

################################################################################
