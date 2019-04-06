#!/usr/bin/env python3
from __future__ import print_function
import os
import glob
import sys
import argparse
import cv2
import numpy as np


def error(msg):
    sys.stderr.write(msg)
    sys.exit(1)


def save_frame(args, number, frame):
    print("writing frame %06d" % number)
    cv2.imwrite(os.path.join(args.outdir, "frame_%06d.png"%number), frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create video feedback along a range of frames')
    parser.add_argument('imagedir', metavar='imagedir', type=str,
        help='directory with images to be whited out'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default=None,
        help='directory to write frame images to'
    )
    parser.add_argument('-a', '--amount', dest='amount', type=float, action='store', default=0.1,
        help='feedback amplification 0.0..1.0'
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
    parser.add_argument('-t', '--type', dest='type', action='store', default='png',
        help='source image type'
    )
    parser.add_argument('-r', '--rate', dest='rate', type=float, action='store',
        help='rate'
    )
    args = parser.parse_args()

    if os.path.isdir(args.imagedir):
        imagefiles = sorted([
            os.path.join(args.imagedir, f)
            for f in glob.glob(os.path.join(args.imagedir, '*.%s' % args.type))
            if os.path.isfile(os.path.join(args.imagedir, f))
        ])
    else:
        error('source image directory not found')

    bitmap = cv2.imread(imagefiles[0])
    if bitmap is None:
        print("Problem with the first Imagefile '%s'" % imagefiles[0])
        sys.exit(-1)

    width, height, colors = bitmap.shape

    oldframe = np.zeros((width, height, 3), np.uint8)
    start = args.start - 1
    length = args.length if args.length > 0 else len(imagefiles)-start

    print("%d frames, starting at %d" % (len(imagefiles), start))

    for n, imgf in enumerate(imagefiles):
        if n >= start and n < start+length:
            bitmap = cv2.imread(imgf)
            if bitmap is None:
                continue
            frame = bitmap.copy()
        if n > start and n < start+length:
            if args.rate is None:
                # fixed rate
                frame = frame + args.amount * cv2.GaussianBlur(oldframe, (3, 3), args.blur)
            else:
            # changing rate>>
                rate  = float(n-start)/float(length)
                feedback = ((np.exp(rate)/np.e)**2 + 0.01) * args.rate
                frame = frame + feedback * cv2.GaussianBlur(oldframe, (3, 3), args.blur)
            if args.outdir is not None:
                print("writing frame %06d" % n)
                save_frame(args, n, frame)
            else:
                print("writing frame %s" % imgf)
                cv2.imwrite(imgf, frame)
            oldframe = frame
