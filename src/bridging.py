from shapely.geometry import LineString, Polygon, MultiPoint, Point
from shapely.ops import unary_union


class Edge:
    def __init__(self, b_poly, b_vertex, b_poly_size,
                 e_poly, e_vertex, e_poly_size, status):
        self.b_poly = b_poly
        self.b_vertex = b_vertex
        self.e_poly = e_poly
        self.e_vertex = e_vertex
        self.status = status
        self.b_poly_size = b_poly_size
        self.e_poly_size = e_poly_size

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def make_line(self, vertexes):
        return LineString([vertexes[self.b_poly][self.b_vertex],
                           vertexes[self.e_poly]][self.e_vertex])

    def get_neighbours(self):
        return [Edge(self.b_poly, (self.b_vertex + b_shift) % self.b_poly_size, self.b_poly_size,
                     self.e_poly, (self.e_vertex + e_shift) % self.e_poly_size, self.e_poly_size,
                     "unknown")
                for b_shift in (-1, +1) for e_shift in (-1, +1)]

    def make_tuple(self):
        return self.b_poly, self.b_vertex, self.e_poly, self.e_vertex

    def __eq__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s == o

    def __lt__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s < o

    def __gt__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s > o

    def __ne__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s != o

    def __le__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s <= o

    def __ge__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s >= o


class Quad:
    def __init__(self, e1, e2):
        first = min(e1, e2)
        second = max(e1, e2)
        self.e1 = first
        self.e2 = second

    def get_other_edges(self, vertexes):
        line_b = LineString([vertexes[self.e1.b_poly][self.e1.b_vertex],
                             vertexes[self.e2.b_poly][self.e2.b_vertex]])
        line_e = LineString([vertexes[self.e1.e_poly][self.e1.e_vertex],
                             vertexes[self.e2.e_poly][self.e2.e_vertex]])
        if line_b.intersects(line_e):
            return Edge(self.e1.e_poly, self.e1.e_vertex, self.e1.e_poly_size,
                        self.e2.b_poly, self.e2.b_vertex, self.e2.b_poly_size, "unknown"), \
                   Edge(self.e1.b_poly, self.e1.b_vertex, self.e1.b_poly_size,
                        self.e2.e_poly, self.e2.e_vertex, self.e2.e_poly_size, "unknown")
        else:
            return Edge(self.e1.b_poly, self.e1.b_vertex, self.e1.b_poly_size,
                        self.e2.b_poly, self.e2.b_vertex, self.e2.b_poly_size, "unknown"), \
                   Edge(self.e1.e_poly, self.e1.e_vertex, self.e1.e_poly_size,
                        self.e2.e_poly, self.e2.e_vertex, self.e2.e_poly_size, "unknown")

    def make_valid_polygon(self, vertexes):
        line_b = LineString([vertexes[self.e1.b_poly][self.e1.b_vertex],
                             vertexes[self.e2.b_poly][self.e2.b_vertex]])
        line_e = LineString([vertexes[self.e1.e_poly][self.e1.e_vertex],
                             vertexes[self.e2.e_poly][self.e2.e_vertex]])
        if line_b.intersects(line_e):
            return Polygon([vertexes[self.e1.b_poly][self.e1.b_vertex],
                            vertexes[self.e1.e_poly][self.e1.e_vertex],
                            vertexes[self.e2.b_poly][self.e2.b_vertex],
                            vertexes[self.e2.e_poly][self.e2.e_vertex]])
        else:
            return Polygon([vertexes[self.e1.b_poly][self.e1.b_vertex],
                            vertexes[self.e2.b_poly][self.e2.b_vertex],
                            vertexes[self.e1.e_poly][self.e1.e_vertex],
                            vertexes[self.e2.e_poly][self.e2.e_vertex]])

    def get_area(self, vertexes):
        return self.make_valid_polygon(vertexes).area

    def make_tuple(self):
        return self.e1.make_tuple(), self.e2.make_tuple()

    def __eq__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s == o

    def __lt__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s < o

    def __gt__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s > o

    def __ne__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s != o

    def __le__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s <= o

    def __ge__(self, other):
        s = self.make_tuple()
        o = other.make_tuple()
        return s >= o


# для геометрий shapely
def is_free(line, polygons):
    """Checks if line intersects one or more polygon from list."""
    to_return = 1
    ends = MultiPoint(line.coords)
    for poly in polygons:
        inter = line.intersection(poly).difference(ends)
        to_return = to_return and not inter
    return to_return


# для геометрий shapely
def is_secant(line, poly):
    """Checks if line intersects polygon on edge, but not on vertex."""
    point = line.intersection(poly.boundary)
    if point.is_empty:
        return False
    if point.geom_type == "MultiPoint":
        if poly.covers(line):
            return False
        else:
            return True
    if point.geom_type == "Point" and point in [Point(p) for p in poly.boundary.coords]:
        return False
    if point.geom_type == "LineString":
        if poly.covers(line):
            return False
        else:
            return True
    return True


def get_lines(geoms):
    vertexes = [geom.exterior.coords for geom in geoms]
    e_full = []
    n = len(vertexes)
    for i in range(n):
        n_i = len(vertexes[i]) - 1
        for j in range(n_i):
            j_e = (j + 1) % n_i
            line = Edge(i, j, n_i, i, j_e, n_i, "bound")
            e_full.append(line)

    for i_b in range(n - 1):
        n_i_b = len(vertexes[i_b]) - 1
        for j_b in range(n_i_b):
            for i_e in range(i_b + 1, n):
                n_i_e = len(vertexes[i_e]) - 1
                for j_e in range(n_i_e):
                    if is_free(LineString([vertexes[i_b][j_b], vertexes[i_e][j_e]]), geoms):
                        line = Edge(i_b, j_b, n_i_b, i_e, j_e, n_i_e, "edge")
                        e_full.append(line)
    return e_full


def get_quads(edges, vertexes):
    quads = []
    for edge in edges:
        line_e = edge.make_line(vertexes)
        neighbours = edge.get_neighbours(edge.b_poly_size, edge.e_poly_size)
        for neighbour in neighbours:
            condition1 = neighbour in edges
            line_n = neighbour.make_line(vertexes)
            condition2 = not line_n.intersects(line_e)
            if condition1 and condition2:
                neighbour = edges[edges.index(neighbour)]  # чтобы status не unknown
                qd = Quad(edge, neighbour)
                quads.append(qd)
    return quads


def handle_edges(qd, e_full, vertexes):
    # должны меняться в e_full
    e_full[e_full.index(qd.e1)].set_status = "bound"
    e_full[e_full(qd.e2)].set_status = "bound"
    bnd = qd.get_other_edges(vertexes)
    e_full[e_full.index(bnd[0])] = "inner"
    e_full[e_full.index(bnd[1])] = "inner"
    for e in e_full:
        if e.get_status() in ("edge", "bound"):
            line = e.make_line(vertexes)
            if is_secant(line, qd.make_valid_poly) and e not in [qd.e1, qd.e2, bnd[0], bnd[1]]:
                e.set_status("secant")
            if qd.make_valid_poly.covers(line) and e not in [qd.e1, qd.e2, bnd[0], bnd[1]]:
                e.set_status("inner")


def get_second_points(point, e_full):
    points = [(i.b_poly, i.b_vertex, i.b_poly_size) for i in e_full
              if i.get_status == "edge"
              and (i.b_poly, i.b_vertex, i.b_poly_size) != point
              and (i.e_poly, i.e_vertex, i.e_poly_size) == point] \
             + [(i.e_poly, i.e_vertex, i.e_poly_size) for i in e_full
                if i.get_status() == "edge"
                and (i.b_poly, i.b_vertex, i.b_poly_size) == point
                and (i.e_poly, i.e_vertex, i.e_poly_size) != point]
    return points


def form_quads(edge, quads, e_full):
    e_b = (edge.b_poly, edge.b_vertex, edge.b_poly_size)
    e_e = (edge.e_poly, edge.e_vertex, edge.e_poly_size)
    b_points = get_second_points(e_b, e_full)
    e_points = get_second_points(e_e, e_full)
    for bn in b_points:
        for ed in e_points:
            to_check = Edge(*min(bn, ed), *max(bn, ed), "unknown")
            if to_check in e_full:
                to_check = e_full[e_full.index(to_check)]  # чтобы status не unknown
                if to_check.get_status() == "bound":
                    b = e_full[e_full.index(Edge(*min(e_b, bn), *max(e_b, bn)))]
                    e = e_full[e_full.index(Edge(*min(e_e, ed), *max(e_e, ed)))]
                    qd = Quad(b, e)
                    if qd not in quads:
                        quads.append(qd)


def handle_quads(item, quads, e_full, vertexes, united):
    to_remove = [q for q in quads
                 if e_full[q.e1] in ("inner", "secant")
                 or e_full[q.e2] in ("inner", "secant")
                 or are_united({q.e1.b_poly, q.e1.e_poly,
                                q.e2.b_poly, q.e2.e_poly}, united)]
    for item in to_remove:
        quads.remove(item)
    for e in item.e1, item.e2:
        form_quads(e, quads, e_full)
    quads.sort(key=lambda x: x.get_area(vertexes), reverse=True)


def are_united(points, united):
    to_return = 0
    for topo in united:
        to_return = to_return or points.issubset(topo)
    return to_return


def handle_topology(item, united):
    p1b = item.e1.b_poly
    p1e = item.e1.e_poly
    p2b = item.e2.b_poly
    p2e = item.e2.e_poly
    cur_u = {p1b, p1e, p2b, p2e}
    cur_inter = []
    for topo in united:
        if cur_u.intersection(topo):
            cur_inter.append(topo)
            cur_u = cur_u.union(topo)
    for topo in cur_inter:
        united.remove(topo)
    united.append(cur_u)


def get_bridges(vertexes, e_full, quad, nm):
    bridges = []
    united = []
    q_sorted = sorted(quad, key=lambda x: x.get_area(vertexes), reverse=True)
    for cnt in range(nm):
        item = q_sorted.pop()
        poly = item.make_valid_polygon(vertexes)
        bridges.append(poly)
        handle_topology(item, united)
        handle_edges(item, e_full, vertexes)
        handle_quads(item, q_sorted, e_full, vertexes, united)
    return bridges


def build_bridges(geoms, m):
    """Builds bridges-polygons between n polygons to save m polygons where m < n."""
    if m > len(geoms):
        raise ValueError("There are less amount of polygons in geometry than parament value")
    elif m < 1:
        raise ValueError("Amount of polygons couldn't be less than 1")
    vertexes = [geom.exterior.coords for geom in geoms]  # vetrexes[i][j] - j-ая вершина в i-ом полигоне
    e_full = get_lines(geoms)
    edges = [edge for edge in e_full if edge.get_status() == "edge"]
    quad = get_quads(edges, vertexes)
    bridges = get_bridges(vertexes, e_full, quad, len(vertexes) - m)
    to_union = bridges + list(geoms)
    result = unary_union(to_union)
    return result
