from flask import Flask, request
import json
from poly_info import poly_info

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
    
@app.route("/handler", methods=['POST'])
def handle_geom():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        try:
            wkt1 = request.json["wkt1"]
            return json.dumps(poly_info(wkt1))
        except Exception as e:
            return str(e)
    else:
        return 'Content-Type not supported!'