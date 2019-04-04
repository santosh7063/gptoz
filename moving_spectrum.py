#!/usr/bin/env python3
from __future__ import print_function, division
import os.path
from sys import stdout
import argparse
import numpy as np
import scipy.fftpack
from drawSvg import Drawing
from audiopack import loadwav, audio_chunks
from videopack import render_frame
from lib import progress


def spectrum(block):
    s = scipy.fftpack.fft(block)
    return 2.0/N * np.abs(s[:N//2])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw hectic lines from spectrum')
    parser.add_argument('soundfile', metavar='soundfile', type=str,
        help='soundfile'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frame images to'
    )
    parser.add_argument('-m', '--multichannel', dest='multichannel', action='store_true',
        help='multichannel'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument('-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    print("Samplerate: %d" % meta.rate)
    print("Channels: %d" % meta.channels)
    print("Length: %d samples, %d seconds" % (meta.samples, meta.seconds))

    blocksize  = meta.rate // args.fps
    blocks     = meta.samples // blocksize

    print("%d Frames at %d samples" % (blocks, blocksize))

    N = blocksize
    T = 1.0 / blocksize * 1.25
    for n, b in enumerate(audio_chunks(data, blocksize)):
        padded = "{0:03d}".format(n)
        drawing = Drawing(args.width, args.height, origin=(0, 0))
        if args.multichannel and meta.channels > 1:
            reflect = [(1,1), (-1,1), (1,-1), (-1,-1)]
            for i in range(meta.channels-1):
                scene = render_frame(
                    drawing,
                    spectrum(b.T[i]),
                    plotter='osci',
                    width=args.width,
                    height=args.height
                )
        else:
            if meta.channels > 1:
                b = b.T[0]
            scene = render_frame(
                drawing,
                spectrum(b),
                plotter='osci',
                width=args.width,
                height=args.height
            )
        drawing.saveSvg(os.path.join(args.outdir, "spectrum_"+padded+'.svg'))
        progress(n, blocks)

    stdout.write('\n')
