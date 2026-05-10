import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import h3
import folium
import json


def assemble_polylines(hexagons):
    polylines = []
    lat = []
    lng = []
    for hex_ in hexagons:
        boundary = list(h3.cell_to_boundary(hex_))
        polyline = boundary + [boundary[0]]
        lat.extend(v[0] for v in polyline)
        lng.extend(v[1] for v in polyline)
        polylines.append(polyline)
    return polylines


def visualize_hexagons(hexagons, color="red", folium_map=None, zoom_start=13):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons.
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex_ in hexagons:
        boundary = list(h3.cell_to_boundary(hex_))
        polyline = boundary + [boundary[0]]
        lat.extend(v[0] for v in polyline)
        lng.extend(v[1] for v in polyline)
        polylines.append(polyline)

    if folium_map is None:
        m = folium.Map(location=[sum(lat) / len(lat), sum(lng) / len(lng)],
                       zoom_start=zoom_start, tiles='cartodbpositron')
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(locations=polyline, weight=1, opacity=0.8, color=color)
        m.add_child(my_PolyLine)
    return m


def visualize_polygon(polyline, color):
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location=[sum(lat) / len(lat), sum(lng) / len(lng)],
                   zoom_start=13, tiles='cartodbpositron')
    my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color=color)
    m.add_child(my_PolyLine)
    return m


def get_h3_neighbors(h3_address, layers=1):
    neighbors = {i: h3.grid_ring(h3_address, i) for i in range(layers + 1)}
    return neighbors


def get_h3_address(latlon, resolution):
    lat, lon = latlon
    h3_address = h3.latlng_to_cell(lat, lon, resolution)
    return h3_address


def read_json(file):
    with open(file) as f:
        json_file = json.load(f)
    return json_file
