"""
GeoJSON边界提取示例代码

演示如何使用 geojson_bounds.py 模块从GeoJSON文件中提取边界信息。
"""

import sys
sys.path.append('..')

from Utils.geojson_bounds import (
    get_geojson_bounds,
    get_geojson_bounds_tuple,
    print_geojson_bounds,
    get_bounding_box_corners
)

# ============================================
# 示例1: 获取郑州市边界（字典格式）
# ============================================
print("=" * 50)
print("示例1: 获取边界（字典格式）")
print("=" * 50)

geojson_file = "../../boundary/zhengzhou.geojson"

bounds = get_geojson_bounds(geojson_file)
print(f"\n边界字典: {bounds}\n")
print(f"西边界（最小经度）: {bounds['min_lon']}")
print(f"东边界（最大经度）: {bounds['max_lon']}")
print(f"南边界（最小纬度）: {bounds['min_lat']}")
print(f"北边界（最大纬度）: {bounds['max_lat']}")

# ============================================
# 示例2: 获取边界（元组格式）
# ============================================
print("\n" + "=" * 50)
print("示例2: 获取边界（元组格式）")
print("=" * 50)

min_lon, min_lat, max_lon, max_lat = get_geojson_bounds_tuple(geojson_file)
print(f"\n边界元组: ({min_lon}, {min_lat}, {max_lon}, {max_lat})")
print(f"\n这种格式可以直接用于 earthaccess.search_data():")
print(f"  earthaccess.search_data(")
print(f"      bounding_box=({min_lon}, {min_lat}, {max_lon}, {max_lat}),")
print(f"      ...)")

# ============================================
# 示例3: 打印格式化的边界信息
# ============================================
print("\n" + "=" * 50)
print("示例3: 打印格式化的边界信息")
print("=" * 50)

print_geojson_bounds(geojson_file)

# ============================================
# 示例4: 获取边界框的四个角点
# ============================================
print("=" * 50)
print("示例4: 获取边界框的四个角点")
print("=" * 50)

corners = get_bounding_box_corners(geojson_file)
corner_names = ["左下角（西南）", "左上角（西北）", "右上角（东北）", "右下角（东南）"]

print("\n边界框角点坐标:")
for i, (name, (lon, lat)) in enumerate(zip(corner_names, corners), 1):
    print(f"  {i}. {name}: 经度={lon:.4f}°, 纬度={lat:.4f}°")

# ============================================
# 示例5: 在Earthdata下载中使用
# ============================================
print("\n" + "=" * 50)
print("示例5: 在Earthdata下载中使用")
print("=" * 50)

print("\n方式A - 使用边界框（推荐，简单高效）:")
print("```python")
print("from Utils.geojson_bounds import get_geojson_bounds_tuple")
print()
print("# 获取边界")
print("bbox = get_geojson_bounds_tuple('boundary/zhengzhou.geojson')")
print()
print("# 用于搜索")
print("results = earthaccess.search_data(")
print("    short_name='CYGNSS_L1_V3.2',")
print("    bounding_box=bbox,")
print("    temporal=('2020-07-01', '2020-07-31')")
print(")")
print("```")

print("\n方式B - 使用角点构建多边形:")
print("```python")
print("from Utils.geojson_bounds import get_bounding_box_corners")
print()
print("# 获取四个角点")
print("corners = get_bounding_box_corners('boundary/zhengzhou.geojson')")
print()
print("# 添加闭合点（第一个点）")
print("polygon_coords = corners + [corners[0]]")
print()
print("# 用于搜索")
print("results = earthaccess.search_data(")
print("    short_name='CYGNSS_L1_V3.2',")
print("    polygon=polygon_coords,")
print("    temporal=('2020-07-01', '2020-07-31')")
print(")")
print("```")

# ============================================
# 示例6: 计算区域面积（近似）
# ============================================
print("\n" + "=" * 50)
print("示例6: 计算区域大小")
print("=" * 50)

lon_span = max_lon - min_lon
lat_span = max_lat - min_lat

# 粗略估算（在中纬度地区）
# 1度经度 ≈ 111 km * cos(纬度)
# 1度纬度 ≈ 111 km
avg_lat = (min_lat + max_lat) / 2
import math
lon_km = lon_span * 111 * math.cos(math.radians(avg_lat))
lat_km = lat_span * 111

print(f"\n区域大小（近似）:")
print(f"  经度方向: {lon_km:.2f} km")
print(f"  纬度方向: {lat_km:.2f} km")
print(f"  边界框面积: {lon_km * lat_km:.2f} km²")
print(f"\n注意: 这是边界框的面积，实际区域可能小于这个值。")
