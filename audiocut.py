#!/usr/bin/env python
import click
import random
import shutil
import subprocess
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips
)


def get_timecodes(soundfile, beat):
    aubiocut = shutil.which('aubiocut')
    if beat:
        aubiocut_command = (aubiocut, '-b', soundfile)
    else:
        aubiocut_command = (aubiocut, soundfile)

    process = subprocess.Popen(aubiocut_command, stdout=subprocess.PIPE)
    (out, _) = process.communicate()
    return [float(n) for n in out.split(b'\n') if n]


@click.command
@click.argument('videofile')
@click.option('-s', '--soundfile')
@click.option('-o', '--outfile', default='output.mp4')
@click.option('-b', '--beat', is_flag=True)
def main(videofile, soundfile, outfile, beat):
    timecodes = get_timecodes(soundfile, beat)

    clips = []
    t0 = 0
    r = random.random()
    with VideoFileClip(videofile) as clip:
        for t in timecodes:
            if random.random() > 0.666:
                r = random.random()

            delta = t - t0
            t0 = r * (clip.duration - delta)
            clips.append(clip.subclip(t0, t0 + delta))
            t0 = t

        final_clip = concatenate_videoclips(clips)
        with AudioFileClip(soundfile) as audioclip:
            final_clip.audio = audioclip
            final_clip.write_videofile(outfile)


if __name__ == '__main__':
    main()
