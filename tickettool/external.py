# Functions related to external programs

import os
import subprocess


def open_sublime(files=[], directories=[]):
    _open_external_program(['subl'] + files + directories)

def open_nemo(directories=[]):
    _open_external_program(['nemo'] + directories)

def open_gnome_terminal(directories=[]):
    tabs = [x for d in directories for x in ['--tab', '--working-directory', d]]
    _open_external_program(['gnome-terminal', '--geometry', '80x88+0+0'] + tabs)

def _open_external_program(cmd):
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def find_git_root(file):
    try:
        directory = os.path.dirname(file)
        p = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=directory)
        return p.stdout.decode('utf-8').strip() or None
    except FileNotFoundError:
        return None
