# Ticklet

A command-line tool for ticket management (the bug tracker kind).
Keeps track of tickets, including status, affected files and related notes.

## Getting started

1. Place `ticklet.py` somewhere in your `$PATH`, e.g. in `~/bin`.
2. Run `ticklet.py -h` for usage information.

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
