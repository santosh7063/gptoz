# -*- coding: utf-8 -*-
import os
from sys import stdout


# guess terminal size
def get_columns():
    try:
        _, columns = map(int, os.popen('stty size', 'r').read().split())
    except ValueError:
        _, columns = 20, 80

    return columns - 3


def progress(part, complete, width=get_columns()):
    done = int(part / complete * width)
    left = width - done
    stdout.write('[%s%s]' % (('-' * done), (' ' * left)))
    stdout.flush()
    stdout.write("\b" * (width + 2))
