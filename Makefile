#!/usr/bin/make -f

srcs := $(shell find ticklet/ -name '*.py')

.PHONY: all
all: clean test sdist bdist deb

.PHONY: clean
clean: clean-debian/changelog
	dpkg-buildpackage -rfakeroot -Tclean
	python3 setup.py clean
	rm -rf build dist *.egg-info
	rm ticklet/VERSION

.PHONY: test
test:
	@for test in tests/*; do ./"$$test" || exit $$?; done

.PHONY: sdist
sdist: setup.py $(srcs) ticklet/VERSION
	python3 setup.py sdist

.PHONY: bdist
bdist: setup.py $(srcs) ticklet/VERSION
	python3 setup.py bdist

.PHONY: deb
deb: debian/changelog $(srcs) ticklet/VERSION
	debuild -us -uc -I -I'.vagrant' -I'*.egg-info' -I'dist'

.PHONY: debian/changelog
debian/changelog: clean-debian/changelog
	gbp dch -a --debian-tag 'v%(version)s' -N $$(./setup.py -V) --urgency low \
		--ignore-branch

.PHONY: clean-debian/changelog
clean-debian/changelog:
	sed -ri '/UNRELEASED/d; /^ticklet ([\d.]*)/,$$!d' debian/changelog

ticklet/VERSION: setup.py
	python3 setup.py --version >$@
