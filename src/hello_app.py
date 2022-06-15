from flask import Flask, request, Response
import json
from src.poly_info import poly_info
from src.combining import combine

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
    
@app.route("/GetPolyParams", methods=['POST'])
def handle_geom():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        try:
            wkt1 = request.json["wkt1"]
            return Response(response = json.dumps(poly_info(wkt1)), 
                            status = 200) 
        except ValueError as e:
            return Response('ValueError: ' + str(e), status = 400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status = 400)
    else:
        return Response('Content-Type not supported!', status = 400)


@app.route("/CombineMultiPolygons", methods=['POST'])
def combine_polygons():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        try:
            req = request.json
            mp1_wkt = req["wkt1"]
            mp2_wkt = req["wkt2"]
            union_wkt = combine(mp1_wkt, mp2_wkt)
            return Response(response = f'{{"union_wkt" : "{union_wkt}"}}', status = 200) 
        except ValueError as e:
            return Response('ValueError: ' + str(e), status = 400)
        except KeyError as e:
            return Response('KeyError: ' + str(e), status = 400)
    else:
        return Response('Content-Type not supported!', status = 400)