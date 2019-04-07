#!/usr/bin/env python
"""
Paint waveform for audiofile
"""
from __future__ import print_function, division
import sys, os
import argparse
from collections import namedtuple
import numpy as np
from scipy.io import wavfile
from drawSvg import Drawing, Path
from audiopack import pcm2float
from lib import progress


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def drawSamples(drawing, data, width=600, height=400, show_progress=False):
    size = len(data)
    grain = width / size
    path = Path(
        stroke_width=1,
        stroke='black',
        fill='black',
        fill_opacity=0.0,
    )
    path.M(0, height / 2)
    for i, d in enumerate(data):
        x = i * grain
        y = d * height * 0.5 + height * 0.5
        path.L(x, y)
        if show_progress:
            progress(i, size)

    drawing.append(path)
    return drawing


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Draw oscilloscope line from audiobuffer'
    )
    parser.add_argument(
        'soundfile', metavar='soundfile', type=str,
        help='soundfile'
    )
    parser.add_argument(
        '-o', '--out', dest='outfile', action='store', default='/tmp/test',
        help='filename to write to'
    )
    parser.add_argument(
        '-m', '--multichannel', dest='multichannel', action='store_true',
        help='multichannel'
    )
    parser.add_argument(
        '-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument(
        '-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument(
        '-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    parser.add_argument(
        '-l', '--line-width', dest='linewidth', type=int, action='store', default=1,
        help='height'
    )
    args = parser.parse_args()

    try:
        rate, raw = wavfile.read(args.soundfile)
    except ValueError:
        print("no audiofile provided")
        sys.exit()

    data = pcm2float(raw, 'float64')

    length = namedtuple('length', ['samples', 'seconds'])
    length.samples = len(data)
    length.seconds = length.samples / float(rate)

    blocksize  = rate // args.fps
    blocks     = length.samples // blocksize

    try:
        channels = data.shape[1]
        print("Channels: %d"%(channels))
    except IndexError:
        channels = 1
        print("Channels: 1")


    # if outfile is directory, write frames, else one big stripe
    if os.path.isdir(args.outfile):
        for n, b in enumerate(chunks(data, blocksize)):
            padded = "{0:06d}".format(n)
            if len(b) < blocksize:
                b = np.lib.pad(b, ((blocksize-len(b)) // 2), 'constant')
            if args.multichannel and channels > 1:
                reflect = [(1,1), (-1,1), (1,-1), (-1,-1)]
                for i in range(channels - 1):
                    drawing = Drawing(args.width, args.height)
                    drawing = drawSamples(drawing, b.T[i], args.width, args.height)
            else:
                if channels > 1:
                    b = b.T[0]
                drawing = Drawing(args.width, args.height)
                drawing = drawSamples(drawing, b, args.width, args.height)
            sys.stdout.write('frame: %s' % padded)
            sys.stdout.flush()
            sys.stdout.write("\b" * 13)
            drawing.saveSvg(
                os.path.join("%s/%s.svg" % (args.outfile, padded))
            )

    else:
        if args.multichannel and channels > 1:
            reflect = [(1,1), (-1,1), (1,-1), (-1,-1)]
            for i in range(channels - 1):
                drawing = Drawing(args.width, args.height)
                drawing = drawSamples(
                    drawing, data.T[i], args.width, args.height,
                    show_progress=True
                )
        else:
            if channels > 1:
                data = data.T[0]
            drawing = Drawing(args.width, args.height)
            drawing = drawSamples(
                drawing, data, args.width, args.height,
                show_progress=True
            )
        sys.stdout.write('\n')
        drawing.saveSvg(os.path.join(args.outfile))
