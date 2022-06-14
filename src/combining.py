from shapely import wkt
from shapely.geometry import Polygon
from shapely.errors import WKTReadingError
from shapely.ops import unary_union

def combine(poly1, poly2, **kwargs):
    try:
        geom_1 = wkt.loads(poly1["wkt"])
        geom_2 = wkt.loads(poly2["wkt"])
        if not(geom_1.geom_type == 'Polygon' and geom_2.geom_type == 'Polygon'):
            raise ValueError("geom_type is not Polygon")
        to_return = unary_union([geom_1, geom_2])
        if to_return.geom_type == "MultiPolygon":
            raise ValueError('couldn\'t create Polygon')
        return to_return.wkt
    except KeyError:
        raise KeyError("No wkt attribute")
    except WKTReadingError as e:
        raise ValueError(str(e))  
        
