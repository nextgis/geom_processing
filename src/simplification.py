from shapely.geometry import Point


class StraightLine:
    def __init__(self, p1, p2):
        self.a = p1.y - p2.y
        self.b = p2.x - p1.y
        self.c = p2.x * self.a + p2.y * self.b

    def inter_point(self, other):
        d = self.a * other.b - self.b * other.a
        dx = self.c * other.b - self.b * other.c
        dy = self.a * other.c - self.c * other.a
        if d == 0:
            return []
        else:
            x = dx / d
            y = dy / d
            return Point(x, y)


def convex_change(prev_ps, this_p, next_p):
    l_prev = StraightLine(prev_ps[0].coords, prev_ps[1].coords)
    l_next = StraightLine(this_p.coords, next_p.coords)
    new_p = l_next.inter_point(l_prev)
    direct = ((next_p.x - prev_ps[1].x) * (this_p.y - prev_ps[1].y)
              - (next_p.y - prev_ps[1].y) * (this_p.x - prev_ps[1].x))
    if new_p:
        new_direct = ((next_p.x - prev_ps[0].x) * (new_p.y - prev_ps[0].y)
                      - (next_p.y - prev_ps[0].y) * (new_p.x - prev_ps[0].x))
        if new_direct * direct >= 0:
            return [prev_ps[0], new_p, next_p]
        else:
            return [prev_ps[0], prev_ps[1], this_p, next_p]
    else:
        return [prev_ps[0], prev_ps[1], this_p, next_p]


def concave_change(prev_p, this_p, next_p):
    return [prev_p, next_p]


def is_convex(this_p, prev_p, next_p):
    pass


def simplify(geoms):
    pass