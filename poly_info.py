from shapely import wkt, geometry


def poly_info(obj_wkt):
    obj_geom = wkt.loads(obj_wkt)
    if not(obj_geom.geom_type == 'Polygon' or obj_geom.geom_type == 'MultiPolygon'):
        raise ValueError 
    obj_info = {"area" : obj_geom.area,
                "perimetr" : obj_geom.length,
                "BoundBox" : obj_geom.bounds}
    return obj_info