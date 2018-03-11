# Ticklet

A command-line tool for ticket management (the bug tracker kind).
Keeps track of tickets, including status, affected files and related notes.

## Usage

Run `ticklet -h` for usage instructions:

```
usage: ticklet [-h] [--version] [-l] [-k] [-a] [-u] [-o] [-d] [-s STATUS]
               [-m SUMMARY]
               [TICKET [TICKET ...]]

positional arguments:
  TICKET                ticket(s) to act upon

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -l, --list            list active tickets
  -k, --list-all        list all tickets
  -a, --archive         move tickets to archive
  -u, --unarchive       move tickets from archive
  -o, --open            open existing tickets only
  -d, --delete          delete tickets
  -s STATUS, --status STATUS
                        set the status
  -m SUMMARY, --summary SUMMARY
                        set the summary
```

## Installation

### Automatic (with `.deb` package)

This is the recommended approach on Debian-based systems.

```sh
# Debian 9 (Stretch)
make deb
sudo dpkg -i ../ticklet_*.deb
```

### Automatic (with `setuptools`)

1. Install the [dependencies](#Dependencies).
2. Build and install `ticklet` using `setup.py`.

```sh
# Debian 9 (Stretch)
sudo apt install python3 python3-yaml python3-setuptools
sudo ./setup.py install
```

### Manual

1. Copy `ticklet.py` (ideally without the `.py` extension) to somewhere in your `$PATH`, e.g. `/usr/bin`.
2. Ensure that the file is executable (`755`).
3. Install the [dependencies](#Dependencies).

```sh
# Debian 9 (Stretch)
sudo install -m 0755 -o root ticklet.py /usr/bin/ticklet
sudo apt install python3 python3-yaml
```

## Dependencies

- Python 3
- PyYAML

## Configuration

Some of `ticklet`'s behavior can be configured through `~/.config/ticklet.yaml`.

```yaml
# Example config
---
directory:
  active: /home/yourname/tickets/active
  archive: /home/yourname/tickets/archive

template: |
  # Ticket {id}
  
  _Summary_:
  _Status_ : New
  
  
  ## Files
  
  -
  
  
  ## Notes
  
  

plugins:
  filters:
    - git
  openers:
    - nemo
    - gnome_terminal
    - vscode
```
