from shapely import wkt
from shapely.geometry import Polygon
from shapely.errors import WKTReadingError


def poly_info(obj_wkt):
    try:
        obj_geom = wkt.loads(obj_wkt)
        if not(obj_geom.geom_type == 'Polygon' or obj_geom.geom_type == 'MultiPolygon'):
            raise ValueError("geom_type is not Polygon or MultiPolygon")
        obj_info = {"area" : obj_geom.area,
                    "perimetr" : obj_geom.length,
                    "bound_box" : wkt.dumps(get_bb_polygon(obj_geom.bounds))}
        return obj_info
    except WKTReadingError as e:
        raise ValueError(str(e))

def get_bb_polygon(bounds):
    v = [(bounds[x], bounds[y]) for (x, y) in [(0, 1), (0, 3), (2, 3), (2, 1)]]
    return Polygon(v)

