from flask import Flask, jsonify
import numpy as np
import rasterio
import random
from rasterio.transform import xy
from pyproj import Transformer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_ndwi_data(month):
    file_path = f'/Users/seo/Desktop/GIS/GIS_Pro/ndwi/month{month}_ndwi.tif'
    
    with rasterio.open(file_path) as src:
        ndwi_data = src.read(1)
        transform_data = src.transform
        crs = src.crs
        bounds = src.bounds
    
    return ndwi_data, transform_data, crs, bounds

def downsample_ndwi(ndwi_data, factor=10):
    return ndwi_data[::factor, ::factor]

def calculate_flood_risk_areas(ndwi_data, high_threshold=-1.5, low_threshold=-1.0, inner_region_size=30, outer_region_size=200):
    high_risk_areas = []
    low_risk_areas = []
    
    rows, cols = ndwi_data.shape
    
    for i in range(0, rows, inner_region_size):
        for j in range(0, cols, inner_region_size):
            region = ndwi_data[i:i+inner_region_size, j:j+inner_region_size]
            avg_ndwi = np.mean(region)
            
            sides = random.randint(4, 8)
            inner_polygon = create_polygon(i, j, inner_region_size, sides)
            
            if avg_ndwi <= high_threshold:
                high_risk_areas.append({
                    'risk_level': 'high',
                    'polygon': inner_polygon
                })
            elif avg_ndwi > low_threshold:
                low_risk_areas.append({
                    'risk_level': 'low',
                    'polygon': inner_polygon
                })

    selected_high_risk = cluster_and_select(high_risk_areas, num_clusters=min(3, len(high_risk_areas)))
    selected_low_risk = cluster_and_select(low_risk_areas, num_clusters=min(3, len(low_risk_areas)))

    medium_risk_areas = []

    # Create medium risk areas around selected high and low risk areas
    for area in selected_high_risk + selected_low_risk:
        medium_polygon = create_polygon_from_center(area['polygon'], outer_region_size, sides)
        medium_risk_areas.append({
            'risk_level': 'medium',
            'polygon': medium_polygon
        })

    return selected_high_risk, medium_risk_areas, selected_low_risk

def create_polygon(x, y, size, sides):
    angle_step = 360 / sides
    polygon = []
    for k in range(sides):
        angle = np.deg2rad(k * angle_step)
        dx = size / 2 * np.cos(angle)
        dy = size / 2 * np.sin(angle)
        polygon.append([x + dx, y + dy])
    polygon.append(polygon[0])
    return polygon

def create_polygon_from_center(polygon, size, sides):
    center_x = np.mean([point[0] for point in polygon])
    center_y = np.mean([point[1] for point in polygon])
    return create_polygon(center_x, center_y, size, sides)

def cluster_and_select(risk_areas, num_clusters):
    if len(risk_areas) == 0:
        return []
    sorted_areas = sorted(risk_areas, key=lambda x: np.mean([p[0] for p in x['polygon']]))
    return sorted_areas[:num_clusters]

def pixel_to_geocoord(pixel_x, pixel_y, transform_data, transformer):
    lon, lat = xy(transform_data, pixel_y, pixel_x)
    lon, lat = transformer.transform(lon, lat)
    return lon, lat

def convert_polygons_to_geocoords(polygon_data, transform_data, transformer):
    geo_polygons = []
    for polygon in polygon_data:
        geo_polygon = [pixel_to_geocoord(x, y, transform_data, transformer) for x, y in polygon['polygon']]
        geo_polygons.append({
            'risk_level': polygon['risk_level'],
            'polygon': geo_polygon
        })
    return geo_polygons

@app.route('/api/flood-risk/<int:month>/', methods=['GET'])
def get_flood_risk(month):
    ndwi_data, transform_data, src_crs, bounds = load_ndwi_data(month)
    ndwi_data_downsampled = downsample_ndwi(ndwi_data)
    
    high_risk, medium_risk, low_risk = calculate_flood_risk_areas(ndwi_data_downsampled, inner_region_size=30, outer_region_size=200)
    
    transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
    
    high_risk_geo = convert_polygons_to_geocoords(high_risk, transform_data, transformer)
    medium_risk_geo = convert_polygons_to_geocoords(medium_risk, transform_data, transformer)
    low_risk_geo = convert_polygons_to_geocoords(low_risk, transform_data, transformer)
    
    response = {
        'month': month,
        'high_risk_areas': high_risk_geo,
        'medium_risk_areas': medium_risk_geo,
        'low_risk_areas': low_risk_geo
    }
    
    return jsonify(response)

@app.route('/')
def a():
    return "hello print"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
