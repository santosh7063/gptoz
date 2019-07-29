#!/usr/bin/env python3
import sys
import os.path
import argparse
import numpy as np
import scipy.fftpack
import cv2
from audiopack import loadwav, audio_chunks
from lib import progress


def spectrum(block, N):
    s = scipy.fftpack.fft(block)
    return 2.0/N * np.abs(s[:N//2])


def render_frame(img, spectrum, threshold, width, height):
    for n, f in enumerate(spectrum):
        if np.abs(f) > threshold:
            p1 = (0, height // 2)
            for x in range(width-1):
                y = f*np.sin(float(n)*(float(x)/float(width)))
                if n % 2 == 0:
                    y *= -1.
                p2 = (x+1, int(y*height + height/2))
                cv2.line(img, p1, p2, (255, 255, 255), lineType=cv2.LINE_AA)
                p1 = p2
    return img


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
    parser.add_argument('-t', '--threshold', dest='threshold', type=float, action='store', default=0.1,
        help='threshold'
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
    for n, b in enumerate(audio_chunks(data, blocksize)):
        padded = "{0:05d}".format(n+1)
        img = np.zeros((args.height, args.width, 3), np.uint8)
        if args.multichannel and meta.channels > 1:
            reflect = [(1,1), (-1,1), (1,-1), (-1,-1)]
            for i in range(meta.channels-1):
                img = render_frame(
                    img,
                    spectrum(b.T[i], N),
                    threshold=args.threshold,
                    width=args.width,
                    height=args.height
                )
        else:
            if meta.channels > 1:
                b = b.T[0]
            img = render_frame(
                img,
                spectrum(b, N),
                threshold=args.threshold,
                width=args.width,
                height=args.height
            )
        cv2.imwrite(os.path.join(args.outdir, '%s.png' % padded), img)
        progress(n, blocks)

    sys.stdout.write("\n")
