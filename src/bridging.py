from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union


def is_free(line, polygons):
    """Checks if line intersects one or more polygon from list."""
    to_return = 1
    for poly in polygons:
        to_return = to_return and not poly.intersects(line)
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


def intersects_on_edge(line, poly):
    """Checks if line intersects polygon on edge, but not on vertex."""
    point = line.intersection(poly.boundary)
    if point.empty:
        return False
    if len(point) == 1 and point[0] in [poly.boundary.coords]:
        return False
    return True


def build_bridges(geoms, m):
    """Builds bridges-polygons between n polygons to save m polygons where m < n."""
    vertexes = [geom.exterior.coords for geom in geoms]  # vetrexes[i][j] - j-ая вершина в i-ом полигоне
    e_full = {}  # ребра: исходные и добавленные
    n = len(vertexes)
    for i in range(n):
        for j in range(len(vertexes[i])):
            j_e = j + 1
            if j_e == len(vertexes[i]):
                j_e = 0
            e_full[(i, j, i, j_e)] = {"origin": "bound"}

    # 1. Построение отрезков
    for i_b in range(n - 1):
        for j_b in range(len(vertexes[i_b])):
            for i_e in range(i_b + 1, n):
                for j_e in range(len(vertexes[i_e])):
                    if is_free(LineString([vertexes[i_b][j_b], vertexes[i_e][j_e]]), geoms):
                        e_full[(i_b, j_b, i_e, j_e)] = {"origin": "edge"}

    # 2. Сбор четырехугольников
    quad = {}
    for edge in e_full:
        line_e = LineString([vertexes[edge[0]][1], vertexes[edge[2]][3]])
        neighbours = get_neighbours(edge, len(vertexes[0]), len(vertexes[2]))
        for neighbour in neighbours:
            condition1 = neighbour in e_full
            line_n = LineString([vertexes[neighbour[0]][1], vertexes[neighbour[2]][3]])
            condition2 = not line_n.intersects(line_e)
            if condition1 and condition2:
                first = min(edge, neighbour)
                second = max(edge, neighbour)
                cur_area = Polygon([vertexes[edge[0]][edge[1]], vertexes[edge[2]][edge[3]],
                                    vertexes[neighbour[2]][edge[3]], vertexes[neighbour[0]][edge[1]]]).area
                quad[(first, second)] = cur_area

    # 3. Выбор перетяжек
    bridges = []
    q_sorted = sorted(list(quad.items()), key=lambda x: x[1], reverse=True)
    for cnt in range(n - m):
        item = q_sorted.pop()
        e1 = item[0]
        e2 = item[1]
        poly = Polygon([vertexes[e1[0]][e1[1]], vertexes[e1[2]][e1[3]],
                        vertexes[e2[2]][e2[3]], vertexes[e2[0]][e2[1]]])
        bridges.append(poly)
        e_full[e1]["origin"] = "bound"
        e_full[e2]["origin"] = "bound"
        b1 = (e1[0], min(e1[1], e2[1]), e2[0], max(e1[1], e2[1]))
        b2 = (e1[2], min(e1[3], e2[3]), e2[2], max(e1[3], e2[3]))
        e_full[b2]["origin"] = "inner"
        e_full[b1]["origin"] = "inner"
        for e in e_full:
            if e_full[e]["origin"] in ("edge", "bound"):
                line = LineString([vertexes[e[0]][e[1]], vertexes[e[2]][e[3]]])
                if intersects_on_edge(line, poly) and e not in [e1, e2, b1, b2]:
                    e_full[e]["origin"] = "secant"
        for q in q_sorted:
            if (e_full[q[0]]["origin"] in ("inner", "secant")
                    or e_full[q[1]]["origin"] in ("inner", "secant")):
                q_sorted.remove(q)

    result = unary_union[geoms + bridges]
    return result
