import rasterio
import numpy as np
import matplotlib.pyplot as plt

# NDMI 파일 경로
month = 8
ndmi_file = f"/Users/seo/Desktop/GIS/GIS_Pro/ndmi/month{month}.tif"

# NDMI 데이터 읽기
with rasterio.open(ndmi_file) as src:
    ndmi_data = src.read(1)  # 첫 번째 밴드를 읽습니다.
    ndmi_meta = src.meta

# 비정상적으로 큰 음수 값을 NaN으로 처리
ndmi_data = np.where(ndmi_data < -1.0e+30, np.nan, ndmi_data)

# NDMI 값이 비정상적으로 큰 값을 가지는 경우 필터링
ndmi_data = np.where((ndmi_data >= -1) & (ndmi_data <= 1), ndmi_data, np.nan)

# NDMI 데이터 통계
ndmi_mean = np.nanmean(ndmi_data)
ndmi_median = np.nanmedian(ndmi_data)
ndmi_std = np.nanstd(ndmi_data)

print(f"NDMI 평균값: {ndmi_mean}")
print(f"NDMI 중앙값: {ndmi_median}")
print(f"NDMI 표준편차: {ndmi_std}")

# NDMI 데이터 시각화
plt.figure(figsize=(10, 8))
plt.imshow(ndmi_data, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(label='NDMI')
plt.title('NDMI Map')
plt.show()

# NDMI 데이터를 특정 임계값에 따라 분류
threshold = 0.2  # 예시 임계값
classified_ndmi = np.where(ndmi_data > threshold, 1, 0)

# 분류된 NDMI 시각화
plt.figure(figsize=(10, 8))
plt.imshow(classified_ndmi, cmap='gray')
plt.title('Classified NDMI Map')
plt.show()
