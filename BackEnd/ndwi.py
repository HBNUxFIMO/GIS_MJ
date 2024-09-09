import rasterio
import numpy as np
import matplotlib.pyplot as plt

# NDWI 파일 경로
month = 11
ndwi_file = f"/Users/seo/Desktop/GIS/GIS_Pro/month{month}/month{month}_ndwi.tif"

# NDWI 데이터 읽기
with rasterio.open(ndwi_file) as src:
    ndwi_data = src.read(1)  # 첫 번째 밴드를 읽습니다.
    ndwi_meta = src.meta

# 비정상적으로 큰 음수 값을 NaN으로 처리
ndwi_data = np.where(ndwi_data < -1.0e+30, np.nan, ndwi_data)

# NDWI 값이 비정상적으로 큰 값을 가지는 경우 필터링
ndwi_data = np.where((ndwi_data >= -1) & (ndwi_data <= 1), ndwi_data, np.nan)

# NDWI 데이터 통계
ndwi_mean = np.nanmean(ndwi_data)
ndwi_median = np.nanmedian(ndwi_data)
ndwi_std = np.nanstd(ndwi_data)

print(f"NDWI 평균값: {ndwi_mean}")
print(f"NDWI 중앙값: {ndwi_median}")
print(f"NDWI 표준편차: {ndwi_std}")

# NDWI 데이터 시각화
plt.figure(figsize=(10, 8))
plt.imshow(ndwi_data, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(label='NDWI')
plt.title('NDWI Map')
plt.show()

# NDWI 데이터를 특정 임계값에 따라 분류
threshold = 0.3  # 예시 임계값
classified_ndwi = np.where(ndwi_data > threshold, 1, 0)

# 분류된 NDWI 시각화
plt.figure(figsize=(10, 8))
plt.imshow(classified_ndwi, cmap='gray')
plt.title('Classified NDWI Map')
plt.show()
