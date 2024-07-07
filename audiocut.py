#!/usr/bin/env python

from typing import Tuple, List, Sequence
from dataclasses import dataclass
import click
import random
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
)  # type: ignore
from aubiowrap import get_beat, get_pitch


Seconds = float
Frequency = float


@dataclass
class Config:
    soundfile: str
    outfile: str
    randomize: float
    probability: float


class Timeline:
    fps: float = 25
    config: Config
    beats: Sequence[Seconds]
    pitches: List[Tuple[Seconds, Frequency]]
    clips: List[VideoFileClip]
    slices: List[VideoFileClip]
    audio: AudioFileClip

    def __init__(self, fps: float, config: Config):
        self.fps = fps
        self.config = config
        self.clips = []
        self.slices = []

    def add_clip(self, clip: VideoFileClip):
        self.clips.append(clip)

    def lookup_pitch(
        self, time: Seconds, tolerance: Seconds = 0.1
    ) -> Tuple[Seconds, Frequency]:
        last = 0.0
        t = 0.0
        for t, v in self.pitches:
            if t < time:
                last = v
                continue
            elif t - time < tolerance:
                return (t, v)
            else:
                return (t, last)
        return (t, last)

    def on_transient(
        self, time: float, time_delta: float = 0.25, frequency_delta: float = 4.0
    ) -> bool:
        (t1, a) = self.lookup_pitch(time - time_delta, tolerance=0.01)
        (t2, b) = self.lookup_pitch(time, tolerance=0.01)
        return abs(a - b) < frequency_delta

    def get_slice_times(
        self, start: float, duration: float, tm1: float, t: float
    ) -> Tuple[float, float]:
        delta = t - tm1
        if self.re_trigger(t) or start + delta > duration:
            r = random.random()
            start = r * (duration - delta)
        end = start + delta
        return (start, end)

    def re_trigger(self, t) -> bool:
        if random.random() > self.config.randomize:
            return self.on_transient(t)
        else:
            return random.random() < self.config.probability

    def slice_clips(self):
        """
        Slice according to the beat structure
        """
        label = "Slicing video to the beat"
        with click.progressbar(self.beats, label=label) as beats:
            clip = self.clips[0]
            tm1 = 0.0
            start = 0.0
            for time in beats:
                start, end = self.get_slice_times(start, clip.duration, tm1, time)
                self.slices.append(clip.subclip(start, end))
                tm1 = time

    def combine_slices(self):
        self.combined = concatenate_videoclips(self.slices)

    def save_with_audio(self):
        with AudioFileClip(self.config.soundfile) as audioclip:
            self.combined.audio = audioclip
            self.save()

    def save(self):
        self.combined.write_videofile(self.config.outfile, fps=self.fps)


def is_close(a: float, b: float, tolerance: float = 0.1):
    abs(abs(a) - abs(b)) < tolerance


def pitch_parser(line) -> Tuple[float, float]:
    time, pitch = line.split(b" ")
    return (float(time), float(pitch))


@click.command()
@click.argument("videofile")
@click.option("-s", "--soundfile")
@click.option("-o", "--outfile", default="output.mp4")
@click.option("-f", "--fps", default=25, type=float)
@click.option("-b", "--beat", is_flag=True, help="the -b parameter to aubiocut")
@click.option(
    "-r",
    "--randomize",
    default=0.5,
    type=float,
    help="distribution of determinism to randomness",
)
@click.option(
    "-p",
    "--probability",
    default=0.618,
    type=float,
    help="probability of a random event",
)
@click.option("--with-audio", is_flag=True)
def main(
    videofile: str,
    soundfile: str,
    outfile: str,
    fps: float,
    beat: bool,
    randomize: float,
    probability: float,
    with_audio: bool,
):
    """
    Slice a video clip to the beat of a given soundtrack.
    """
    config = Config(
        soundfile=soundfile,
        outfile=outfile,
        randomize=randomize,
        probability=probability,
    )
    timeline = Timeline(fps=fps, config=config)
    timeline.pitches = get_pitch(soundfile, pitch_parser)
    timeline.beats = get_beat(soundfile, beat)

    with VideoFileClip(videofile) as clip:
        timeline.add_clip(clip)
        timeline.slice_clips()
        timeline.combine_slices()
        if with_audio:
            timeline.save_with_audio()
        else:
            timeline.save()


if __name__ == "__main__":
    main()
