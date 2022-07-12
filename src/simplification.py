from shapely.geometry import Point, LineString, Polygon, MultiPolygon


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


class ChangeList(list):
    def fill(self, geom):
        for point in geom:
            change = self.ChangePoint(point)
            self.append(change)
        for elem in self:
            self._calc_elem(elem)  # метод списка
        return self

    def _calc_elem(self, elem):
        index = self.index(elem)
        next_ch = self[index + 1]
        prev_ch = self[index - 1]
        preprev_ch = self[index - 2]
        poly = self.polygonize()
        elem.calc_changes(next_ch, prev_ch, preprev_ch, poly)

    def recalc_elem(self, elem):
        index = self.index(elem)
        next_ch = self[index + 1]
        prev_ch = self[index - 1]
        preprev_ch = self[index - 2]
        elem.update(next_ch, prev_ch, preprev_ch)
        self._calc_elem(elem)
        self._calc_elem(preprev_ch)

    def recalc_min(self):
        mn = min(self, key=lambda x: x.area)
        self.recalc_elem(mn)

    def polygonize(self):
        return Polygon([item.point() for item in self])

    class ChangePoint:
        def __init__(self, point):
            self._point = point
            self._method = "no_method"
            self._area = float("inf")

        @property
        def point(self):
            return self.point

        @point.setter
        def point(self, point):
            self._point = point

        @property
        def area(self):
            return self._area

        def calc_change(self, next_ch, prev_ch, preprev_ch, poly):
            try:
                prev_p = prev_ch.point
                next_p = next_ch.point
                line = LineString([prev_p, next_p]).difference(prev_p).difference(next_p)
                if poly.covers(line):
                    self._method = "convex"
                    preprev_p = preprev_ch.point
                    convex_point = self._find_convex_point(preprev_p, prev_p,
                                                           self._point, next_p)
                    self._area = Polygon([convex_point, next_p, preprev_p]).area
                else:
                    self._method = "concave"
                    self._area = Polygon([self.point, next_p, prev_p]).area
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

        def update(self, next_ch, prev_ch, preprev_ch):
            try:
                if self._method == "concave":
                    del self
                elif self._method == "convex":
                    preprev_p = preprev_ch.point
                    prev_p = prev_ch.point
                    next_p = next_ch.point
                    convex_point = self._find_convex_point(preprev_p, prev_p,
                                                           self.point, next_p)
                    self._point = convex_point
                    del prev_ch

            except Exception as e:
                print(e)


def get_changes(geoms):
    changes = []
    for geom in geoms:
        geom_changes = ChangeList().fill(geom)
        changes.append(geom_changes)
    return changes


def get_change_of_min(changes):
    mns = [min(change, key=lambda x: x.get_area()) for change in changes]
    mn = min(mns, key=lambda x: x.get_area())
    index = mns.index(mn)
    return changes[index]


def simplify(polygons, m):
    geoms = [list(polygon.exterior.coords) for polygon in polygons]
    changes = get_changes(geoms)
    for cnt in range(len(geoms) - m):
        ch_m = get_change_of_min(changes)
        ch_m.recalc_min()
    return MultiPolygon([change.polygonize() for change in changes])
