#!/usr/bin/env python3
"""
Distort one image bz the lightness values of another, modulated by sound input
"""
from typing import Any, List, Tuple
from dataclasses import dataclass
import sys
from glob import glob
from os import path
from aubio import fft, fvec, level_lin
from itertools import cycle
import argparse
import cv2
import numpy as np

from audiopack import loadwav, audio_chunks


@dataclass
class Opt:
    amount: float
    direction: str


def scrape(image, image_1, image_2, data: Tuple[List, List], height, width, opt: Opt):
    d1, d2 = data

    block_length = len(d1)
    f = fft(block_length)
    bins1 = f.rdo(f(fvec(d1)))
    bins2 = f.rdo(f(fvec(d2)))

    level = level_lin(fvec(d1 + d2))

    if opt.direction == 'y':
        source = image_1
        modulator = image_2
        target = image
        dim = width
        glow = (11, 1)
    else:
        source = image_1.T
        modulator = image_2.T
        target = image.T
        dim = height
        glow = (1, 11)

    kernel = np.array([[-1.0, -1.0],
                       [2.0, 2.0],
                       [-1.0, -1.0]])

    kernel = kernel/(np.sum(kernel) if np.sum(kernel) != 0 else 1)

    for i, t in enumerate(target):
        for j, _ in enumerate(t):
            index = int(j * (opt.amount * modulator[i][j]) / 255) % dim
            target[i][j] += source[i][index]

    img_blurred = cv2.GaussianBlur(cv2.filter2D(image, -1, kernel), glow, 1)

#    for i, t in enumerate(target):
#        s1 = bins1[i % block_length]
#        for j, pixel in enumerate(t):
#            s2 = bins2[(i * dim + j) % block_length]
#            pixel_slice = target[i].take(
#                range(j, j + 100 + int((s1 + s2) * 100)),
#                mode='wrap'
#            )
#            for x, v in enumerate(sorted(pixel_slice)):
#                y = ((j + x) % dim) - 1
#                target[i][y] = v

    return cv2.addWeighted(image, 1, img_blurred, 1, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Offset image pixels by another image modulated by the audio frame'
    )
    parser.add_argument('images', metavar='images', nargs='+', type=str,
        help='images or image directories'
    )
    parser.add_argument('-s', '--soundfile', action='store', type=str,
        help='soundfile'
    )
    parser.add_argument('-a', '--amount', action='store', type=float, default=1,
        help='effect strength'
    )
    parser.add_argument('-A', '--amplify', action='store', type=float, default=1.0,
        help='amplify audio frames'
    )
    parser.add_argument('-d', '--direction', action='store', type=str, default='x',
        help='shift direction: x or y'
    )
    parser.add_argument('-o', '--outdir', action='store', default='/tmp/',
        help='output directory'
    )
    parser.add_argument('-W', '--width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', type=int, action='store', default=720,
        help='height'
    )
    parser.add_argument('-f', '--fps', type=int, action='store', default=25,
        help='frames per second'
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    data = data * args.amplify

    blocksize: int = meta.rate // args.fps
    blocks: int    = meta.samples // blocksize

    image_set_1 = glob(args.images[0])
    image_set_2 = glob(args.images[1])

    opt = Opt(direction=args.direction, amount=args.amount)

    for n, (block, image_1, image_2) in enumerate(
        zip(
            audio_chunks(data, blocksize),
            cycle(image_set_1),
            cycle(image_set_2)
        )
    ):
        padded = "{0:05d}".format(n)
        bitmap_1 = cv2.imread(image_1, cv2.IMREAD_GRAYSCALE)
        bitmap_2 = cv2.imread(image_2, cv2.IMREAD_GRAYSCALE)
        height, width = bitmap_1.shape
        bitmap = np.zeros((height, width), np.uint8)

        if meta.channels == 2:
            block_channels = (block.T[0], block.T[1])
        else:
            block_channels = np.array_split(data, 2)

        image = scrape(
            bitmap,
            bitmap_1,
            bitmap_2,
            block_channels,
            height,
            width,
            opt
        )
        cv2.resize(image, (args.width, args.height))
        cv2.imwrite(path.join(args.outdir, f'{padded}.png'), image)

        percent_finished = int(n / blocks * 100)
        print(f'{percent_finished:>3}%', end='\r', flush=True)
