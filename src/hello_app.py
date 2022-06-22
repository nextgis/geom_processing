from flask import Flask, request, Response
import json
from shapely import wkt
from shapely.errors import WKTReadingError
from src.poly_info import poly_info
from src.combining import combine

app = Flask(__name__)


def convert_to_mp(input_wkt):
    try:
        geom = wkt.loads(input_wkt)
        if not(geom.geom_type == 'MultiPolygon'):
            raise ValueError("geom_type is not MultiPolygon")
        else:
            return geom
    except WKTReadingError as e:
        raise ValueError(str(e))


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
    
@app.route("/GetPolyParams", methods=['POST'])
def handle_geom():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        try:
            wkt1 = request.json["wkt1"]
            return Response(response=json.dumps(poly_info(wkt1)),
                            status=200)
        except ValueError as e:
            return Response('ValueError: ' + str(e), status=400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status=400)
    else:
        return Response('Content-Type not supported!', status=400)


@app.route("/CombineMultiPolygons", methods=['POST'])
def combine_polygons():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        try:
            req = request.json
            geom_1 = convert_to_mp(req["wkt1"])
            geom_2 = convert_to_mp(req["wkt2"])
            params = {k: req[k] for k in req.keys() if k != "wkt1" or k != "wkt2"}
            union = combine(geom_1, geom_2, **params)
            union_wkt = union.wkt
            return {'union_wkt': union_wkt}, 200
        except ValueError as e:
            return Response('ValueError: ' + str(e), status=400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status=400)
    else:
        return Response('Content-Type not supported!', status=400)

