# -*- coding: utf-8 -*-
from drawSvg import Path
from math import pi, e, sin, cos, sqrt
import random
from audiopack import spectrum
from flash import Flash


 ##     ##     ##      ##     ##     ##     ##     ##     ##
#  #  ##  #  ##  #  ##   #  ##  #  ##  #  ##  #  ##  #  ##  #  #
#   ##     ##     ##      ##     ##     ##     ##     ##     ##
##
### Data visualization functions
##
#
def scatter(drawing, data, width, height, reflect, opts=None):
    """ plot pairs of samples as coordinates """
    path = Path(stroke_width=1, stroke='black', fill='black', fill_opacity=0.0)
    cx, cy = (width * 0.5, height * 0.5)
    path.M(cx, cy)
    for i in range(len(data) // 2):
        px = data[i*2:i*2+2][0]
        py = data[i*2:i*2+2][1]
        path.L(
            cx + width * px * 0.5 * reflect[0],
            cy + height * py * 0.5 * reflect[1]
        )

    drawing.append(path)
    return drawing


def osci(drawing, data, width, height, reflect, opts=None):
    """ Draw a path from left to right, sample on y """
    path = Path(stroke_width=1, stroke='black', fill='black', fill_opacity=0.0)
    path.M(0., height * 0.5)
    points = len(data)
    for i in range(points):
        x = i * width / points
        y = height * data[i] + height * 0.5
        path.L(x, y)

    drawing.append(path)
    return drawing


def cross(drawing, data, width, height, reflect, opts=None):
    path = Path(stroke_width=1, stroke='black', fill='black', fill_opacity=0.0)
    path.M(width * 0.5, height * 0.5)
    spec = spectrum(data, len(data))
    for i, j in zip(data, spec):
        x = i * width * 0.5 + width * 0.5
        y = (height * j * 0.5 * pi) + height * 0.5
        #y  = height * j * pi
        path.L(x, y)

    drawing.append(path)
    return drawing


def flash(drawing, data, width, height, reflect, opts=None):
    opts = opts or {}
    flash = Flash(width=width, height=height)
    flashes = [flash]
    nodes = len(data) // 2
    for i in range(nodes):
        if flash.current_point().within_perimeter(flash.end, 10):
            flash = Flash(width=width, height=height)
            flashes.append(flash)
        else:
            flash.random_walk(
                data[i] * random.randrange(1, 7) ** e,
                data[nodes-i-1],
                mix=0.0
            )

    for flash in flashes:
        drawing = flash.render(drawing, opts.get('thickness'))

    return drawing


def render_frame(drawing, data, plotter=None, width=600, height=400, reflect=(1, 1), opts=None):
    """ Wrap the renderer so different plugin plotters can be used """
    opts = opts or {}
    try:
        plotter = globals()[plotter]
    except KeyError:
        plotter = scatter
    return plotter(drawing, data, width, height, reflect, opts)
