#!/usr/bin/make -f

SHELL := /bin/sh

srcdir := .

prefix      := /usr/local
exec_prefix := $(prefix)
bindir      := $(exec_prefix)/bin
libdir      := $(exec_prefix)/lib

plugins := $(shell find $(srcdir)/plugins/ -name '*.py' -printf '%f\n')
outdir  := build

version = $$(git describe --tags --always --dirty \
	--match 'v[0-9]*\.[0-9]*\.[0-9]*' | tail -c +2)

.SUFFIXES:

.PHONY: all
all: clean test-src build test

.PHONY: rebuild
rebuild: clean build

.PHONY: clean
clean:
	rm -rf $(outdir)

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

.PHONY: install
install: $(DESTDIR)$(bindir)/ticklet \
         $(addprefix $(DESTDIR)$(libdir)/ticklet/plugins/, $(plugins))

$(DESTDIR)$(bindir)/ticklet: $(outdir)/ticklet
	@mkdir -p $(dir $@)
	install -m 0755 $^ $@

$(DESTDIR)$(libdir)/ticklet/plugins/%.py: $(outdir)/plugins/%.py
	@mkdir -p $(dir $@)
	install -m 0644 $^ $@

.PHONY: tar
tar:
	d=$$(basename $$(pwd)) ;\
	v=$(version) ;\
	t=$$(mktemp) ;\
	git ls-files | sed -e '/^.gitignore$$/d' -e '/^.travis.yml$$/d' \
		-e "s,.*,$$d/&," >$$t ;\
	cd .. && tar cfz $$d/ticklet_$$v.tar.gz -T $$t ;\
	rm $$t
