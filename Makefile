#!/usr/bin/make -f

.PHONY: all
all: clean test sdist bdist deb

.PHONY: clean
clean: clean-debian/changelog
	debuild clean
	python3 setup.py clean
	rm -rf build dist *.egg-info

.PHONY: test
test:
	@for test in test/*; do ./"$$test" || exit $$?; done

.PHONY: sdist
sdist: ticklet.py setup.py
	python3 setup.py sdist

.PHONY: bdist
bdist: ticklet.py setup.py
	python3 setup.py bdist

.PHONY: deb
deb: ticklet.py debian/changelog
	debuild -us -uc

.PHONY: debian/changelog
debian/changelog: clean-debian/changelog
	gbp dch -a --debian-tag 'v%(version)s' -N $$(./setup.py -V)-1 \
		--urgency low --ignore-branch

.PHONY: clean-debian/changelog
clean-debian/changelog:
	sed -ri '/UNRELEASED/d; /^ticklet ([\d.-]*)/,$$!d' debian/changelog
