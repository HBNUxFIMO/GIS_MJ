import rasterio
import numpy as np
import matplotlib.pyplot as plt

# NDVI 파일 경로
month = 4

ndvi_file = f"/Users/seo/Desktop/GIS/GIS_Pro/ndvi/month{month}.tif"

# NDVI 데이터 읽기
with rasterio.open(ndvi_file) as src:
    ndvi_data = src.read(1)  # 첫 번째 밴드를 읽습니다.
    ndvi_meta = src.meta

# 비정상적으로 큰 음수 값을 NaN으로 처리
ndvi_data = np.where(ndvi_data < -1.0e+30, np.nan, ndvi_data)

# NDVI 값이 비정상적으로 큰 값을 가지는 경우 필터링
ndvi_data = np.where((ndvi_data >= -1) & (ndvi_data <= 1), ndvi_data, np.nan)

# NDVI 데이터 통계
ndvi_mean = np.nanmean(ndvi_data)
ndvi_median = np.nanmedian(ndvi_data)
ndvi_std = np.nanstd(ndvi_data)

print(f"NDVI 평균값: {ndvi_mean}")
print(f"NDVI 중앙값: {ndvi_median}")
print(f"NDVI 표준편차: {ndvi_std}")

# NDVI 데이터 시각화
plt.figure(figsize=(10, 8))
plt.imshow(ndvi_data, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(label='NDVI')
plt.title('NDVI Map')
plt.show()

# NDVI 데이터를 특정 임계값에 따라 분류
threshold = 0.2  # 예시 임계값
classified_ndvi = np.where(ndvi_data > threshold, 1, 0)

# 분류된 NDVI 시각화
plt.figure(figsize=(10, 8))
plt.imshow(classified_ndvi, cmap='gray')
plt.title('Classified NDVI Map')
plt.show()
