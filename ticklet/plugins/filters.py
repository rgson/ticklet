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

import os
import subprocess


def git(files=None, dirs=None):
    def find_toplevel(filename):
        try:
            dirname = os.path.dirname(filename)
            p = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirname)
            repo = p.stdout.decode('utf-8').strip()
            return repo
        except:
            return None
    if files:
        repos = {find_toplevel(f) for f in files}
        dirs = (dirs or []) + [r for r in repos if r]
    return files, dirs
