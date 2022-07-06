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

    def get_neighbours(self):
        return [(self.b_poly, (self.b_vertex + b_shift) % self.b_poly_size,
                 self.e_poly, (self.e_vertex + e_shift) % self.e_poly_size)
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


# метод класса Edge
def get_neighbours(edge, size1, size2):
    """Returns edges, which connect neighbour vertexes on polygons for edge-parameter."""
    p1 = edge[0]
    v1_i = edge[1]
    p2 = edge[2]
    v2_i = edge[3]
    return [(p1, (v1_i - 1) % size1, p2, (v2_i - 1) % size2),
            (p1, (v1_i - 1) % size1, p2, (v2_i + 1) % size2),
            (p1, (v1_i + 1) % size1, p2, (v2_i - 1) % size2),
            (p1, (v1_i + 1) % size1, p2, (v2_i + 1) % size2)]


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


# для геометрий shapely
# todo должен возвращать список Edge
def get_lines(geoms):
    vertexes = [geom.exterior.coords for geom in geoms]
    e_full = {}  # ребра: исходные и добавленные
    n = len(vertexes)
    for i in range(n):
        n_i = len(vertexes[i]) - 1
        for j in range(n_i):
            j_e = (j + 1) % n_i
            e_full[(i, j, i, j_e)] = "bound"

    for i_b in range(n - 1):
        n_i_b = len(vertexes[i_b]) - 1
        for j_b in range(n_i_b):
            for i_e in range(i_b + 1, n):
                n_i_e = len(vertexes[i_e]) - 1
                for j_e in range(n_i_e):
                    if is_free(LineString([vertexes[i_b][j_b], vertexes[i_e][j_e]]), geoms):
                        e_full[(i_b, j_b, i_e, j_e)] = "edge"
    return e_full


# сделан класс Quad
def make_quad(e1, e2):
    first = min(e1, e2)
    second = max(e1, e2)
    return first, second


# todo переделать для классов Edge и Quad
def get_quads(edges, vertexes):
    quads = {}
    for edge in edges:
        line_e = LineString([vertexes[edge[0]][edge[1]], vertexes[edge[2]][edge[3]]])
        neighbours = get_neighbours(edge, len(vertexes[edge[0]]) - 1, len(vertexes[edge[2]]) - 1)
        for neighbour in neighbours:
            condition1 = neighbour in edges
            line_n = LineString([vertexes[neighbour[0]][neighbour[1]], vertexes[neighbour[2]][neighbour[3]]])
            condition2 = not line_n.intersects(line_e)
            if condition1 and condition2:
                qd = make_quad(edge, neighbour)
                cur_area = Polygon([vertexes[edge[0]][edge[1]], vertexes[edge[2]][edge[3]],
                                    vertexes[neighbour[2]][neighbour[3]], vertexes[neighbour[0]][neighbour[1]]]).area
                quads[qd] = cur_area
    return quads


# в классе Quad make_valid_polygon
def arrange_vertexes(e1, e2, vertexes):
    a1 = e1[0], e1[1]
    b1 = e1[2], e1[3]
    a2 = e2[0], e2[1]
    b2 = e2[2], e2[3]
    line_a = LineString([vertexes[a1[0]][a1[1]], vertexes[a2[0]][a2[1]]])
    line_b = LineString([vertexes[b1[0]][b1[1]], vertexes[b2[0]][b2[1]]])
    if line_a.intersects(line_b):
        return a1, b1, a2, b2
    else:
        return a1, b1, b2, a2


# todo переделать для Edge
def handle_edges(e1, e2, v, poly, e_full, vertexes):
    e_full[e1] = "bound"
    e_full[e2] = "bound"
    bnd1 = make_edge(v[1], v[2])
    bnd2 = make_edge(v[0], v[3])
    e_full[bnd1] = "inner"
    e_full[bnd2] = "inner"
    for e in e_full:
        if e_full[e] in ("edge", "bound"):
            line = LineString([vertexes[e[0]][e[1]], vertexes[e[2]][e[3]]])
            if is_secant(line, poly) and e not in [e1, e2, bnd1, bnd2]:
                e_full[e] = "secant"
            if poly.covers(line) and e not in [e1, e2, bnd1, bnd2]:
                e_full[e] = "inner"


# todo переделать для Edge
# вопрос в необходимости
def make_edge(bn, ed):
    mn = min(bn, ed)
    mx = max(bn, ed)
    if mn[0] == mx[0] and mn[1] == 0 and mx[1] > 1:
        t = mn
        mn = mx
        mx = t
    return mn[0], mn[1], mx[0], mx[1]


# todo переделать для Edge
def get_second_points(point, e_full):
    points = [(i[0], i[1]) for i in e_full if e_full[i] == "edge"
              and (i[0], i[1]) != point and (i[2], i[3]) == point] \
             + [(i[2], i[3]) for i in e_full if e_full[i] == "edge"
                and (i[0], i[1]) == point and (i[2], i[3]) != point]
    return points


def form_quads(e, quads, e_full, vertexes):
    e_b = (e[0], e[1])
    e_e = (e[2], e[3])
    b_points = get_second_points(e_b, e_full)
    e_points = get_second_points(e_e, e_full)
    for bn in b_points:
        for ed in e_points:
            to_check = make_edge(bn, ed)
            if to_check in e_full.keys():
                if e_full[to_check] == "bound":
                    poly = Polygon([vertexes[e[0]][e[1]], vertexes[e[2]][e[3]],
                                    vertexes[ed[0]][ed[1]], vertexes[bn[0]][bn[1]]])
                    if poly.is_valid:
                        e1 = make_edge(e_b, bn)
                        e2 = make_edge(e_e, ed)
                        qd = make_quad(e1, e2)
                        area = poly.area
                        quads.append((qd, area))


def handle_quads(e1, e2, quads, e_full, vertexes, united):
    to_remove = [q for q in quads
                 if e_full[q[0][0]] in ("inner", "secant")
                 or e_full[q[0][1]] in ("inner", "secant")
                 or (q[0][0][0] in united and q[0][0][2] in united)]
    for item in to_remove:
        quads.remove(item)
    for e in e1, e2:
        form_quads(e, quads, e_full, vertexes)
    quads.sort(key=lambda x: x[1], reverse=True)


def get_bridges(vertexes, e_full, quad, nm):
    bridges = []
    united = set()
    q_sorted = sorted(list(quad.items()), key=lambda x: x[1], reverse=True)
    for cnt in range(nm):
        item = q_sorted.pop()
        e1 = item[0][0]
        e2 = item[0][1]
        v = arrange_vertexes(e1, e2, vertexes)
        poly = Polygon([vertexes[v[0][0]][v[0][1]], vertexes[v[1][0]][v[1][1]],
                        vertexes[v[2][0]][v[2][1]], vertexes[v[3][0]][v[3][1]]])
        bridges.append(poly)
        united.add(v[0][0])
        united.add(v[1][0])
        handle_edges(e1, e2, v, poly, e_full, vertexes)
        handle_quads(e1, e2, q_sorted, e_full, vertexes, united)
    return bridges


def build_bridges(geoms, m):
    """Builds bridges-polygons between n polygons to save m polygons where m < n."""
    if m > len(geoms):
        raise ValueError("There are less amount of polygons in geometry than parament value")
    elif m < 1:
        raise ValueError("Amount of polygons couldn't be less than 1")
    vertexes = [geom.exterior.coords for geom in geoms]  # vetrexes[i][j] - j-ая вершина в i-ом полигоне
    e_full = get_lines(geoms)
    edges = [edge for edge in e_full if e_full[edge] == "edge"]
    quad = get_quads(edges, vertexes)
    bridges = get_bridges(vertexes, e_full, quad, len(vertexes) - m)
    to_union = bridges + list(geoms)
    result = unary_union(to_union)
    return result
