#!/usr/bin/env python3
import sys
import argparse
import cv2
import numpy as np
from scipy.io import wavfile
"""
Plot audio samples as pixels in an image bitmap
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='convert audiofile to image bitmap'
    )
    parser.add_argument('soundfile', metavar='soundfile', type=str,
        help='soundfile'
    )
    parser.add_argument('-o', '--outfile', dest='outfile', action='store', default='/tmp/output.png',
        help='output file'
    )
    parser.add_argument('-m', '--multichannel', dest='multichannel', action='store_true',
        help='multichannel'
    )
    parser.add_argument('-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    args = parser.parse_args()

    rate, raw = wavfile.read(args.soundfile)
    data = np.asarray(raw)
    if args.width * args.height < len(data):
        print('bitmap too small')
        sys.exit(-1)

    bitmap = np.zeros((args.height, args.width, 3), np.uint8)
    for line in range(args.height):
        for pixel in range(args.width):
            linear_pixel = line * args.height + pixel
            if linear_pixel < len(data):
                bitmap[line, pixel] = [
                    data[linear_pixel, 0],
                    data[linear_pixel, 1],
                    data[linear_pixel, 0]
                ]

    cv2.imwrite(args.outfile, bitmap)
