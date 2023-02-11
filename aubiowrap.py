import typing as t

import shutil
import subprocess
"""
Retrieve output from the aubio commandline tools
"""
def get_commandline_program(name):
    program = shutil.which(name)
    if program is None:
        raise IOError(f'{name} not found')

    return program

def aubiocommand(command: t.Sequence[str], parser=float):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    (out, _) = process.communicate()
    return [parser(n) for n in out.splitlines() if n]


def get_beat(soundfile: str, beat: bool) -> t.Sequence[float]:
    args: t.Tuple[str, ...]
    aubiocut = get_commandline_program('aubiocut')

    if beat:
        args = (aubiocut, '-b', soundfile)
    else:
        args = (aubiocut, soundfile)
    return aubiocommand(args)


def get_notes(soundfile: str):
    """
    aubionotes
    """
    aubionotes = get_commandline_program('aubionotes')
    if aubionotes is None:
        raise IOError('aubionotes not found')

    return aubiocommand((aubionotes, soundfile))


def get_pitch(soundfile: str, parser):
    """
    run aubiopitch on soundfile
    """
    aubiopitch = get_commandline_program('aubiopitch')
    return aubiocommand((aubiopitch, soundfile), parser)
