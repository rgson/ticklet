# Ticklet

A command-line tool for ticket management (the bug tracker kind).
Keeps track of tickets, including status, affected files and related notes.

## Usage

Run `ticklet -h` for usage instructions:

```
usage: ticklet [-h] [-l] [-k] [-a] [-u] [-o] [-d] [-s STATUS] [-m SUMMARY]
               [ticket [ticket ...]]

positional arguments:
  ticket                the ticket ID(s) to open/change

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list tickets
  -k, --list-all        list tickets, including archive
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

### Manual

1. Copy `ticklet.py` (ideally without the `.py` extension) to somewhere in your `$PATH`, e.g. `/usr/local/bin`.
2. Ensure that the file is executable (`755`).
3. Install the [dependencies](#Dependencies).

*Example:*

```sh
# Debian 9 (Stretch)
sudo install -m 0755 -o root ticklet.py /usr/local/bin/ticklet
sudo apt install python3 python3-yaml
```

### Automatic (with `setuptools`)

1. Install the [dependencies](#Dependencies).
2. Build and install using `setup.py`.

```sh
# Debian 9 (Stretch)
sudo apt install git python3-setuptools python3-yaml
sudo ./setup.py install
```

## Dependencies

- Python 3
- PyYAML

## Configuration

Some of `ticklet`s behavior can be configured through `~/.config/ticklet.yaml`.

*Example:*

```yaml
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
  
  
```
