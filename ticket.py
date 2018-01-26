#!/usr/bin/env python3

import argparse
import operator
import os
import sys

from tickettool import notes, ticket


# Create active and archive directories

for d in [ticket._dir_active, ticket._dir_archive]:
    os.makedirs(d, exist_ok=True)

# Parse command-line arguments

parser = argparse.ArgumentParser()
parser.add_argument('-l' , '--list'     , help='list tickets'                   , action='store_true')
parser.add_argument('-k' , '--list-all' , help='list tickets, including archive', action='store_true')
parser.add_argument('-a' , '--archive'  , help='move tickets to archive'        , action='store_true')
parser.add_argument('-u' , '--unarchive', help='move tickets from archive'      , action='store_true')
parser.add_argument('-o' , '--open'     , help='open existing tickets only'     , action='store_true')
parser.add_argument('-d' , '--delete'   , help='delete tickets'                 , action='store_true')
parser.add_argument('-s' , '--status'   , help='set the status'                                      )
parser.add_argument('ticket'            , help='the ticket ID(s) to open/change', nargs='*'          )
args = parser.parse_args()

# Check for conflicting arguments

conflicting_arguments = [
    {'-a/--archive': args.archive, '-u/--unarchive': args.unarchive},
    {'-d/--delete' : args.delete , '-o/--open'     : args.open     }]

for conflicts in conflicting_arguments:
    if sum(conflicts.values()) > 1:
        names = [k for k, v in conflicts.items() if v]
        print('Conflicting options:', ', '.join(names), file=sys.stderr)
        sys.exit(1)

# Default to creating and opening tickets

no_action = sum(bool(v) for k, v in args.__dict__.items() if k != 'ticket') < 1
args.create = no_action
args.open |= no_action

# Perform requested actions

if no_action and not args.ticket:
    parser.print_help()

if args.list or args.list_all:
    tickets = ticket.list(include_archived=args.list_all)
    tickets = sorted(tickets, key=operator.attrgetter('id'))
    tickets = [ticket.str(t) for t in tickets]
    print('\n'.join(tickets))

elif not args.ticket:
    print('No tickets specified for action', file=sys.stderr)
    sys.exit(1)

else:
    error = False

    for ticket_id in args.ticket:
        try:
            t = ticket.find(ticket_id)
        except ticket.TicketNotFound as e:
            if args.create:
                t = ticket.create(ticket_id)
            else:
                print('Ticket not found:', e, file=sys.stderr)
                error = True
                continue

        if args.status is not None:
            notes.write(notes.read(t)._replace(status=args.status))

        if args.archive:
            t = ticket.archive(t)
        elif args.unarchive:
            t = ticket.unarchive(t)

        if args.open:
            ticket.open(t)
        elif args.delete:
            prompt = 'Are you sure you want to delete {}? (y/N): '.format(t.id)
            confirm = '-'
            while confirm not in 'YyNn':
                confirm = input(prompt) or 'N'
            if confirm in 'Yy':
                ticket.delete(t)

    if error:
        sys.exit(1)
