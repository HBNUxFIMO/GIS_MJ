from flask import Flask, jsonify
import numpy as np
import rasterio
from rasterio.transform import xy
from pyproj import Transformer
from flask_cors import CORS
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

app = Flask(__name__)
CORS(app)

# 외부에서 조정 가능한 변수
distance_threshold = 10
region_size = 40

# 1단계: NDWI 데이터 로드 및 좌표 추출
def load_ndwi_data(month):
    file_path = f'/Users/seo/Desktop/GIS/GIS_Pro/ndwi/month{month}_ndwi.tif'
    
    with rasterio.open(file_path) as src:
        ndwi_data = src.read(1)
        transform_data = src.transform
        crs = src.crs
        nodata_value = src.nodata  # NoData 값 가져오기
    
    return ndwi_data, transform_data, crs, nodata_value

def load_ndvi_data(month):
    file_path = f'/Users/seo/Desktop/GIS/GIS_Pro/ndwi/month{month}.tif'
    
    with rasterio.open(file_path) as src:
        ndvi_data = src.read(1)
        transform_data = src.transform
        crs = src.crs
        nodata_value = src.nodata  # NoData 값 가져오기
    
    return ndvi_data, transform_data, crs, nodata_value

def load_ndmi_data(month):
    file_path = f'/Users/seo/Desktop/GIS/GIS_Pro/ndwi/month{month}.tif'
    
    with rasterio.open(file_path) as src:
        ndmi_data = src.read(1)
        transform_data = src.transform
        crs = src.crs
        nodata_value = src.nodata  # NoData 값 가져오기
    
    return ndmi_data, transform_data, crs, nodata_value

# 인접한 영역을 병합하는 함수
def merge_close_areas(polygons, distance_threshold):
    if len(polygons) == 0:
        return []
    merged_polygons = unary_union([poly.buffer(distance_threshold) for poly in polygons])
    
    if isinstance(merged_polygons, Polygon):
        return [merged_polygons]
    elif isinstance(merged_polygons, MultiPolygon):
        return list(merged_polygons.geoms)  # MultiPolygon을 개별 Polygon으로 분리하여 리스트로 반환
    else:
        return []

# 다각형을 단순화하는 함수
def simplify_polygons(polygons, tolerance=0.001):
    return [poly.simplify(tolerance) for poly in polygons]

# 홍수 위험 및 안전 지역 계산 함수
def calculate_flood_risk_areas(ndwi_data, high_threshold, low_threshold, region_size, distance_threshold, nodata_value):
    rows, cols = ndwi_data.shape
    grid_y, grid_x = np.mgrid[0:rows:region_size, 0:cols:region_size]
    
    # NoData 값과 NaN 값 필터링
    valid_mask = (ndwi_data[grid_y, grid_x] != nodata_value) & (~np.isnan(ndwi_data[grid_y, grid_x]))
    
    high_risk_mask = (ndwi_data[grid_y, grid_x] <= high_threshold) & valid_mask
    low_risk_mask = (ndwi_data[grid_y, grid_x] >= low_threshold) & valid_mask
    medium_risk_mask = (ndwi_data[grid_y, grid_x] > high_threshold) & (ndwi_data[grid_y, grid_x] < low_threshold) & valid_mask
    
    high_risk_polygons = [Polygon([(i, j), (i + region_size, j), (i + region_size, j + region_size), (i, j + region_size)]) 
                          for i, j in zip(grid_y[high_risk_mask], grid_x[high_risk_mask])]
    
    low_risk_polygons = [Polygon([(i, j), (i + region_size, j), (i + region_size, j + region_size), (i, j + region_size)]) 
                         for i, j in zip(grid_y[low_risk_mask], grid_x[low_risk_mask])]
    
    medium_risk_polygons = [Polygon([(i, j), (i + region_size, j), (i + region_size, j + region_size), (i, j + region_size)]) 
                            for i, j in zip(grid_y[medium_risk_mask], grid_x[medium_risk_mask])]

    high_risk_areas = merge_close_areas(high_risk_polygons, distance_threshold)
    low_risk_areas = merge_close_areas(low_risk_polygons, distance_threshold)
    medium_risk_areas = merge_close_areas(medium_risk_polygons, distance_threshold)

    # 다각형 단순화 적용
    high_risk_areas = simplify_polygons(high_risk_areas)
    low_risk_areas = simplify_polygons(low_risk_areas)
    medium_risk_areas = simplify_polygons(medium_risk_areas)
    
    return high_risk_areas, medium_risk_areas, low_risk_areas

# 다각형을 지리 좌표로 변환하는 함수
def convert_polygons_to_geocoords(polygons, transform_data, transformer):
    geo_polygons = []
    for polygon in polygons:
        geo_polygon = [(transformer.transform(*xy(transform_data, x, y))) for x, y in polygon.exterior.coords]
        geo_polygons.append(geo_polygon)
    return geo_polygons

# 3단계: API 엔드포인트
@app.route('/api/flood-risk/<int:month>/', methods=['GET'])
def get_flood_risk(month):
    ndwi_data, transform_data, src_crs, nodata_value = load_ndwi_data(month)
    high_threshold = -0.3  # 예시 임계값, 데이터에 맞게 조정 필요
    low_threshold = 0.1    # 예시 임계값, 데이터에 맞게 조정 필요
    
    high_risk, medium_risk, low_risk = calculate_flood_risk_areas(ndwi_data, high_threshold, low_threshold, region_size, distance_threshold, nodata_value)
    
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
