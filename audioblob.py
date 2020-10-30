#!/usr/bin/env python3
from typing import List, Tuple
from os import path
from aubio import fft, fvec, level_lin
import argparse
import cv2
import numpy as np

from audiopack import loadwav, audio_chunks
"""
Render blurry blob, dancing around the image to the music
"""


def blob(image, data: Tuple[List, List]):
    height, width, _ = image.shape

    cx = width // 2
    cy = height // 2

    d1, d2 = data

    f = fft(len(d1))
    s1 = f.rdo(f(fvec(d1)))
    s2 = f.rdo(f(fvec(d2)))

    level = level_lin(fvec(d1 + d2))

    for i, j, k, n in zip(d1, s1, reversed(d2), s2):

        x = cx + int(i * width * 0.5)
        y = cy + int((height * k * 0.5))

        radius = level * 1000
        r1 = int(j * radius)
        r2 = int(n * radius)
        if r1 > 0 and r2 > 0:
            cv2.ellipse(image, (x, y), (r1, r2), 0, 0, 360, (255, 255, 255))
            image = cv2.GaussianBlur(image, (5, 5), 0)

    return image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse audiofile to dancing blob'
    )
    parser.add_argument('soundfile', metavar='soundfile', type=str,
        help='soundfile'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp/',
        help='output directory'
    )
    parser.add_argument('-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='frames per second'
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    blocksize: int = meta.rate // args.fps
    blocks: int    = meta.samples // blocksize

    for n, block in enumerate(audio_chunks(data, blocksize)):
        padded = "{0:05d}".format(n)
        bitmap = np.zeros((args.height, args.width, 3), np.uint8)
        if meta.channels == 2:
            block_channels = (block.T[0], block.T[1])
        else:
            block_channels = np.array_split(data, 2)

        image = blob(bitmap, block_channels)
        cv2.imwrite(path.join(args.outdir, f'{padded}.png'), image)
