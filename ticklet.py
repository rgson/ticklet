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

import argparse
import collections
import fileinput
import glob
import operator
import os
import shutil
import subprocess
import sys
import texttable
import textwrap
import yaml


class TicketNotFound(Exception):
    pass

class ProfileNotFound(Exception):
    pass

class OpenerNotFound(Exception):
    pass


class Config:

    default_config_dir = os.path.join(
            os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
            'ticklet')

    default_config = {
        'directory_active': os.path.expanduser('~/tickets/active'),
        'directory_archive': os.path.expanduser('~/tickets/archive'),
        'display_grid': False,
        'template': textwrap.dedent("""\
            # Ticket {id}

            _Summary_:
            _Status_ : New


            ## Files

            -


            ## Notes

            """),
    }

    def __init__(self, profile=None):
        self.config_dir = self.default_config_dir
        self.config = self.default_config.copy()
        self.profile = None
        if profile:
            self.set_profile(profile)
        self.load_config()

    def __getattr__(self, key):
        try:
            return self.config[key]
        except KeyError:
            raise AttributeError

    def load_config(self):
        try:
            with open(self.config_file()) as f:
                self.config.update(yaml.load(f) or {})
        except FileNotFoundError:
            return
        for key, value in self.config.items():
            if key.startswith('directory_'):
                self.config[key] = os.path.expanduser(value)

    def set_profile(self, profile):
        self.profile = profile
        self.config_dir = self.profile_dir(profile)
        if not os.path.isdir(self.config_dir):
            raise ProfileNotFound(profile)

    def profile_dir(self, profile):
        return os.path.join(self.default_config_dir, 'profiles', profile)

    def config_file(self):
        return os.path.join(self.config_dir, 'config.yaml')

    def opener_dir(self):
        return os.path.join(self.config_dir, 'openers')

    def openers(self):
        try:
            return sorted([
                f.path for f in os.scandir(self.opener_dir())
                if f.is_file() and os.access(f.path, os.X_OK)
            ])
        except FileNotFoundError:
            return []

    @classmethod
    def touch_user_config(cls):
        c = cls()
        for directory in [c.config_dir, c.profile_dir(''), c.opener_dir()]:
           os.makedirs(directory, exist_ok=True)
        try:
            with open(c.config_file(), 'x') as f:
                pass
        except FileExistsError:
            pass


class Ticket(collections.namedtuple('Ticket', 'id path')):

    @staticmethod
    def _path(id, directory):
        return '{}/{}'.format(directory, id)

    @classmethod
    def find(cls, id, optional=False):
        directories = (config.directory_active, config.directory_archive)
        paths = (cls._path(id, directory) for directory in directories)
        found = next((path for path in paths if os.path.exists(path)), None)
        if not found and not optional:
            raise TicketNotFound(id)
        return cls(id=id, path=found) if found else None

    @classmethod
    def create(cls, id):
        path = cls._path(id, config.directory_active)
        os.makedirs(path)
        ticket = cls(id=id, path=path)
        Notes.create(ticket)
        return ticket

    def delete(self):
        shutil.rmtree(self.path)

    @classmethod
    def list(cls, include_archived=False):
        yield from cls._list_tickets_in(config.directory_active)
        if include_archived:
            yield from cls._list_tickets_in(config.directory_archive)

    @classmethod
    def _list_tickets_in(cls, directory):
        for d in glob.glob(directory + '/*/'):
            yield cls(id=d[len(directory)+1:-1], path=d[:-1])

    def archive(self):
        return self._move_ticket(config.directory_archive)

    def unarchive(self):
        return self._move_ticket(config.directory_active)

    def _move_ticket(self, target_dir):
        target_path = Ticket._path(self.id, target_dir)
        shutil.move(self.path, target_path)
        return self.__class__(self.id, target_path)

    def open(self):
        n = Notes.read(self)
        files = {n.path} | set(n.files) if n else {self.path}
        files = {os.path.expanduser(f) for f in files}
        openers = config.openers()
        if not openers:
            raise OpenerNotFound()
        for opener in openers:
            subprocess.run([opener] + list(files))


class Notes(collections.namedtuple('Notes', 'path summary status files')):

    @staticmethod
    def _path(ticket):
        return '{}/{}'.format(ticket.path, 'notes.md')

    @classmethod
    def create(cls, ticket):
        path = Notes._path(ticket)
        with open(path, 'w') as f:
            print(config.template.format(id=ticket.id), file=f)
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


# Initialize the user profile

Config.touch_user_config()

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

# Load configuration

try:
    config = Config(profile=args.profile)
except ProfileNotFound as e:
    print('Profile not found:', e, file=sys.stderr)
    sys.exit(1)

# Ensure that the ticket directories exist

for directory in (config.directory_active, config.directory_archive):
    os.makedirs(directory, exist_ok=True)

# Default to creating and opening tickets

ignore_args = {'tickets', 'profile'}
no_action = not any(v not in (None, False)
                    for k, v in args.__dict__.items()
                    if k not in ignore_args)
args.create = no_action
args.open |= no_action

# Perform requested actions

if no_action and not args.tickets:
    parser.print_help()

if args.list or args.list_all:
    tickets = Ticket.list(include_archived=args.list_all)
    tickets = sorted(tickets, key=operator.attrgetter('id'))
    if not tickets:
        sys.exit(0)
    notes = (Notes.read(t) or Notes(['']*4) for t in tickets)
    max_width = shutil.get_terminal_size((0, 0)).columns - 1
    tbl = texttable.Texttable(max_width)
    if not config.display_grid:
        tbl.set_deco(0)
    tbl.add_rows([[t.id, n.summary, n.status] for t, n in zip(tickets, notes)],
                 header=False)
    print(tbl.draw())

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
            try:
                Ticket.open(t)
            except OpenerNotFound:
                print("You don't have any openers. To open tickets, "
                      "add some to your configuration directory ({})."
                      .format(config.opener_dir()), file=sys.stderr)
        elif args.delete:
            prompt = 'Are you sure you want to delete {}? (y/N): '.format(t.id)
            confirm = '-'
            while confirm not in 'YyNn':
                confirm = input(prompt) or 'N'
            if confirm in 'Yy':
                Ticket.delete(t)

    if missing_tickets:
        sys.exit(2)
