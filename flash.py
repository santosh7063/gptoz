# -*- coding: utf-8 -*-
from __future__ import print_function, division
import sys
import math
import random
from numpy import dot
from drawSvg import Drawing, Path


def angle_between(v1, v2):
    u = v1.normal_form
    v = v2.normal_form
    try:
        return math.acos(
            dot(u, v) / dot(v1.length, v2.length)
        )
    except ValueError:
        print('value error: {0!r} {1!r}'.format(u, v))
        return math.pi


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
            self.y >= 0 and self.y <= y
        )

    def within_perimeter(self, other, r):
        return Vector(self, other).length < r


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
    def normal_form(self):
        """
        B - A, assume 0, 0 origin
        """
        return (self.a.x - self.b.x, self.a.y - self.b.y)

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

    def __init__(self, width=500, height=500, start=None, end=None):
        self.width = width
        self.height = height
        self.start = start or Point(width // 2, height)
        self.end = end or Point(width // 2, 0)
        self._nodes = []
        self._nodes.append(self.start)

    def __str__(self):
        return ' → '.join(map(str, self._nodes))

    def __repr__(self):
        return '<Flash {}>'.format(id(self))

    def __len__(self):
        return len(self._nodes)

    @property
    def current_node(self):
        return self._nodes[-1:][0]

    def current_point(self):
        return self.points[-1:][0]

    def random_point(self, x=10, y=10):
        current = self.current_point()
        return Point(
            current.x + random.randint(1, x) - x // 2,
            current.y + random.randint(1, y) - y // 2
        )

    def random_walk(self, length=random.randint(1, 10), data=0.0, mix=0.0):
        """
        Create a segment in a zig-zag path towards the end point
        :param number:
            length of the segment
        :param float:
            range -1..1 fixed influence on the deflector
        :param float:
            range 0..1 how to mix fixed with random value
        """
        def next_node(length):
            try:
                a, b = self.points[-2:]
            except ValueError:
                return self.random_point(10, 10)

            deflect = random.random() * (1. - mix) + data * mix
            factor = random.randint(-1, 1)
            if factor == 0:
                # why is it off?
                new_angle = math.pi / 2 - Vector(b, self.end).phi + (deflect - 0.5)
                length = length ** 2
            else:
                new_angle = math.pi / 2 - factor * deflect * math.pi / 2

            nv = Vector.from_polar(b, new_angle, length)
            return b.translate(*nv.ab)

        node = next_node(length)
        retry = 10
        while not node.within_limits(self. width, self.height):
            node = next_node(length)
            retry -= 1
            # safety catch against infinite looping
            if retry == 0:
                node = self.random_point()
                break
        self.add_node(node)

    def add_node(self, node=None):
        if node is None:
            node = self.random_point()
        self._nodes.append(node)

    @property
    def flashes(self):
        return [n for n in self._nodes if isinstance(n, Flash)]

    @property
    def points(self):
        return [n for n in self._nodes if isinstance(n, Point)]

    @property
    def edges(self):
        return [
            Vector(self.points[i], p)
            for i, p in enumerate(self.points[1:])
        ]

    @property
    def path(self):
        path = Path(
            stroke_width=1,
            stroke='black',
            fill='black',
            fill_opacity=0.0,
            stroke_miterlimit=25 # keep it pointy
        )
        path.M(self.start.x, self.start.y)
        for node in self.points[1:]:
            path.L(node.x, node.y)

        return path

    def render_path(self, thickness=1.0):
        """
        Render double lined, filled flash path
        """
        path = Path(
            stroke_width=1,
            stroke='black',
            fill='black',
            fill_opacity=1.0,
            stroke_miterlimit=99 # keep it pointy
        )
        path.M(self.start.x, self.start.y)

        for node in self.points[1:]:
            path.L(node.x, node.y)

        backflash = []
        for i, v1 in enumerate(self.edges):
            lp = len(self.points)
            if i < lp - 2:
                v2 = self.edges[i + 1]
                assert v1.b == v2.a
                phi = angle_between(v1, v2)
                distance = thickness - (thickness / (i + 1))
                point = Vector.from_polar(v1.b, phi, distance)
                backflash.append(point)

        for p in reversed(backflash):
            path.L(p.b.x, p.b.y)

        path.Z()
        return path

    def render(self, drawing=None, thickness=1.0):
        drawing = drawing or Drawing(self.width, self.height, origin=(0, 0))
        drawing.append(self.render_path(thickness))
        return drawing


if __name__ == '__main__':
    try:
        nodes = int(sys.argv[1])
    except (ValueError, IndexError):
        nodes = 23

    flash = Flash()
    flashes = [flash]
    current = 0
    for _ in range(nodes):
        if flash.current_point().within_perimeter(flash.end, 10):
            flash = Flash()
            flashes.append(flash)
            current += 1
        flash.random_walk()

    drawing = Drawing(500, 500, origin=(0, 0))
    for flash in flashes:
        drawing.append(flash.render_path())
    drawing.saveSvg('/tmp/flash.svg')
