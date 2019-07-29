#!/usr/bin/env python3
import os
import argparse
import cv2
import numpy as np
from scipy.fftpack import rfft
import audiopack as ap
import lib


def triple(i):
    return (i, i, i)

def render_frame(img, data, blocksize, width, height):
    spectrum = [triple(255 * (0, 1)[s > 0]) for s in rfft(data)]
    offset = len(spectrum) // height
    new_block = np.full(
        (height, offset, 3),
        0,
        dtype=np.uint8
    )
    new_block = np.resize(spectrum, (height, offset, 3))
    img[:,-offset:] = new_block
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='create video feedback along a range of frames'
    )
    parser.add_argument('audiofile', metavar='audiofile', type=str,
        help='Audiofile'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frames to'
    )
    parser.add_argument('-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument('-b', '--blur', dest='blur', type=float, action='store', default=5.0,
        help='blur amount'
    )
    parser.add_argument('-s', '--startframe', dest='start', type=int, action='store', default=1,
        help='start frame'
    )
    parser.add_argument('-l', '--length', dest='length', type=int, action='store', default=0,
        help='length'
    )
    parser.add_argument('-r', '--rate', dest='rate', type=float, action='store',
        help='rate'
    )
    args = parser.parse_args()

    image = np.zeros((args.height, args.width, 3), dtype=np.uint8)
    meta, audio = ap.loadwav(args.audiofile)

    blocksize = meta.rate // args.fps
    blocks = meta.samples // blocksize
    scroll = blocksize // args.height
    lastimg = None
    for i, block in enumerate(ap.audio_chunks(audio, blocksize)):
        img = lastimg if lastimg is not None else image
        img = render_frame(
            img,
            block.T[0] if meta.channels > 1 else block,
            blocksize,
            width=args.width,
            height=args.height
        )
        cv2.imwrite(os.path.join(args.outdir, '{0:05d}.png'.format(i+1)), img)
        lastimg = np.zeros(img.shape, img.dtype)
        # scroll left
        lastimg[:,0:args.width-scroll] = img[:,scroll:]
        # progress
        lib.progress(i, blocks)
