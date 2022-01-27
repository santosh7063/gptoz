#!/usr/bin/env python3

import argparse
import cv2
import numpy as np
from os import path
from glob import glob
from itertools import cycle
from aubio import fvec, level_lin
from audiopack import loadwav, audio_chunks, spectrum
from scipy.signal import fftconvolve
from scipy.interpolate import interp1d


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convolve a series of images with audio frames'
    )
    parser.add_argument('soundfile', metavar='soundfile', type=str,
        help='soundfile'
    )
    parser.add_argument('-i', '--infile', dest='infile', action='store',
        help='image file(s)'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp/',
        help='output directory'
    )
    parser.add_argument('-s', '--shape', dest='shape', type=str, action='store',
        help='shape audio block: 84,42'
    )
    parser.add_argument('-m', '--mode', dest='mode', type=str, action='store', default='signal',
        help='signal: time domain, fft: frequency domain'
    )
    parser.add_argument('-n', '--negative', dest='negative', action='store_true',
        help='negative'
    )
    parser.add_argument('-M', '--mix', dest='mix', action='store_true',
        help='mix by loudness'
    )
    parser.add_argument('-a', '--amplify', dest='amplify', type=float, action='store',
        help='amplify signal or spectrum'
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
    parser.add_argument('-t', '--trigger', dest='trigger', action='store_true',
        help='Stabilize on waveform features'
    )
    parser.add_argument('--start', dest='start', type=int, action='store', default=0,
        help='Start frame'
    )
    parser.add_argument('--length', dest='length', type=int, action='store', default=0,
        help="Length in video frames"
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    blocksize: int = meta.rate // args.fps
    blocks: int    = meta.samples // blocksize

    start: int = args.start
    length = args.length if args.length > 0 else blocks-start

    files = glob(args.infile)
    if args.shape:
        try:
            shape = tuple(map(int, args.shape.split(',')))
            assert len(shape) == 2
        except (AssertionError, ValueError):
            print('Can not parse shape parameter, must be: x,y')
    else:
        shape = None

    if args.amplify is None:
        if args.mode == 'fft':
            amplify = 100
        elif args.mode == 'signal':
            amplify = 1
    else:
        amplify = args.amplify

    for n, data_pair in enumerate(zip(audio_chunks(data, blocksize), cycle(files))):
        if n < start:
            continue
        if n > start+length:
            break

        block, imgfile = data_pair
        padded = "{0:05d}".format(n)
        bitmap = cv2.imread(imgfile, cv2.IMREAD_GRAYSCALE)
        level = level_lin(fvec(block.T[0]))

        if args.mode == 'fft' and args.mix:
            block = spectrum(block, meta.rate, bins=(1 + int(level * blocksize)))
        elif args.mode == 'fft':
            block = spectrum(block, meta.rate)
        elif args.mode == 'signal' and args.mix:
#            block = np.resize(block, (1 + int(level * blocksize), ))
            block = block[0:1 + int(level * blocksize)]

        if shape:
            block = np.reshape(block, shape)
        if args.negative:
            block = np.max(block) / 2 - block

        image = fftconvolve(bitmap, block * amplify, mode='same')

        cv2.imwrite(path.join(args.outdir, f'{padded}.png'), image)

        percent_finished = int(n / blocks * 100)
        print(f'{percent_finished:>3}%', end='\r', flush=True)
