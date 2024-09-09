from flask import Flask, jsonify
import numpy as np
import rasterio
import random

app = Flask(__name__)

def load_ndwi_data(month):
    file_path = f'/Users/seo/Desktop/GIS/GIS_Pro/ndwi/month{month}_ndwi.tif'
    
    with rasterio.open(file_path) as src:
        ndwi_data = src.read(1)
    
    return ndwi_data

def downsample_ndwi(ndwi_data, factor=10):
    return ndwi_data[::factor, ::factor]

def calculate_flood_risk_areas(ndwi_data, high_threshold=0.3, low_threshold=0.6):
    high_risk_areas = []
    medium_risk_areas = []
    low_risk_areas = []
    
    for i in range(ndwi_data.shape[0]):
        for j in range(ndwi_data.shape[1]):
            if ndwi_data[i, j] <= high_threshold:
                polygon = [
                    [i, j],
                    [i+1, j],
                    [i+1, j+1],
                    [i, j+1],
                    [i, j]
                ]
                high_risk_areas.append({
                    'risk_level': 'high',
                    'polygon': polygon
                })
            elif high_threshold < ndwi_data[i, j] <= low_threshold:
                polygon = [
                    [i, j],
                    [i+1, j],
                    [i+1, j+1],
                    [i, j+1],
                    [i, j]
                ]
                medium_risk_areas.append({
                    'risk_level': 'medium',
                    'polygon': polygon
                })
            else:
                polygon = [
                    [i, j],
                    [i+1, j],
                    [i+1, j+1],
                    [i, j+1],
                    [i, j]
                ]
                low_risk_areas.append({
                    'risk_level': 'low',
                    'polygon': polygon
                })
    
    # 각 레벨에서 3개의 영역 선택 (랜덤)
    selected_high_risk = random.sample(high_risk_areas, min(3, len(high_risk_areas)))
    selected_medium_risk = random.sample(medium_risk_areas, min(3, len(medium_risk_areas)))
    selected_low_risk = random.sample(low_risk_areas, min(3, len(low_risk_areas)))
    
    return selected_high_risk, selected_medium_risk, selected_low_risk

@app.route('/api/flood-risk/<int:month>/', methods=['GET'])
def get_flood_risk(month):
    ndwi_data = load_ndwi_data(month)
    ndwi_data_downsampled = downsample_ndwi(ndwi_data)
    high_risk, medium_risk, low_risk = calculate_flood_risk_areas(ndwi_data_downsampled)
    
    response = {
        'month': month,
        'high_risk_areas': high_risk,
        'medium_risk_areas': medium_risk,
        'low_risk_areas': low_risk
    }
    
    return jsonify(response)

@app.route('/')
def a():
    return "hello print"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
