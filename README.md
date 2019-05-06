# Ticklet

`ticklet` is a command-line tool for ticket management (the bug tracker kind).
It keeps track of tickets, including status, affected files and related notes.

## Usage

Usage instructions can be viewed at any time by running `ticklet -h`.
The program also comes with an associated manual page (`man ticklet`).

```
usage: ticklet [-h] [--version] [-l] [-k] [-a] [-u] [-o] [-d] [-s STATUS]
               [-m SUMMARY] [-r FROM TO] [-p PROFILE]
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
  -r FROM TO, --rename FROM TO
                        rename a ticket
  -p PROFILE, --profile PROFILE
                        use an alternative configurations profile
```

## Installation

### Debian-based distributions

The recommended approach for users of Debian-based systems is to install the
program in the form of a `.deb` package.

Pre-built `.deb` packages can be downloaded from the
[releases page](https://github.com/rgson/ticklet/releases).
Alternatively, one can be built from source: 

```sh
# 1. Build the .deb package
sudo apt install devscripts fakeroot equivs git-buildpackage
mk-build-deps -i -s sudo debian/control
make deb

# 2. Install ticklet and its dependencies
sudo apt install ../ticklet_*.deb
```

### Other distributions

The program can also be installed in a more distribution-agnostic way using
`make install`. The Makefile supports the use of [DESTDIR](gnu-destdir) and
other relevant [directory variables](gnu-dirvars) to customize the installation.

Generally, the installation goes something like this:

1. Install Python 3 and the other [dependencies](requirements.txt).
2. Build and install `ticklet` using `make install`.

```sh
# 1. Run a staged install in a local sub-directory
make install DESTDIR=./stage

# 2. Verify that the directory structure in ./stage suits your system

# 3. Perform a system-wide install
sudo make install
```

[gnu-destdir]: https://www.gnu.org/prep/standards/html_node/DESTDIR.html#DESTDIR
[gnu-dirvars]: https://www.gnu.org/prep/standards/html_node/Directory-Variables.html#Directory-Variables

## Configuration

Some of `ticklet`'s behavior can be configured through
`~/.config/ticklet/config.yaml`.

The list of active plugins is of particular interest to every `ticklet` user.
It determines the actions taken when a ticket is opened. Due to users' wildly
divergent preferences for different text editors, etc., there is
**no default action** when opening tickets. Defining your own setup with the
help of plugins is thus essential for a major part of `ticklet`'s functionality.

```yaml
# Example config
---
directory_active: /home/yourname/tickets/active
directory_archive: /home/yourname/tickets/archive

display_grid: false

template: |
  # Ticket {id}
  
  _Summary_:
  _Status_ : New
  
  
  ## Files
  
  -
  
  
  ## Notes
  
  
```

## Openers

Openers define what happens when a ticket is opened.

An opener is an executable located in the `~/.config/ticklet/openers` directory.
When a ticket is opened, all of the configured openers are executed in
lexicographic order. The full list of files from the ticket's notes, including
the notes file itself, is passed as arguments. It may then filter and open the
files in any way desired.

Example:
```sh
# ~/.config/ticklet/openers/example.sh

#!/bin/sh
echo "$@"
code -n "$@"
```

## Profiles

Profiles allow configurations to be temporarily overridden using the
`-p`/`--profile` option. Settings specified in a profile will be used instead of
the settings defined in the user's default configuration.

Each profile consists of a directory in `~/.config/ticklet/profiles`. For
example, `~/.config/ticklet/profiles/read` defines a profile named *read*. This
directory can then contain configuration files just like the main directory.
When a profile is activated, all settings will be loaded from within the
profile's directory instead.
