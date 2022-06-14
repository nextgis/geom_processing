from shapely import wkt
from shapely.geometry import Polygon
from shapely.errors import WKTReadingError
from shapely.ops import unary_union

def combine(poly1, poly2, **kwargs):
    try:
        geom_1 = wkt.loads(poly1["wkt"])
        geom_2 = wkt.loads(poly2["wkt"])
        if not(geom_1.geom_type == 'Polygon' or geom_2.geom_type == 'Polygon'\
                or geom_1.geom_type == 'MultiPolygon' or geom_2.geom_type == 'MultiPolygon'):
            raise ValueError("geom_type is not Polygon")
        to_return = unary_union([geom_1, geom_2])
        return to_return.wkt
    except KeyError:
        raise ValueError(str(e))
        
        
