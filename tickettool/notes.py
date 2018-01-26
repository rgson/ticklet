# Functions related to notes

import collections
import fileinput
import os


_note_template = ("""\
# Ticket {id}

_Summary_:
_Status_ : New


## Files

-


## Notes

""")

Notes = collections.namedtuple('Notes', 'path summary status files')

def path(ticket):
    return '{}/{}'.format(ticket.path, 'notes.md')

def create(ticket):
    file = path(ticket)
    with open(file, 'w') as f:
        print(_note_template.format(id=ticket.id), file=f)
    return Notes(path=file, summary='', status='New', files=[])

def read(ticket):
    try:
        file = path(ticket)
        summary = status = None
        files, files_section = [], False
        with open(file, 'r') as f:
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
        return Notes(path=file, summary=summary, status=status, files=files)
    except FileNotFoundError:
        return None

def write(notes):
    files_section, files_printed = False, False
    with fileinput.FileInput(notes.path, inplace=True) as f:
        for line in f:
            if line.startswith('_Status_'):
                line = '_Status_ : {}\n'.format(notes.status)
            elif line.startswith('_Summary_'):
                line = '_Summary_: {}\n'.format(notes.summary)
            elif line.startswith('## Files'):
                files_section = True
            elif files_section and line.startswith('- '):
                line = ''
                if not files_printed:
                    line = '- {}\n'.format('\n- '.join(notes.files))
                    files_printed = True
            elif files_section and line.startswith('## '):
                files_section = False
            print(line, end='')
