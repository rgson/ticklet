# (c) 2018, Robin Gustafsson <robin@rgson.se>
#
# This file is part of Ticklet.
#
# Ticklet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ticklet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ticklet.  If not, see <http://www.gnu.org/licenses/>.

import pkg_resources
import sys

from ..config import config


def run_filters(files=None, dirs=None):
    for n in config['plugins.filters']:
        for e in pkg_resources.iter_entry_points('ticklet.plugins.filters', n):
            try:
                files, dirs = e.load()(files, dirs)
            except Exception as ex:
                print("Failed to run filter '{}': {}".format(n, ex),
                    file=sys.stderr)
    return files, dirs

def run_openers(files=None, dirs=None):
    for n in config['plugins.openers']:
        for e in pkg_resources.iter_entry_points('ticklet.plugins.openers', n):
            try:
                e.load()(files, dirs)
            except Exception as ex:
                print("Failed to run opener '{}': {}".format(n, ex),
                    file=sys.stderr)
