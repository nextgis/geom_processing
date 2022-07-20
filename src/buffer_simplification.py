from shapely.geometry import Polygon
from shapely.ops import unary_union
from math import pi


def buffer_simplify(mp, m, am_iter=1000):
    n = vertex_in_mp(mp)
    if am_iter < 1:
        raise ValueError("Negative amount of iterations is incorrect")
    if m >= n:
        raise ValueError("Expected amount of vertexes is more then actual")
    cur_rad = get_init_rad(mp, m)
    cur_ver = 0
    res_mp = Polygon([])
    prev_mp = Polygon([])
    cnt = 0
    reverse_cnt = 0
    while cur_ver < m and cnt < am_iter:
        cur_rad *= 0.5
        prev_mp = res_mp
        res_mp = calc_mp(cur_rad, mp)
        prev_ver = cur_ver
        cur_ver = vertex_in_mp(res_mp)
        if prev_ver > cur_ver:
            reverse_cnt += 1
            if reverse_cnt > 3:
                raise ValueError("Error of simplification.")
        cnt += 1
    if prev_mp.is_empty and cur_ver != m:
        raise ValueError(f"Couldn't simplify to {m} vertexes")
    if cur_ver == m:
        return res_mp
    return prev_mp


def get_init_rad(mp, m):
    n = vertex_in_mp(mp)
    cmp = mp.length / 2
    calc_rad = n * pi / m**2 * cmp
    return calc_rad


def calc_mp(cur_rad, mp):
    buffers = [poly.buffer(cur_rad) for poly in mp.geoms]
    tol = cur_rad
    simple = [buf.simplify(tol) for buf in buffers]
    return unary_union(simple)


def vertex_in_mp(mp):
    if mp.geom_type == "MultiPolygon":
        return sum([len(poly.exterior.coords)
                    + sum([len(interior.coords) for interior in poly.interiors])
                    for poly in mp.geoms])
    elif mp.geom_type == "Polygon":
        return len(mp.exterior.coords) \
               + sum([len(interior.coords) for interior in mp.interiors])