#!/usr/bin/env python3

import os
import setuptools
import shutil
import subprocess
import sys


# Version
try:
    p = subprocess.Popen(['git', 'describe',
        '--tags', '--always', '--dirty', '--match', r'v[0-9]*\.[0-9]*\.[0-9]*'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    v, *dev = p.stdout.readlines()[0].strip().decode('utf-8')[1:].split('-')
    formats = ['{}', '{}.dev0+{}', '{}.dev{}+{}', '{}.dev{}+{}.{}']
    version = formats[len(dev)].format(v, *dev)
except:
    print('Error: failed to find version', file=sys.stderr)
    sys.exit(1)


# Dependencies
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


# Scripts
scripts = []
rename_scripts = {'ticklet.py': 'ticklet'}
build_bin = 'build/_bin'
os.makedirs(build_bin, exist_ok=True)
for old, new in rename_scripts.items():
    scripts.append(os.path.join(build_bin, new))
    shutil.copyfile(old, scripts[-1])


setuptools.setup(
    name='ticklet',
    version=version,
    description='A command-line tool for ticket management (the bug tracker kind)',
    license='GPLv3+',
    author='Robin Gustafsson',
    author_email='robin@rgson.se',
    keywords=['ticket', 'notes', 'cli'],
    url='https://github.com/rgson/ticket-tool',
    download_url='https://github.com/rgson/ticklet/tarball/' + version,
    scripts=scripts,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Documentation',
        'Topic :: Utilities',
    ]
)
