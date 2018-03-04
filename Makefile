#!/usr/bin/make -f

.PHONY: all
all: clean test sdist bdist deb

.PHONY: clean
clean:
	debuild clean
	python3 setup.py clean
	rm -rf build dist *.egg-info

.PHONY: test
test:
	@for test in test/*; do ./"$$test"; done

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
debian/changelog:
	sed -ri '/UNRELEASED/d; /^ticklet ([\d.]*)/,$$!d' debian/changelog
	gbp dch -a --debian-tag 'v%(version)s' -N $$(./setup.py -V) --urgency low \
		--ignore-branch
