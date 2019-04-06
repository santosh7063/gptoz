# -*- coding: utf-8 -*-
from __future__ import print_function, division
import cv2
import numpy as np
import random
from lib import progress


class Grid(object):

    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self._grid = [
            [0 for cell in range(width)]
            for line in range(height)
        ]

    def randomize(self):
        self._grid = [
            [random.randint(0, 1) for cell in range(self.width)]
            for line in range(self.height)
        ]

    @property
    def array(self):
        return np.array(self._grid)

    def get_cell(self, x, y):
        return self._grid[y][x]

    def get_neighbours(self, x, y):
        ns = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if not (i == 0 and j == 0):
                    ns.append(self.get_cell(
                        (x + i) % self.width,
                        (y + j) % self.height,
                    ))
        return ns

    def gol(self, x, y, cell):
        neighbours = self.get_neighbours(x, y)
        s = sum(neighbours)
        if s == 3:
            return 1
        elif s == 2:
            return cell
        else:
            return 0

    def step(self, rules='gol'):
        grid = self._grid.copy()
        for y, line in enumerate(self._grid):
            for x, cell in enumerate(line):
                grid[y][x] = getattr(self, rules)(x, y, cell)
        self._grid = grid


if __name__ == '__main__':

    gol = Grid(width=100, height=60)
    gol.randomize()
    for i in range(99):
        gol.step(rules='gol')
        cv2.imwrite('/tmp/{:03d}.png'.format(i), gol.array)
        progress(i, 99)
