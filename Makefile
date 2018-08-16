#!/usr/bin/make -f

SHELL := /bin/sh

srcdir := .

prefix      := /usr/local
exec_prefix := $(prefix)
bindir      := $(exec_prefix)/bin
libdir      := $(exec_prefix)/lib
datarootdir := $(prefix)/share
mandir      := $(datarootdir)/man
man1dir     := $(mandir)/man1
man1ext     := .1

plugins := $(shell find $(srcdir)/plugins/ -name '*.py' -printf '%f\n')
outdir  := build

has_git := $(shell which git >/dev/null && git rev-parse 2>/dev/null \
	&& echo true || echo false)

ifeq ($(has_git), true)
version := $(shell git describe --tags --always \
	--match 'v[0-9]*\.[0-9]*\.[0-9]*' | tail -c +2)
else
version := $(shell cat VERSION)
endif

.SUFFIXES:

.PHONY: all
all: build

.PHONY: rebuild
rebuild: clean build

.PHONY: clean
clean:
	rm -rf $(outdir)
	if $(has_git); then rm -f VERSION; fi
	if which dh_clean >/dev/null && [ -d debian ]; then dh_clean; fi

.PHONY: build
build: $(outdir)/ticklet $(addprefix $(outdir)/plugins/, $(plugins))

$(outdir)/plugins/%.py: $(srcdir)/plugins/%.py
	@mkdir -p $(dir $@)
	cp $< $@

$(outdir)/ticklet: $(srcdir)/ticklet.py
	@mkdir -p $(dir $@)
	cp $^ $@
	sed -i "s,^\(__version__ *= *\)'.*'$$,\1'$(version)'," $@
	sed -i "s,^\(LIBDIR *= *\)'.*'$$,\1'$(libdir)'," $@
	chmod +x $@

.PHONY: test
test: $(outdir)/ticklet
	for test in tests/*; do ./$$test $^ || exit $$?; done

.PHONY: test-src
test-src:
	for test in tests/*; do ./$$test || exit $$?; done

.PHONY: man
man: $(outdir)/man/ticklet$(man1ext)

$(outdir)/man/ticklet$(man1ext): $(outdir)/ticklet $(srcdir)/man/ticklet.h2m
	@mkdir -p $(dir $@)
	help2man -i $(word 2,$^) -o $@ $<
	sed -ni '1,/usage:/{/usage:/!p}; /arguments:/,$$p' $@

.PHONY: install
install: $(DESTDIR)$(bindir)/ticklet \
         $(addprefix $(DESTDIR)$(libdir)/ticklet/plugins/, $(plugins)) \
         $(DESTDIR)$(man1dir)/ticklet$(man1ext)

$(DESTDIR)$(bindir)/ticklet: $(outdir)/ticklet
	@mkdir -p $(dir $@)
	install -m 0755 $^ $@

$(DESTDIR)$(libdir)/ticklet/plugins/%.py: $(outdir)/plugins/%.py
	@mkdir -p $(dir $@)
	install -m 0644 $^ $@

$(DESTDIR)$(man1dir)/%$(man1ext): $(outdir)/man/%$(man1ext)
	@mkdir -p $(dir $@)
	install -m 0644 $^ $@

.PHONY: tar
tar: VERSION
	set -e ;\
	d=$$(basename $$(pwd)) ;\
	t=$$(mktemp) ;\
	git ls-files | sed -e '/^.gitignore$$/d' -e '/^.travis.yml$$/d' \
		-e '\,^debian/,d' -e "s,.*,$$d/&," >$$t ;\
	echo $$d/VERSION >>$$t ;\
	cd .. && tar cfz $$d/ticklet_$(version).tar.gz -T $$t ;\
	rm $$t

.PHONY: VERSION
VERSION:
	echo $(version) >$@

.PHONY: deb
deb: tar build debian/changelog
	mv ticklet_*.tar.gz ../$$(basename ticklet_*.tar.gz .tar.gz).orig.tar.gz
	debuild -us -uc

.PHONY: debian/changelog
debian/changelog: $(outdir)/ticklet
	sed -i '/UNRELEASED/d; /^ticklet/,$$!d' debian/changelog
	if ! grep -q $(version)-1 $@; then \
		gbp dch -a --debian-tag='v%(version)s' -N $(version)-1 \
			--urgency low --ignore-branch || exit $$? ;\
	fi
