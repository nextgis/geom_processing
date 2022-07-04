from shapely.geometry import LineString, Polygon, MultiPoint, Point
from shapely.ops import unary_union


def is_free(line, polygons):
    """Checks if line intersects one or more polygon from list."""
    to_return = 1
    ends = MultiPoint(line.coords)
    for poly in polygons:
        inter = line.intersection(poly).difference(ends)
        to_return = to_return and not inter
    return to_return


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
                first = min(edge, neighbour)
                second = max(edge, neighbour)
                cur_area = Polygon([vertexes[edge[0]][edge[1]], vertexes[edge[2]][edge[3]],
                                    vertexes[neighbour[2]][neighbour[3]], vertexes[neighbour[0]][neighbour[1]]]).area
                quads[(first, second)] = cur_area
    return quads


def get_new_inner(e1, e2):
    ps1 = sorted([e2[1], e1[1]], reverse=not(e1[1] and e2[1]))
    ps2 = sorted([e2[3], e1[3]], reverse=not(e1[3] and e2[3]))
    b1 = (e1[0], ps1[0], e2[0], ps1[1])
    b2 = (e1[2], ps2[0], e2[2], ps2[1])
    return b1, b2


def handle_edges(e1, e2, poly, e_full, vertexes):
    e_full[e1] = "bound"
    e_full[e2] = "bound"
    b = get_new_inner(e1, e2)
    e_full[b[0]] = "inner"
    e_full[b[1]] = "inner"
    for e in e_full:
        if e_full[e] in ("edge", "bound"):
            line = LineString([vertexes[e[0]][e[1]], vertexes[e[2]][e[3]]])
            if is_secant(line, poly) and e not in [e1, e2, b[0], b[1]]:
                e_full[e] = "secant"
            if poly.covers(line) and e not in [e1, e2, b[0], b[1]]:
                e_full[e] = "inner"


def handle_quads(quads, e_full):
    for q in quads:
        if (e_full[q[0]] in ("inner", "secant")
                or e_full[q[1]] in ("inner", "secant")):
            quads.remove(q)


def get_bridges(vertexes, e_full, quad, nm):
    bridges = []
    q_sorted = sorted(list(quad.items()), key=lambda x: x[1], reverse=True)
    for cnt in range(nm):
        item = q_sorted.pop()
        e1 = item[0][0]
        e2 = item[0][1]
        poly = Polygon([vertexes[e1[0]][e1[1]], vertexes[e1[2]][e1[3]],
                        vertexes[e2[2]][e2[3]], vertexes[e2[0]][e2[1]]])
        bridges.append(poly)
        handle_edges(e1, e2, poly, e_full, vertexes)
        handle_quads(q_sorted, e_full)
    return bridges


def build_bridges(geoms, m):
    """Builds bridges-polygons between n polygons to save m polygons where m < n."""
    # 1. Построение отрезков
    vertexes = [geom.exterior.coords for geom in geoms]  # vetrexes[i][j] - j-ая вершина в i-ом полигоне
    e_full = get_lines(geoms)

    # 2. Сбор четырехугольников
    edges = [edge for edge in e_full if e_full[edge] == "edge"]
    quad = get_quads(edges, vertexes)

    # 3. Выбор перетяжек
    bridges = get_bridges(vertexes, e_full, quad, len(vertexes) - m)

    to_union = list(geoms) + bridges
    result = unary_union(to_union)
    return result
