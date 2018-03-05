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
import textwrap


class Config:

    def __init__(self, config_values):
        self.config_values = config_values

    def __getitem__(self, key):
        v = self.config_values
        for part in key.split('.'):
            v = v[part]
        return v

    def __setitem__(self, key, value):
        v = self.config_values
        parts = key.split('.')
        for part in parts[:-1]:
            v = v[part]
        v[key] = value

    def update(self, changed_values):
        def merge_dicts(a, b):
            for k in b:
                if k in a and isinstance(a[k], dict) and isinstance(b[k], dict):
                    merge_dicts(a[k], b[k])
                else:
                    a[k] = b[k]
        merge_dicts(self.config_values, changed_values)


config = Config({
    'directory': {
        'active': os.path.expanduser('~/tickets/active'),
        'archive': os.path.expanduser('~/tickets/archive'),
    },
    'template': textwrap.dedent("""\
        # Ticket {id}

        _Summary_:
        _Status_ : New


        ## Files

        -


        ## Notes

        """),
})
