from shapely import wkt
from shapely.geometry import MultiPolygon
from shapely.errors import WKTReadingError

from shapely.ops import unary_union

def combine(geom_1, geom_2, **kwargs):    
    to_return = unary_union([geom_1, geom_2])
    if to_return.geom_type == "Polygon":
        to_return = MultiPolygon([to_return])
        return to_return.wkt
    elif to_return.geom_type == "MultiPolygon":    
        return to_return.wkt
    else:
        raise ValueError("Result is not MultiPolygon : " + to_return.geom_type)

