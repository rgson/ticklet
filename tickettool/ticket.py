# Functions related to tickets

import collections
import glob
import os
import shutil

from tickettool import external, notes


_dir_active  = os.path.expanduser('~') + '/tickets/active'
_dir_archive = os.path.expanduser('~') + '/tickets/archive'

Ticket = collections.namedtuple('Ticket', 'id path')

class TicketNotFound(Exception):
    pass

def path(id, directory=_dir_active):
    return '{}/{}'.format(directory, id)

def find(id, optional=False):
    directories = (_dir_active, _dir_archive)
    paths = (path(id, directory) for directory in directories)
    found = next((path for path in paths if os.path.exists(path)), None)
    if not found and not optional:
        raise TicketNotFound(id)
    return Ticket(id=id, path=found) if found else None

def create(id):
    p = path(id)
    os.makedirs(p)
    ticket = Ticket(id=id, path=p)
    notes.create(ticket)
    return ticket

def delete(ticket):
    shutil.rmtree(ticket.path)

def list(include_archived=False):
    tickets = _list_tickets_in(_dir_active)
    if include_archived:
        tickets += _list_tickets_in(_dir_archive)
    return tickets

def _list_tickets_in(directory):
    return [Ticket(id=d[len(directory)+1:-1], path=d[:-1])
            for d in glob.glob(directory + '/*/')]

def str(ticket):
    n = notes.read(ticket)
    return ('{:10}  {:25.25}  {}'.format(ticket.id, n.summary, n.status) if n
            else ticket.id)

def archive(ticket):
    return _move_ticket(ticket, _dir_archive)

def unarchive(ticket):
    return _move_ticket(ticket, _dir_active)

def _move_ticket(ticket, target_dir):
    target_path = path(ticket.id, target_dir)
    shutil.move(ticket.path, target_path)
    return Ticket(ticket.id, target_path)

def open(ticket):
    n = notes.read(ticket)
    if n:
        repos = [r for r in {external.find_git_root(f) for f in n.files} if r]
        files = [n.path] + n.files
        directories = [ticket.path] + repos
    else:
        files, directories = [], [ticket.path]
    external.open_sublime(files, directories)
    external.open_nemo(directories)
    external.open_gnome_terminal(directories)
