#!/usr/bin/env python3

import argparse
import enum
import fileinput
import functools
import glob
import itertools
import os
import re
import shutil
import subprocess
import sys
import textwrap

class State(enum.Enum):
    active = 1
    archived = 2

    @property
    def path(self):
        if self is State.active:
            return os.path.expanduser('~') + "/tickets/active"
        if self is State.archived:
            return os.path.expanduser('~') + "/tickets/archive"

@functools.total_ordering
class Ticket:
    def __init__(self, ticket_id):
        self.id = ticket_id
        for s in (State.active, State.archived):
            self.state = s
            if os.path.exists(self._path):
                self.notes = Notes(self._notes_filepath)
                break
        else:
            self.state = None
            self.notes = None

    def create(self):
        if self.state is not None:
            print("Ticket {} already exists".format(self.id), file=sys.stderr)
            return
        self.state = State.active
        self.notes = Notes.create(self.id, self._notes_filepath)

    def open(self):
        if self.state is None:
            return self._warn_doesnt_exist()
        directory = self._path
        notes_file = self._notes_filepath
        files = self.notes.files if self.notes is not None else {}
        directories = [directory] + list(self._find_repos(files))
        terminal_tabs = list(itertools.chain.from_iterable(
            ['--tab', '--working-directory', d] for d in directories))
        subprocess.Popen(['gnome-terminal', '--geometry', '80x88+0+0'] + terminal_tabs)
        subprocess.Popen(['subl', directory, notes_file] + list(files))
        subprocess.Popen(['nemo', directory])

    def delete(self):
        directory = self._path
        if directory is not None:
            shutil.rmtree(directory)

    def archive(self):
        self._move(State.archived)

    def unarchive(self):
        self._move(State.active)

    @property
    def status(self):
        if self.state is None:
            return self._warn_doesnt_exist()
        return self.notes.status

    @status.setter
    def status(self, value):
        if self.state is None:
            return self._warn_doesnt_exist()
        self.notes.status = value

    @property
    def summary(self):
        if self.state is None:
            return self._warn_doesnt_exist()
        return self.notes.summary

    def _move(self, new_state):
        if self.state is None:
            return self._warn_doesnt_exist()
        if self.state is new_state:
            return
        old_path = self._path
        self.state = new_state
        new_path = self._path
        shutil.move(old_path, new_path)
        self.notes.filepath = new_path

    def _warn_doesnt_exist(self):
        print("Ticket {} does not exist".format(self.id), file=sys.stderr)

    def _find_repos(self, files):
        dirs = {os.path.dirname(f) for f in files}
        repos = set()
        cmd = ['git', 'rev-parse', '--show-toplevel']
        for d in dirs:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=d) as p:
                repo = p.stdout.read()
                if repo:
                    repos.add(repo.decode('utf-8').strip())
        return repos

    @property
    def _notes_filepath(self):
        if self.state is None:
            return None
        return "{}/notes.md".format(self._path, self.id)

    @property
    def _path(self):
        if self.state is None:
            return None
        return "{}/{}".format(self.state.path, self.id)

    @staticmethod
    def get_tickets(include_archived=False):
        tickets = set()
        included_states = {State.active} if not include_archived else {State.active, State.archived}
        for state in included_states:
            state_dir = state.path
            for ticket_dir in glob.glob(state_dir + '/*/'):
                ticket_id = ticket_dir[len(state_dir)+1:-1]
                tickets.add(Ticket(ticket_id))
        return tickets

    def __eq__(self, other):
        if not hasattr(other, "id"):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other):
        if not hasattr(other, "id"):
            return NotImplemented
        return self.id < other.id

    def __str__(self):
        return("{:10}  {:25.25}  {}".format(self.id, self.summary, self.status))

    def __hash__(self):
        return hash(self.id)

class Notes:
    def __init__(self, filepath):
        self.filepath = filepath

    @property
    def status(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                if line.startswith("_Status_"):
                    return line[line.index(':') + 1:].strip()
        return ''

    @status.setter
    def status(self, value):
        with fileinput.FileInput(self.filepath, inplace=True) as f:
            for line in f:
                if line.startswith("_Status_"):
                    line = "_Status_ : {}\n".format(value)
                print(line, end='')

    @property
    def summary(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                if line.startswith("_Summary_"):
                    return line[line.index(':') + 1:].strip()
        return ''

    @property
    def files(self):
        files_section = False
        relevant_files = set()
        with open(self.filepath, 'r') as f:
            for line in f:
                if line.startswith("## Files"):
                    files_section = True
                elif line.startswith("## Notes"):
                    files_section = False
                elif files_section and line.startswith("- "):
                    relevant_files.add(line[len("- "):].strip())
        return relevant_files

    @staticmethod
    def create(ticket_id, filepath):
        content = textwrap.dedent("""\
            # Ticket {}

            _Summary_:
            _Status_ : New


            ## Files

            -


            ## Notes

            """.format(ticket_id))
        os.makedirs(os.path.dirname(filepath))
        with open(filepath, 'w+') as f:
            print(content, file=f)
        return Notes(filepath)


################################################################################

# Parse command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument('-l' , '--list'     , help="list tickets"                   , action='store_true')
parser.add_argument('-k' , '--list-all' , help="list tickets, including archive", action='store_true')
parser.add_argument('-a' , '--archive'  , help="move tickets to archive"        , action='store_true')
parser.add_argument('-u' , '--unarchive', help="move tickets from archive"      , action='store_true')
parser.add_argument('-o' , '--open'     , help="open existing tickets only"     , action='store_true')
parser.add_argument('-d' , '--delete'   , help="delete tickets"                 , action='store_true')
parser.add_argument('-s' , '--status'   , help="set the status"                 , nargs=1)
parser.add_argument('ticket'            , help="the ticket ID(s) to open/change", type=Ticket, nargs='*')
parser.set_defaults(action='create_tickets')
args = parser.parse_args()

# Create active and archive directories

for state in {State.active, State.archived}:
    os.makedirs(state.path, exist_ok=True)

# Run command

if args.list or args.list_all:
    found = Ticket.get_tickets(include_archived=args.list_all)
    for ticket in sorted(found):
        print(ticket)

elif args.ticket:

    if args.archive and args.unarchive:
        print('Conflicting arguments: -a/--archive, -u/--unarchive')
        sys.exit(1)

    no_action = not any(v for k, v in args.__dict__.items() if k != 'ticket')

    for ticket in args.ticket:

        if args.status:
            ticket.status = args.status[0]

        if args.archive:
            ticket.archive()

        if args.unarchive:
            ticket.unarchive()

        if args.open:
            ticket.open()

        if args.delete:
            prompt = 'Are you sure you want to delete {}? (y/N): '.format(ticket.id)
            confirm = None
            while confirm not in 'YyNn':
                confirm = input(prompt) or 'N'
            if confirm in 'Yy':
                ticket.delete()

        if no_action:
            if ticket.state is None:
                ticket.create()
            ticket.open()

else:
    parser.print_help()
