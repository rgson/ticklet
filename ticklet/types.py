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

import collections
import fileinput
import glob
import os
import shutil
import subprocess

from .config import config


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
        n = Notes.read(self)
        if n:
            roots = {External.find_git_root(f) for f in n.files}
            repos = [r for r in roots if r]
            files = [n.path] + n.files
            directories = [self.path] + repos
        else:
            files, directories = [], [self.path]
        External.open_sublime(files, directories)
        External.open_nemo(directories)
        External.open_gnome_terminal(directories)


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


class External:

    @staticmethod
    def open_sublime(files=[], dirs=[]):
        External._start_program(['subl'] + files + dirs)

    @staticmethod
    def open_nemo(dirs=[]):
        External._start_program(['nemo'] + dirs)

    @staticmethod
    def open_gnome_terminal(dirs=[]):
        tabs = [x for d in dirs for x in ['--tab', '--working-directory', d]]
        cmd = ['gnome-terminal', '--geometry', '80x88+0+0'] + tabs
        External._start_program(cmd)

    @staticmethod
    def _start_program(cmd):
        subprocess.Popen(cmd,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def find_git_root(filename):
        try:
            dirname = os.path.dirname(filename)
            p = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=dirname)
            return p.stdout.decode('utf-8').strip() or None
        except FileNotFoundError:
            return None
