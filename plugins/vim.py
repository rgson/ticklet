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

import subprocess


def open_files(files, dirs):
    if not files:
        return

    file_list = [];
    for index,file in enumerate(files):
        file_list += [file];
        if index%3 == 0 or file == files[-1]:
            open_terminal(file_list);
            file_list=[];

def open_terminal(files):
    cmd = ['gnome-terminal', '--', 'vim', '-O'] + files;
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

