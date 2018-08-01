#!/usr/bin/env python3

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

__version__ = '0.0.0~unknown'

LIBDIR = '.'

import argparse
import collections
import fileinput
import glob
import operator
import os
import shutil
import subprocess
import sys
import textwrap
import yaml


class TicketNotFound(Exception):
    pass


class Ticket(collections.namedtuple('Ticket', 'id path')):

    @staticmethod
    def _path(id, directory):
        return '{}/{}'.format(directory, id)

    @classmethod
    def find(cls, id, optional=False):
        directories = (config['directory.active'], config['directory.archive'])
        paths = (cls._path(id, directory) for directory in directories)
        found = next((path for path in paths if os.path.exists(path)), None)
        if not found and not optional:
            raise TicketNotFound(id)
        return cls(id=id, path=found) if found else None

    @classmethod
    def create(cls, id):
        path = cls._path(id, config['directory.active'])
        os.makedirs(path)
        ticket = cls(id=id, path=path)
        Notes.create(ticket)
        return ticket

    def delete(self):
        shutil.rmtree(self.path)

    @classmethod
    def list(cls, include_archived=False):
        yield from cls._list_tickets_in(config['directory.active'])
        if include_archived:
            yield from cls._list_tickets_in(config['directory.archive'])

    @classmethod
    def _list_tickets_in(cls, directory):
        for d in glob.glob(directory + '/*/'):
            yield cls(id=d[len(directory)+1:-1], path=d[:-1])

    def __str__(self):
        n = Notes.read(self) or Notes(['']*4)
        return '{:10}  {:25.25}  {}'.format(self.id, n.summary, n.status)

    def archive(self):
        return self._move_ticket(config['directory.archive'])

    def unarchive(self):
        return self._move_ticket(config['directory.active'])

    def _move_ticket(self, target_dir):
        target_path = Ticket._path(self.id, target_dir)
        shutil.move(self.path, target_path)
        return Ticket(self.id, target_path)

    def open(self):
        files = [], [self.path]
        n = Notes.read(self)
        if n:
            files = [n.path] + n.files
            dirs = [os.path.dirname(filename) for filename in files]
        files, dirs = plugins.run_filters(files, dirs)
        plugins.run_openers(files, dirs)


class Notes(collections.namedtuple('Notes', 'path summary status files')):

    @staticmethod
    def _path(ticket):
        return '{}/{}'.format(ticket.path, 'notes.md')

    @classmethod
    def create(cls, ticket):
        path = Notes._path(ticket)
        with open(path, 'w') as f:
            print(config['template'].format(id=ticket.id), file=f)
        return cls(path=path, summary='', status='New', files=[])

    @classmethod
    def read(cls, ticket):
        try:
            path = Notes._path(ticket)
            summary = status = ''
            files, files_section = [], False
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('_Summary_'):
                        summary = line[line.index(':') + 1:].strip()
                    elif line.startswith('_Status_'):
                        status = line[line.index(':') + 1:].strip()
                    elif line.startswith('## Files'):
                        files_section = True
                    elif files_section and line.startswith('- '):
                        files.append(line[1:].strip())
                    elif files_section and line.startswith('## '):
                        break
            return cls(path=path, summary=summary, status=status, files=files)
        except FileNotFoundError:
            return None

    def write(self):
        files_section, files_printed = False, False
        with fileinput.FileInput(self.path, inplace=True) as f:
            for line in f:
                if line.startswith('_Status_'):
                    line = '_Status_ : {}\n'.format(self.status)
                elif line.startswith('_Summary_'):
                    line = '_Summary_: {}\n'.format(self.summary)
                elif line.startswith('## Files'):
                    files_section = True
                elif files_section and line.startswith('- '):
                    line = ''
                    if not files_printed:
                        line = '- {}\n'.format('\n- '.join(self.files))
                        files_printed = True
                elif files_section and line.startswith('## '):
                    files_section = False
                print(line, end='')


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


class PluginNotFound(Exception):
    pass


class Plugins:

    search_dirs = ['plugins', LIBDIR + '/ticklet/plugins']

    def __init__(self):
        self.plugins = {}

    def __getitem__(self, key):
        if key not in self.plugins:
            self.plugins[key] = self._load(key)
        return self.plugins[key]

    def _load(self, plugin):
        for d in Plugins.search_dirs:
            try:
                return self._load_file(plugin, '{}/{}.py'.format(d, plugin))
            except (FileNotFoundError, ImportError):
                pass
        raise PluginNotFound(plugin)

    def _load_file(self, plugin, path):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(plugin, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except (AttributeError, ImportError):
            from importlib.machinery import SourceFileLoader
            module = SourceFileLoader(plugin, path).load_module()
        return module

    def run_filters(self, files, dirs):
        for p in config['plugins.files.filter']:
            files, dirs = self[p].filter_files(files, dirs)
        return files, dirs

    def run_openers(self, files, dirs):
        openers = config['plugins.files.open']
        if not openers:
            print("You don't have any openers enabled. To open tickets,\n"
                  "add some to your configuration file ({})."
                  .format(user_config_file), file=sys.stderr)
        for p in openers:
            self[p].open_files(files, dirs)


# Initialize

plugins = Plugins()

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
    'plugins': {
        'files': {
            'filter': [],
            'open': [],
        },
    },
    'profiles': {
    },
})

# Load configuration

user_config_file = '{}/ticklet'.format(
    os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')))
try:
    with open(user_config_file) as f:
        config.update(yaml.load(f))
except FileNotFoundError:
    pass

# Parse command-line arguments

parser = argparse.ArgumentParser('ticklet')
parser.add_argument(       '--version'  , version=__version__              , action='version'           )
parser.add_argument('-l' , '--list'     , help='list active tickets'       , action='store_true'        )
parser.add_argument('-k' , '--list-all' , help='list all tickets'          , action='store_true'        )
parser.add_argument('-a' , '--archive'  , help='move tickets to archive'   , action='store_true'        )
parser.add_argument('-u' , '--unarchive', help='move tickets from archive' , action='store_true'        )
parser.add_argument('-o' , '--open'     , help='open existing tickets only', action='store_true'        )
parser.add_argument('-d' , '--delete'   , help='delete tickets'            , action='store_true'        )
parser.add_argument('-s' , '--status'   , help='set the status'                                         )
parser.add_argument('-m' , '--summary'  , help='set the summary'                                        )
parser.add_argument('-p' , '--profile'  , help='use an alternative configurations profile'              )
parser.add_argument('tickets'           , help='ticket(s) to act upon'     , nargs='*', metavar='TICKET')
args = parser.parse_args()

conflicting_arguments = [
    {'-a/--archive': args.archive, '-u/--unarchive': args.unarchive},
    {'-d/--delete' : args.delete , '-o/--open'     : args.open     },
]

for conflicts in conflicting_arguments:
    if sum(conflicts.values()) > 1:
        names = [k for k, v in conflicts.items() if v]
        print('Conflicting options:', ', '.join(names), file=sys.stderr)
        sys.exit(1)

# Load the requested config profile (if any)

if args.profile:
    try:
        config.update(config['profiles.' + args.profile])
    except:
        print('Profile not found:', args.profile, file=sys.stderr)
        sys.exit(1)

# Ensure that the ticket directories exist

for directory in config['directory'].values():
    os.makedirs(directory, exist_ok=True)

# Default to creating and opening tickets

ignore_args = {'tickets', 'profile'}
no_action = not any(v for k, v in args.__dict__.items() if k not in ignore_args)
args.create = no_action
args.open |= no_action

# Perform requested actions

if no_action and not args.tickets:
    parser.print_help()

if args.list or args.list_all:
    tickets = Ticket.list(include_archived=args.list_all)
    tickets = sorted(tickets, key=operator.attrgetter('id'))
    print('\n'.join(str(t) for t in tickets))

elif not args.tickets:
    print('No tickets specified for action', file=sys.stderr)
    sys.exit(1)

else:
    missing_tickets = False

    for ticket_id in args.tickets:
        try:
            t = Ticket.find(ticket_id)
        except TicketNotFound as e:
            if args.create:
                t = Ticket.create(ticket_id)
            else:
                print('Ticket not found:', e, file=sys.stderr)
                missing_tickets = True
                continue

        if args.status is not None:
            Notes.write(Notes.read(t)._replace(status=args.status))

        if args.summary is not None:
            Notes.write(Notes.read(t)._replace(summary=args.summary))

        if args.archive:
            t = Ticket.archive(t)
        elif args.unarchive:
            t = Ticket.unarchive(t)

        if args.open:
            Ticket.open(t)
        elif args.delete:
            prompt = 'Are you sure you want to delete {}? (y/N): '.format(t.id)
            confirm = '-'
            while confirm not in 'YyNn':
                confirm = input(prompt) or 'N'
            if confirm in 'Yy':
                Ticket.delete(t)

    if missing_tickets:
        sys.exit(2)
