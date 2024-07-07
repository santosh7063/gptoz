from drawSvg import Path
from math import pi, e
import random
from audiopack import spectrum, rms
from flash import Flash, Point


##     ##     ##      ##     ##     ##     ##     ##     ##
#  #  ##  #  ##  #  ##   #  ##  #  ##  #  ##  #  ##  #  ##  #  #
#   ##     ##     ##      ##     ##     ##     ##     ##     ##
##
### Data visualization functions
##
#
def scatter(drawing, data, width, height, reflect, opts=None):
    """plot pairs of samples as coordinates"""
    path = Path(stroke_width=1, stroke="black", fill="black", fill_opacity=0.0)
    cx, cy = (width * 0.5, height * 0.5)
    path.M(cx, cy)
    for i in range(len(data) // 2):
        px = data[i * 2 : i * 2 + 2][0]
        py = data[i * 2 : i * 2 + 2][1]
        path.L(cx + width * px * 0.5 * reflect[0], cy + height * py * 0.5 * reflect[1])

    drawing.append(path)
    return drawing


def osci(drawing, data, width, height, reflect, opts=None):
    """Draw a path from left to right, sample on y"""
    path = Path(stroke_width=1, stroke="black", fill="black", fill_opacity=0.0)
    path.M(0.0, height * 0.5)
    points = len(data)
    for i in range(points):
        x = i * width / points
        y = height * data[i] + height * 0.5
        path.L(x, y)

    drawing.append(path)
    return drawing


def cross(drawing, data, width, height, reflect, opts=None):
    path = Path(stroke_width=1, stroke="black", fill="black", fill_opacity=0.0)
    path.M(width * 0.5, height * 0.5)
    spec = spectrum(data, len(data))
    for i, j in zip(data, spec):
        x = i * width * 0.5 + width * 0.5
        y = (height * j * 0.5 * pi) + height * 0.5
        # y  = height * j * pi
        path.L(x, y)

    drawing.append(path)
    return drawing


def flash(drawing, data, width, height, reflect, opts=None):
    opts = opts or {}
    use_spec = opts.get("use-spec")
    half_width = width / 2
    flash = Flash(width=width, height=height)
    first_flash = flash
    flashes = [flash]
    nodes = len(data) // 2
    energy = rms(data)
    if use_spec:
        spec = spectrum(data, nodes)
        idxs = (-spec).argsort()[:nodes]
        j = 0

    for i in range(nodes):
        if flash.current_point().within_perimeter(flash.end, height / 20):
            start = first_flash.random_node
            end_x = half_width + random.randint(-1, 1) * (half_width - energy)
            end = (
                Point(end_x, (height / nodes) * idxs[j])
                if use_spec
                else Point(end_x, random.randint(0, height))
            )
            flash = Flash(width=width, height=height, start=start, end=end)
            flashes.append(flash)
            if use_spec:
                j += 1
        else:
            if opts.get("long-legs"):
                factor = random.randrange(1, max(3, int(7 + energy))) ** e
            else:
                factor = random.randrange(1, max(3, int(15 + energy)))

            flash.random_walk(data[i] * factor, data[nodes - i - 1], mix=0.0)

    for flash in flashes:
        drawing = flash.render(drawing, opts.get("thickness"))

    return drawing


def render_frame(
    drawing, data, plotter=None, width=600, height=400, reflect=(1, 1), opts=None
):
    """Wrap the renderer so different plugin plotters can be used"""
    opts = opts or {}
    try:
        plotter = globals()[plotter]
    except KeyError:
        plotter = scatter
    return plotter(drawing, data, width, height, reflect, opts)
