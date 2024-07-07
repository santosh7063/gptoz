#!/usr/bin/env python3
import sys
import os.path
import argparse
import numpy as np
import cv2
from audiopack import loadwav, audio_chunks, spectrum, rms
from lib import progress


def gray_frame(img, spectrum, spread, blocksize, height):
    for n, f in enumerate(spectrum):
        c = np.uint8(f * spread * 255)
        yoff = int(height / 2 * n / blocksize)
        if n % 2 == 0:
            yoff = -yoff
        row = int(height / 2) + yoff
        img[row] += (c, c, c)
    return img


def render_frame(img, spectrum, threshold, thickness, spread, width, height):
    blocksize = len(spectrum)
    if threshold == 0:
        return gray_frame(img, spectrum, spread, blocksize, height)

    for n, f in enumerate(spectrum):
        if np.abs(f) > threshold:
            try:
                barsize = thickness * (f * spread + 1 / n) ** 2
            except ZeroDivisionError:
                barsize = 0

            yoff = int(height / 2 * n / blocksize * spread / 2.0)
            if n % 2 == 0:
                yoff = -yoff
            p1 = (0, height // 2 - yoff - int(barsize))
            p2 = (width, height // 2 - yoff + int(barsize))
            cv2.rectangle(img, p1, p2, (255, 255, 255), cv2.FILLED)

    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Draw the audio spectrum as horizontal bars with thickness \
                     indicating strength and position frquency bucket"
    )
    parser.add_argument("soundfile", metavar="soundfile", type=str, help="soundfile")
    parser.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        action="store",
        default="/tmp",
        help="directory to write frame images to",
    )
    parser.add_argument(
        "-m",
        "--multichannel",
        dest="multichannel",
        action="store_true",
        help="multichannel",
    )
    parser.add_argument(
        "-f",
        "--fps",
        dest="fps",
        type=int,
        action="store",
        default=25,
        help="video framerate",
    )
    parser.add_argument(
        "-W",
        "--width",
        dest="width",
        type=int,
        action="store",
        default=1280,
        help="width",
    )
    parser.add_argument(
        "-H",
        "--height",
        dest="height",
        type=int,
        action="store",
        default=720,
        help="height",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        type=float,
        action="store",
        default=0.1,
        help="threshold. if set to zero, values are grayscaled",
    )
    parser.add_argument(
        "-T",
        "--thickness",
        dest="thickness",
        type=float,
        action="store",
        default=1,
        help="threshold. if set to zero, values are grayscaled",
    )
    parser.add_argument(
        "-s",
        "--spread",
        dest="spread",
        type=float,
        action="store",
        default=1.0,
        help="spread. if set to zero will try and follow block energy",
    )
    args = parser.parse_args()

    meta, data = loadwav(args.soundfile)

    print("Samplerate: %d" % meta.rate)
    print("Channels: %d" % meta.channels)
    print("Length: %d samples, %d seconds" % (meta.samples, meta.seconds))

    blocksize = meta.rate // args.fps
    blocks = meta.samples // blocksize

    print("%d Frames at %d samples" % (blocks, blocksize))
    term_width = 100

    N = blocksize
    T = 1.0 / blocksize * 1.25
    for n, b in enumerate(audio_chunks(data, blocksize)):
        img = np.zeros((args.height, args.width, 3), np.uint8)
        if args.multichannel and meta.channels > 1:
            reflect = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            for i in range(meta.channels - 1):
                img = render_frame(
                    img,
                    spectrum(b.T[i], N),
                    threshold=args.threshold,
                    thickness=args.thickness,
                    spread=args.spread or rms(b.T[i]) * 4,
                    width=args.width,
                    height=args.height,
                )
        else:
            if meta.channels > 1:
                b = b.T[0]
            img = render_frame(
                img,
                spectrum(b, N),
                threshold=args.threshold,
                thickness=args.thickness,
                spread=args.spread or rms(b) * 4,
                width=args.width,
                height=args.height,
            )
        cv2.imwrite(os.path.join(args.outdir, "{0:05d}.png".format(n + 1)), img)
        progress(n, blocks)

    sys.stdout.write("\n")
