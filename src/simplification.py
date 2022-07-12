from shapely.geometry import Point, LineString, Polygon


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


class ChangePoint:
    def __init__(self, point, next_ch='', prev_ch=''):
        self._point = point
        self._next_ch = next_ch
        self._prev_ch = prev_ch
        self._method = "no_method"
        self._area = float("inf")

    @property
    def point(self):
        return self.point

    @point.setter
    def point(self, point):
        self._point = point

    @property
    def next_ch(self):
        return self.next_ch

    @next_ch.setter
    def next_ch(self, next_ch):
        self._next_ch = next_ch

    @property
    def prev_ch(self):
        return self.prev_ch

    @prev_ch.setter
    def prev_ch(self, prev_ch):
        self._prev_ch = prev_ch

    def calc_change(self, poly):
        try:
            next_p = self.next_ch().point()
            prev_p = self.prev_ch().point()
            line = LineString([prev_p, next_p]).difference(prev_p).difference(next_p)
            if poly.covers(line):
                self._method = "convex"
                preprev_p = self.prev_ch().prev_ch().point()
                convex_point = self._find_convex_point(preprev_p, prev_p,
                                                       self._point, next_p)
                self._area = Polygon([convex_point, next_p, preprev_p]).area
            else:
                self._method = "concave"
                self._area = Polygon([self.point(), next_p, prev_p]).area
        except ValueError:
            self._method = "no_method"
            self._area = float("inf")
            pass
        except AttributeError:
            self._method = "no_method"
            self._area = float("inf")
            raise AttributeError("Couldn't find neighbours point.")

    @staticmethod
    def _find_convex_point(preprev_p, prev_p, this_p, next_p):
        l_prev = StraightLine(preprev_p.coords, prev_p.coords)
        l_next = StraightLine(this_p.coords, next_p.coords)
        new_p = l_next.inter_point(l_prev)
        direct = ((next_p.x - prev_p.x) * (this_p.y - prev_p.y)
                  - (next_p.y - prev_p.y) * (this_p.x - prev_p.x))
        if new_p:
            new_direct = ((next_p.x - preprev_p.x) * (new_p.y - preprev_p.y)
                          - (next_p.y - preprev_p.y) * (new_p.x - preprev_p.x))
            if new_direct * direct >= 0:
                return new_p
            else:
                raise ValueError("No point of intersection on the interesting side.")
        else:
            raise ValueError("No point of intersection, edges are ||.")

    def recalc(self, poly):
        try:
            if self._method == "concave":
                self._prev_ch.next_ch(self._next_ch)
                self._next_ch.prev_ch(self._prev_ch)
                self._prev_ch.calc_change(poly)
                self._next_ch.calc_change(poly)
                del self # нужно, чтобы его не было и в контейнере
            elif self._method == "convex":
                preprev_ch = self.prev_ch().prev_ch()
                convex_point = self._find_convex_point(preprev_ch.point(), self.prev_ch().point(),
                                                       self.point(), self.next_ch().point())
                self._point = convex_point
                del self._prev_ch
                self._prev_ch = preprev_ch
                self._prev_ch.next_ch(self)
                self.calc_change(poly)
                self._prev_ch.calc_change(poly)
        except Exception as e:
            print(e)

    def __next__(self):
        self.__next__ = self._next_ch


class ChangeList(list):
    def polygonize(self):
        return Polygon([item.point() for item in self])


def get_changes(geoms):
    changes = []
    for geom in geoms:
        geom_changes = ChangeList()
        pairs = list(zip(geom, geom[1:] + geom[:1]))
        for pair in pairs:
            pass
    return changes


def get_min_change(changes):
    mins = [min(change, key=lambda x: x.cost_area) for change in changes]
    return min(mins, key=lambda x: x.cost_area)


def simplify(polygons, m):
    geoms = [list(polygon.exterior.coords) for polygon in polygons]
    changes = get_changes(geoms)
    for cnt in range(len(geoms) - m):
        cur_min = get_min_change(changes)
