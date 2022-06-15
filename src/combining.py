from shapely import wkt
from shapely.geometry import MultiPolygon
from shapely.errors import WKTReadingError
from shapely.ops import unary_union

def combine(mp1_wkt, mp2_wkt, **kwargs):
    try:
        geom_1 = wkt.loads(mp1_wkt)
        geom_2 = wkt.loads(mp2_wkt)
        if not(geom_1.geom_type == 'MultiPolygon' and geom_2.geom_type == 'MultiPolygon'):
            raise ValueError("geom_type is not MultiPolygon")
        to_return = unary_union([geom_1, geom_2])
        if to_return.geom_type == "Polygon":
            to_return = MultiPolygon([to_return])
        return to_return.wkt
    except WKTReadingError as e:
        raise ValueError(str(e))  
        
