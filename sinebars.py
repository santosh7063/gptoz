#!/usr/bin/env python3
from __future__ import division
import os
import argparse
from math import pi, e, sin, cos
from drawSvg import Drawing, Rectangle


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw sinebars')
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frame images to'
    )
    parser.add_argument('-n', '--numbars', dest='numbars', type=int, action='store', default=1,
        help='number of bars'
    )
    parser.add_argument('-i', '--iterations', dest='iterations', type=int, action='store', default=25,
        help='frames to render'
    )
    parser.add_argument('-W', '--width', dest='width', type=int, action='store', default=1280,
        help='width'
    )
    parser.add_argument('-H', '--height', dest='height', type=int, action='store', default=720,
        help='height'
    )
    args = parser.parse_args()

    for n in range(args.iterations):

        drawing = Drawing(args.width, args.height, origin=(0, 0))
        padded = "{0:03d}".format(n)

        cycle = n / args.iterations * 2 * pi
        max_height = args.height / 10
        half_height = args.height / 2

        for i in range(args.numbars):
            height = sin(cycle / 2) * max_height / (i + 1)
            y = half_height + cos(cycle / (i + 1)) * half_height
            rect = Rectangle(0, y, args.width, height, fill='white')
            drawing.append(rect)

        drawing.saveSvg(os.path.join(args.outdir, "sinebars_"+padded+'.svg'))
