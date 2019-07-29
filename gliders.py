#/usr/bin/env python3
from __future__ import print_function, division
from sys import stdout
import argparse
import os
import cv2
import random
from grid import Grid
from lib import progress


class Glider(object):

    def __init__(self, width, height, x=None, y=None, length=10, speed=1):
        self.width = width
        self.height = height
        self.length = length
        self.speed = speed
        self.x = random.randint(0, width-1) if x is None else x
        self.y = random.randint(0, width-1) if y is None else y
        self.direction = self.direction_vector(random.randint(0, 3))
        self.trail = []

    def direction_vector(self, index):
        return (
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1)
        )[index]

    def turn_left(self):
        self.direction = (
            -self.direction[1],
            self.direction[0]
        )

    def turn_right(self):
        self.direction = (
            self.direction[1],
            -self.direction[0]
        )

    def move(self):
        self.trail = ([(self.x, self.y)] + self.trail)[:self.length]
        self.x = (self.x + self.speed * self.direction[0]) % self.width
        self.y = (self.y + self.speed * self.direction[1]) % self.height

    def add_to_grid(self, grid):
        grid[self.y][self.x] = 1
        for i, (x, y) in enumerate(self.trail):
            grid[y][x] = (1, 1, 1, 1, 1, 1, 0.9, 0.8, 0.4, 0.1)[i]
        return grid


class GliderFlock(Grid):

    def __init__(self, width=100, height=100, length=10, size=50, speed=None):
        super().__init__(width, height)
        self._gliders = [
            Glider(
                self.width,
                self.height,
                length=length,
                x=0, y=(i - size // 2) + self.height // 2,
                speed=speed or random.randint(1, 5)
            ) for i in range(size)
        ]

    def step(self):
        grid = []
        for y, row in enumerate(self._grid):
            grid.append(row.copy())

        for g in self._gliders:
            rand = random.randint(0, 100)
            if rand > 95:
                g.turn_left()
            elif rand > 90:
                g.turn_right()
            g.move()
            grid = g.add_to_grid(grid)

        self._grid = grid


if __name__ == '__main__':

    ap = argparse.ArgumentParser('Travelling Signal Line')
    ap.add_argument(
        '-i', '--iterations', dest='iterations', type=int, action='store',
        default=99,
    )
    ap.add_argument(
        '-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='output dir'
    )
    ap.add_argument(
        '-W', '--width', dest='width', type=int, action='store',
        default=100,
        help='width'
    )
    ap.add_argument(
        '-H', '--height', dest='height', type=int, action='store',
        default=100,
        help='height'
    )
    ap.add_argument(
        '-l', '--length', dest='length', type=int,  action='store',
        default=10,
        help='glider length'
    )
    ap.add_argument(
        '-s', '--size', dest='size', type=int,  action='store',
        default=50,
        help='flocksize'
    )
    ap.add_argument(
        '-S', '--speed', dest='speed', type=int,  action='store',
        help='glider speed. if not specified, speed is randomized 1..5'
    )
    args = ap.parse_args()

    flock = GliderFlock(
        width=args.width,
        height=args.height,
        length=args.length,
        size=args.size,
        speed=args.speed,
    )

    for i in range(args.iterations):
        flock.step()
        cv2.imwrite(
            os.path.join(args.outdir, '{:05d}.png'.format(i)),
            flock.array * 255
        )
        progress(i, args.iterations)

    stdout.write('\n')
