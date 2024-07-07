#!/usr/bin/env python3
import os
import argparse
import cv2
import numpy as np
import audiopack as ap
import lib
from itertools import zip_longest


def triple(i):
    return (i, i, i)


def group(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def render_frame(*args, raw=False):
    if raw:
        return render_frame_raw(*args)
    else:
        return render_frame_spectrum(*args)


def render_frame_raw(img, data, blocksize, width, height):
    data = np.abs(data * 255)
    offset = len(data) // height
    new_block = np.resize(data, (height, offset, 3))
    img[:, -offset:] = new_block
    return img


def render_frame_spectrum(img, data, blocksize, width, height):
    #    spectrum = [triple(255 * (0, 1)[s > -0.5 and s < 0.5]) for s in rfft(data)]
    spectrum = np.abs(data / np.linalg.norm(data))
    offset = len(spectrum) // height
    new_block = np.full((height, offset, 3), 0, dtype=np.uint8)
    for x1, y1, x2, y2 in group(spectrum, 4, 0):
        pt1 = (int(width * x1), int(10 * height * y1))
        pt2 = (int(width * x2), int(10 * height * y2))
        cv2.rectangle(new_block, pt1, pt2, (255, 255, 255), cv2.FILLED)

    #    new_block = np.resize(spectrum, (height, offset, 3))
    img[:, -offset:] = np.flipud(new_block)
    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create scrolling strips of imagery from spectrum"
    )
    parser.add_argument("audiofile", metavar="audiofile", type=str, help="Audiofile")
    parser.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        action="store",
        default="/tmp",
        help="directory to write frames to",
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
        "-f",
        "--fps",
        dest="fps",
        type=int,
        action="store",
        default=25,
        help="video framerate",
    )
    parser.add_argument(
        "-R", "--raw", dest="raw", action="store_true", help="use raw audio buffer"
    )
    parser.add_argument(
        "-s",
        "--startframe",
        dest="start",
        type=int,
        action="store",
        default=1,
        help="start frame",
    )
    parser.add_argument(
        "-l",
        "--length",
        dest="length",
        type=int,
        action="store",
        default=0,
        help="length",
    )
    parser.add_argument(
        "-r", "--rate", dest="rate", type=float, action="store", help="rate"
    )
    args = parser.parse_args()

    image = np.zeros((args.height, args.width, 3), dtype=np.uint8)
    meta, audio = ap.loadwav(args.audiofile)

    blocksize = meta.rate // args.fps
    blocks = meta.samples // blocksize
    scroll = blocksize // args.height
    last_img = None
    for i, block in enumerate(ap.audio_chunks(audio, blocksize)):
        img = last_img if last_img is not None else image
        img = render_frame(
            img,
            block.T[0] if meta.channels > 1 else block,
            blocksize,
            args.width,
            args.height,
            raw=args.raw,
        )
        cv2.imwrite(os.path.join(args.outdir, "{0:05d}.png".format(i + 1)), img)
        last_img = np.zeros(img.shape, img.dtype)
        # scroll left
        last_img[:, 0 : args.width - scroll] = img[:, scroll:]
        # progress
        lib.progress(i, blocks)
