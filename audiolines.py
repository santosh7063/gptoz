#!/usr/bin/env python3
from __future__ import division
import os
import argparse
import numpy as np
from audiopack import loadwav, audio_chunks
from videopack import render_frame
from drawSvg import Drawing


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw hectic lines from audiobuffer')
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

    blocksize  = meta.rate // args.fps
    blocks     = meta.samples // blocksize

    for n, b in enumerate(audio_chunks(data, blocksize)):
        padded = "{0:03d}".format(n)
        drawing = Drawing(args.width, args.height, origin=(0, 0))

        if len(b) < blocksize:
            b = np.lib.pad(b, ((blocksize-len(b)) // 2), 'constant')
        if args.multichannel and meta.channels > 1:
            reflect = [(1,1), (-1,1), (1,-1), (-1,-1)]
            for i in range(meta.channels - 1):
                drawing = render_frame(
                    drawing,
                    b.T[i],
                    width=args.width,
                    height=args.height,
                    reflect=reflect[i % meta.channels]
                )
        else:
            if meta.channels > 1:
                b = b.T[0]
            drawing = render_frame(
                drawing,
                b,
                width=args.width,
                height=args.height
            )

        drawing.saveSvg(os.path.join(args.outdir, "audiosvg_"+padded+'.svg'))
