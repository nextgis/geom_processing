from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

EPS = 1e-15


def in_geoms(item, geoms):
    for geom in geoms:
        if geom.contains(item):
            return 1
        elif geom.buffer(EPS).contains(item):
            return 1
    return 0


def fill_holes(geom, hole_area, init_holes):
    ih_poly = [Polygon(ih) for ih in init_holes]
    new_polygons = []
    for item in geom.geoms:
        exterior = item.exterior
        interiors = item.interiors
        new_interiors = [j for j in interiors
                         if Polygon(j).area >= hole_area or
                         in_geoms(Polygon(j), ih_poly)]
        new_polygons += [Polygon(exterior, new_interiors)]
    new_mp = MultiPolygon(new_polygons)
    return new_mp


def prepare_mp(geom):
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    elif geom.geom_type == "MultiPolygon":
        return geom
    else:
        raise ValueError("Result is not MultiPolygon : " + geom.geom_type)


def get_init_holes(mp):
    polygones_holes = [poly.interiors for poly in mp.geoms]
    return [hole for polygon in polygones_holes for hole in polygon]


def combine(geoms, hole_area=0, **kwargs):
    union = unary_union(geoms)
    mp = prepare_mp(union)
    init_holes = [hole for geom in geoms for hole in get_init_holes(geom)]
    filled = fill_holes(mp, hole_area, init_holes)
    return filled

