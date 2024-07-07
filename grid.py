from sys import stdout
import argparse
import os
import cv2
import numpy as np
import random
from lib import progress


class Grid:

    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.clear()

    def randomize(self):
        self._grid = [
            [random.randint(0, 1) for cell in range(self.width)]
            for line in range(self.height)
        ]

    def clear(self):
        self._grid = [[0 for cell in range(self.width)] for line in range(self.height)]

    def glider(self):
        self.set_cell(0, 1, 1)
        self.set_cell(1, 2, 1)
        self.set_cell(2, 0, 1)
        self.set_cell(2, 1, 1)
        self.set_cell(2, 2, 1)

    @property
    def array(self):
        return np.array(self._grid)

    def get_row(self, i):
        return self._grid[i]

    def get_column(self, i):
        return [cell[i] for cell in self._grid[i]]

    def get_cell(self, x, y):
        return self._grid[y][x]

    def set_cell(self, x, y, value):
        self._grid[y][x] = value

    def from_bitmap(self, image):
        self.height, self.width = image.shape
        self._grid = image.clip(0, 1).tolist()

    def get_neighbours(self, x, y):
        ns = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if not (i == 0 and j == 0):
                    ns.append(
                        self.get_cell(
                            (x + i) % self.width,
                            (y + j) % self.height,
                        )
                    )
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

    def gul(self, x, y, cell):
        neighbours = self.get_neighbours(x, y)
        s = sum(neighbours)
        if s % 2 == 0:
            return 0
        else:
            return 1

    def step(self, rules="gol"):
        grid = []
        for y, row in enumerate(self._grid):
            grid.append(row.copy())
            for x, cell in enumerate(row):
                grid[y][x] = getattr(self, rules)(x, y, cell)
        self._grid = grid


if __name__ == "__main__":
    """
    Run a game of life
    """
    ap = argparse.ArgumentParser("Cellular Automata Playground")
    ap.add_argument(
        "-i",
        "--iterations",
        dest="iterations",
        type=int,
        action="store",
        default=99,
    )
    ap.add_argument(
        "-r",
        "--rules",
        dest="rules",
        action="store",
        default="gol",
        help="ruleset algorithms\n" + "gol :: conways game of life\n",
    )
    ap.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        action="store",
        default="/tmp",
        help="output dir",
    )
    ap.add_argument(
        "-W",
        "--width",
        dest="width",
        type=int,
        action="store",
        default=200,
        help="width",
    )
    ap.add_argument(
        "-H",
        "--height",
        dest="height",
        type=int,
        action="store",
        default=80,
        help="height",
    )
    ap.add_argument(
        "-I", "--image", dest="image", action="store", help="init grid from image."
    )
    args = ap.parse_args()

    gol = Grid(width=args.width, height=args.height)

    if args.image:
        image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
        _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        cv2.imshow("image window", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        gol.from_bitmap(image)
    else:
        gol.randomize()

    print(f"writing {args.iterations} frames to {args.outdir}")
    for i in range(args.iterations):
        cv2.imwrite(os.path.join(args.outdir, "{:05d}.png".format(i)), gol.array * 255)
        gol.step(rules=args.rules)
        progress(i, args.iterations)

    stdout.write("\n")
