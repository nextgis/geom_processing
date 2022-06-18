from shapely import wkt
from shapely.geometry import MultiPolygon, Polygon
from shapely.errors import WKTReadingError

from shapely.ops import unary_union

def fill_holes(geom, hole_area):
    poly_tree = [{"exterior" : item.exterior, "interiors" : item.interiors} for item in list(geom)]
    for item in poly_tree:
        item["new_interiors"] = [j for j in item["interiors"] if Polygon(j).area >= hole_area]
    new_polygons = [Polygon(j["exterior"], j["new_interiors"]) for j in poly_tree]
    new_mp = MultiPolygon(new_polygons)
    return new_mp
 

def prepare_mp(geom):
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    elif geom.geom_type == "MultiPolygon":    
        return geom
    else:
        raise ValueError("Result is not MultiPolygon : " + to_return.geom_type)

 
def combine(geom_1, geom_2, hole_area=0, **kwargs):    
    union = unary_union([geom_1, geom_2])
    mp = prepare_mp(union)
    filled = fill_holes(mp, hole_area)
    return filled
    
