#!/usr/bin/env python3
"""
Render blurry blob, dancing to the music
TODO:
    - add damping
    - sync using aubiotempo
"""
from typing import List, Tuple
from dataclasses import dataclass
import json
from os import path
from aubio import fft, fvec, level_lin
import argparse
import cv2
import numpy as np

from audiopack import loadwav, audio_chunks


@dataclass
class Opts:
    radius: int


def blob(image, data: Tuple[List, List], opts: Opts):
    height, width, _ = image.shape

    cx = width // 2
    cy = height // 2

    d1, d2 = data

    f = fft(len(d1))
    s1 = f.rdo(f(fvec(d1)))
    s2 = f.rdo(f(fvec(d2)))

    level_1 = level_lin(fvec(d1))
    level_2 = level_lin(fvec(d2))

    for i, j, k, n, rk, rn in zip(d1, d2, s1, s2, reversed(s1), reversed(s2)):

        x = cx + int(j * width) - int(i * width)
        y = cy + int(height * k) - int(rk * height)

        radius_1 = level_1 * opts.radius
        radius_2 = level_2 * opts.radius
        r1 = int(k * radius_1)
        r2 = int(n * radius_2)

        blur_x = 5
        blur_y = 5

        if r1 > 0 and r2 > 0:
            color = (255, 255, 255)
            cv2.ellipse(image, (x, y), (r1, r2), 0, 0, 360, color)
            image = cv2.GaussianBlur(image, (blur_x, blur_y), 0)

    return image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse audiofile to dancing blob")
    parser.add_argument("soundfile", metavar="soundfile", type=str, help="soundfile")
    parser.add_argument(
        "-a",
        "--amplify",
        action="store",
        type=float,
        default=1.0,
        help="amplify audio frames",
    )
    parser.add_argument(
        "-o", "--outdir", action="store", default="/tmp/", help="output directory"
    )
    parser.add_argument(
        "-W", "--width", type=int, action="store", default=1280, help="width"
    )
    parser.add_argument(
        "-H", "--height", type=int, action="store", default=720, help="height"
    )
    parser.add_argument(
        "-f", "--fps", type=int, action="store", default=25, help="frames per second"
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=int,
        action="store",
        default=1000,
        help="base radius of the circles",
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    data = data * args.amplify

    blocksize: int = meta.rate // args.fps
    blocks: int = meta.samples // blocksize

    opts = Opts(radius=args.radius)

    with open(path.join(args.outdir, "params.json"), "w") as f:
        json.dump(args.__dict__, f)

    for n, block in enumerate(audio_chunks(data, blocksize)):
        padded = "{0:05d}".format(n)
        bitmap = np.zeros((args.height, args.width, 3), np.uint8)
        if meta.channels == 2:
            block_channels = (block.T[0], block.T[1])
        else:
            block_channels = np.array_split(data, 2)

        image = blob(bitmap, block_channels, opts)
        cv2.imwrite(path.join(args.outdir, f"{padded}.png"), image)

        percent_finished = int(n / blocks * 100)
        print(f"{percent_finished:>3}%", end="\r", flush=True)
