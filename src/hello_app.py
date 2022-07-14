from flask import Flask, request, Response
import json
from shapely import wkt
from shapely.errors import WKTReadingError
from src.poly_info import poly_info
from src.combining import combine
from src.bridging import build_bridges
from src.simplification import simplify, buffer_simplify

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
            geoms = [convert_to_mp(i_wkt) for i_wkt in req["wkts"]]
            options = req["options"]
            union = combine(geoms, **options)
            union_wkt = union.wkt
            return {'union_wkt': union_wkt}, 200
        except ValueError as e:
            return Response('ValueError: ' + str(e), status=400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status=400)
    else:
        return Response('Content-Type not supported!', status=400)


@app.route("/Build_Bridges", methods=['POST'])
def bridge_polygons():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        try:
            req = request.json
            mp = convert_to_mp(req["wkt"])
            m = req["m"]
            geom = build_bridges(mp.geoms, m)
            geom_wkt = geom.wkt
            return {'union_wkt': geom_wkt}, 200
        except ValueError as e:
            return Response('ValueError: ' + str(e), status=400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status=400)
    else:
        return Response('Content-Type not supported!', status=400)


@app.route("/Simplify", methods=['POST'])
def simplify_polygons():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        try:
            req = request.json
            mp = convert_to_mp(req["wkt"])
            m = req["m"]
            geom = buffer_simplify(mp, m)
            geom_wkt = geom.wkt
            return {'union_wkt': geom_wkt}, 200
        except ValueError as e:
            return Response('ValueError: ' + str(e), status=400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status=400)
    else:
        return Response('Content-Type not supported!', status=400)

