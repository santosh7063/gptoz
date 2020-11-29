#!/usr/bin/env python3
import argparse
import cv2
import numpy as np
from os import path
from glob import glob
from itertools import cycle
from audiopack import loadwav, audio_chunks, spectrum
from scipy.signal import fftconvolve


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
    parser.add_argument('-a', '--amplify', dest='amplify', type=float, action='store', default=100,
        help='amplify weak signal or spectrum'
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

    files = glob(args.infile)
    if args.shape:
        try:
            shape = tuple(map(int, args.shape.split(',')))
            assert len(shape) == 2
        except (AssertionError, ValueError):
            print('Can not parse shape parameter, must be: x,y')
    else:
        shape = None

    for n, data_pair in enumerate(zip(audio_chunks(data, blocksize), cycle(files))):
        block, imgfile = data_pair
        padded = "{0:05d}".format(n)
        bitmap = cv2.imread(imgfile, cv2.IMREAD_GRAYSCALE)
        if args.mode == 'fft':
            block = spectrum(block, meta.rate) * args.amplify
        if shape:
            block = np.reshape(block, shape)

        image = fftconvolve(bitmap, block, mode='same')
        cv2.imwrite(path.join(args.outdir, f'{padded}.png'), image)

        percent_finished = int(n / blocks * 100)
        print(f'{percent_finished:>3}%', end='\r', flush=True)
