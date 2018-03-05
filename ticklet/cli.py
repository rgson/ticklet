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

import argparse
import operator
import os
import sys
import yaml

from .config import config
from .types import Ticket, TicketNotFound, Notes


def run():
    user_config_dir = os.environ.get('XDG_CONFIG_HOME',
    os.path.expanduser('~/.config'))
    user_config_file = user_config_dir + '/ticklet.yaml'
    try:
        with open(user_config_file) as f:
            config.update(yaml.load(f))
    except FileNotFoundError:
        pass

    for directory in config['directory'].values():
        os.makedirs(directory, exist_ok=True)

    # Parse command-line arguments

    parser = argparse.ArgumentParser()
    parser.add_argument(       '--version'  , help='output version info and exit'   , action='store_true')
    parser.add_argument('-l' , '--list'     , help='list tickets'                   , action='store_true')
    parser.add_argument('-k' , '--list-all' , help='list tickets, including archive', action='store_true')
    parser.add_argument('-a' , '--archive'  , help='move tickets to archive'        , action='store_true')
    parser.add_argument('-u' , '--unarchive', help='move tickets from archive'      , action='store_true')
    parser.add_argument('-o' , '--open'     , help='open existing tickets only'     , action='store_true')
    parser.add_argument('-d' , '--delete'   , help='delete tickets'                 , action='store_true')
    parser.add_argument('-s' , '--status'   , help='set the status'                                      )
    parser.add_argument('-m' , '--summary'  , help='set the summary'                                     )
    parser.add_argument('ticket'            , help='the ticket ID(s) to open/change', nargs='*'          )
    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(__version__)
        sys.exit(0)

    # Check for conflicting arguments

    conflicting_arguments = [
        {'-a/--archive': args.archive, '-u/--unarchive': args.unarchive},
        {'-d/--delete' : args.delete , '-o/--open'     : args.open     }]

    for conflicts in conflicting_arguments:
        if sum(conflicts.values()) > 1:
            names = [k for k, v in conflicts.items() if v]
            print('Conflicting options:', ', '.join(names), file=sys.stderr)
            return 1

    # Default to creating and opening tickets

    no_action = not any(v for k, v in args.__dict__.items() if k != 'ticket')
    args.create = no_action
    args.open |= no_action

    # Perform requested actions

    if no_action and not args.ticket:
        parser.print_help()

    if args.list or args.list_all:
        tickets = Ticket.list(include_archived=args.list_all)
        tickets = sorted(tickets, key=operator.attrgetter('id'))
        print('\n'.join(str(t) for t in tickets))

    elif not args.ticket:
        print('No tickets specified for action', file=sys.stderr)
        return 1

    else:
        missing_tickets = False

        for ticket_id in args.ticket:
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
            return 2

    return 0
