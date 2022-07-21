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
    'wkt': wkts[0],
    "polygons": 1
}

response = requests.post(
    'http://127.0.0.1:5000/BuildBridges',
    json=request_data
)

if response.status_code != 200:
    raise Exception('Bridging error: %s' % response.text)

l = QgsVectorLayer("multipolygon?crs=epsg:4326", "bridged", "memory")
pr = l.dataProvider()
l.startEditing()
g = QgsGeometry.fromWkt(response.json()['bridged_wkt'])
f = QgsFeature() 
f.setGeometry(g)
pr.addFeatures([f])
l.commitChanges()

QgsProject.instance().addMapLayer(l)