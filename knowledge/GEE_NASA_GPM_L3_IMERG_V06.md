# NASA/GPM_L3/IMERG_V06
**数据集 ID**: `NASA/GPM_L3/IMERG_V06`
**数据类型**: ImageCollection
**状态**: 可访问
**生成时间**: 2025-10-06 10:53:51

---
## 📋 数据集描述
> TODO: 添加数据集的详细描述

## 📅 时间信息
- **首张影像日期**: 2000-06-01

## 📊 波段信息
**波段数量**: 9

| 波段名称 | 数据类型 | 描述 |
|---------|---------|------|
| `HQobservationTime` | int | TODO: 添加描述 |
| `HQprecipSource` | int | TODO: 添加描述 |
| `HQprecipitation` | float | TODO: 添加描述 |
| `IRkalmanFilterWeight` | int | TODO: 添加描述 |
| `IRprecipitation` | float | TODO: 添加描述 |
| `precipitationCal` | float | TODO: 添加描述 |
| `precipitationUncal` | float | TODO: 添加描述 |
| `probabilityLiquidPrecipitation` | int | TODO: 添加描述 |
| `randomError` | float | TODO: 添加描述 |

### 波段详细信息

#### `HQobservationTime`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `HQprecipSource`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `HQprecipitation`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `IRkalmanFilterWeight`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `IRprecipitation`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `precipitationCal`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `precipitationUncal`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `probabilityLiquidPrecipitation`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `randomError`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

## 🗺️ 空间信息
- **坐标系统**: `EPSG:4326`
- **空间分辨率**: 0.1 度 (约 11.10 km)

## 🏷️ 属性信息
以下是第一张影像的示例属性：

| 属性名称 | 示例值 |
|---------|--------|
| `system:time_start` | `959817600000` |
| `system:footprint` | `dict` |
| `system:time_end` | `959819399000` |
| `system:version` | `1561155025595214` |
| `system:id` | `NASA/GPM_L3/IMERG_V06/20000601000000` |
| `system:asset_size` | `14567451` |
| `status` | `permanent` |
| `system:index` | `20000601000000` |
| `system:bands` | `dict` |
| `system:band_names` | `list` |

## 💻 使用示例
### Python (Earth Engine API)
```python
import ee
ee.Initialize()

# 加载数据集
dataset = ee.ImageCollection("NASA/GPM_L3/IMERG_V06")

# 过滤时间范围
filtered = dataset.filterDate("2021-01-01", "2021-12-31")

# 过滤空间范围
roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
filtered = filtered.filterBounds(roi)

# 选择波段
selected = filtered.select("HQobservationTime")
```

## 🔗 数据访问
- **GEE 数据目录**: https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V06
- **代码编辑器**: https://code.earthengine.google.com/

## 📚 引用信息
> TODO: 添加数据集的引用信息

## ⚠️ 注意事项
- 本文档由自动脚本生成，部分信息需要人工补充
- 使用前请查阅 GEE 官方文档获取最新信息
- 某些数据集可能需要特定的访问权限

