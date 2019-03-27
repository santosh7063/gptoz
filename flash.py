# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math
import random
from drawSvg import Drawing, Path


class Point(object):

    def __init__(self, x=0.0, y=0.0):
        self._point = (x, y)

    def __repr__(self):
        return '<{0}, {1}>'.format(self.x, self.y)

    @property
    def x(self):
        return self._point[0]

    @x.setter
    def x(self, value):
        self._point[0] = value

    @property
    def y(self):
        return self._point[1]

    @y.setter
    def y(self, value):
        self._point[1] = value

    def translate(self, x, y):
        return Point(
            self.x + x,
            self.y + y
        )

    def within_limits(self, x, y):
        return (
            self.x >= 0 and self.x <= x
            and
            self.y >= 0 and self.y<= y
        )


class Vector(object):

    def __init__(self, a: Point, b: Point):
        if not isinstance(a, Point):
            raise TypeError('a must be Point')
        elif not isinstance(b, Point):
            raise TypeError('b must be Point')
        else:
            self._vector = (a, b)

    def __repr__(self):
        return '<Vector {0!r}, {1!r}>'.format(self.a, self.b)

    @staticmethod
    def from_polar(start, phi, length):
        end = Point(
            start.x + length * math.cos(phi),
            start.y + length * math.sin(phi),
        )
        return Vector(start, end)

    @property
    def a(self):
        return self._vector[0]

    @property
    def b(self):
        return self._vector[1]

    @a.setter
    def a(self, value: Point):
        self._vector[0] = value

    @b.setter
    def b(self, value: Point):
        self._vector[1] = value

    @property
    def ab(self):
        return self.b.x - self.a.x, self.b.y - self.a.y

    @property
    def length(self):
        ab = self.ab
        return math.sqrt(ab[0] ** 2 + ab[1] ** 2)

    @property
    def heading(self):
        ab = self.ab
        length = self.length
        return ab[0] / length, ab[1] / length

    @property
    def phi(self):
        x, y = self.heading
        return math.atan2(x, y)


class Flash(object):

    _nodes = []

    def __init__(self, width=500, height=500, start=None, end=None):
        self.width = width
        self.height = height
        self.start = start or Point(width // 2, height)
        self.end = end or Point(width // 2, 0)
        self._nodes.append(self.start)

    def __str__(self):
        return ' → '.join(map(str, self._nodes))

    def current_point(self):
        return self._nodes[-1:][0]

    def random_point(self, x=10, y=10):
        current = self.current_point()
        return Point(
            current.x + random.randint(1, x) - x // 2,
            current.y + random.randint(1, y) - y // 2
        )

    def random_walk(self, length=random.randint(1, 10), bias=0):
        def next_node(length):
            try:
                a, b = self._nodes[-2:]
            except ValueError:
                return self.random_point(10, 10)

            rand = random.random()
            factor = random.randint(-1, 1)
            if factor == 0:
                # why is it off?
                new_angle = math.pi / 2 - Vector(b, self.end).phi + (rand - 0.5)
                length = length ** 2
            else:
                new_angle = math.pi / 2 - factor * rand * math.pi / 2

            nv = Vector.from_polar(b, new_angle, length)
            return b.translate(*nv.ab)

        node = next_node(length)
        while not node.within_limits(self. width, self.height):
            node = next_node(length)
        self.add_point(node)

    def add_point(self, point=None):
        if point is None:
            point = self.random_point()
        self._nodes.append(point)

    def render(self):
        drawing = Drawing(self.width, self.height, origin=(0, 0))
        path = Path(
            stroke_width=1,
            stroke='black',
            fill='black',
            fill_opacity=0.0
        )
        path.M(self.start.x, self.start.y)
        for node in self._nodes[1:]:
            path.L(node.x, node.y)

        path.L(self.end.x, self.end.y)
        drawing.append(path)
        drawing.saveSvg('/tmp/flash.svg')


if __name__ == '__main__':

    nodes = 99
    flash = Flash()
    for n in range(nodes):
        flash.random_walk()
    flash.render()
