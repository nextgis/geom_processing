import requests

layer = iface.activeLayer()

if not layer.isEditable():
    raise Exception('Layer must be editable')
    
features = layer.selectedFeatures()
# if len(features) < 2:
#    raise Exception('Select 2 or more features')

geoms = [f.geometry() for f in features]
for g in geoms:
    g.convertToMultiType()
wkts = [g.asWkt() for g in geoms]


request_data = {
    'wkt': "MultiPolygon(((2 0, 3 -1, 1 -3, 0 -2, -1 -3, -3 -1, -4 0, -3 1, -1 3, 0 2, 1 3, 3 1, 2 0)))",
    "vertexes": 8
}

response = requests.post(
    'http://127.0.0.1:5000/SimplifyWithBuffer',
    json=request_data
)

if response.status_code != 200:
    raise Exception('Simplifying error: %s' % response.text)

l = QgsVectorLayer("multipolygon?crs=epsg:4326", "simplified", "memory")
pr = l.dataProvider()
l.startEditing()
g = QgsGeometry.fromWkt(response.json()['simplified_wkt'])
f = QgsFeature() 
f.setGeometry(g)
pr.addFeatures([f])
l.commitChanges()

QgsProject.instance().addMapLayer(l)