# NASA/GPM_L3/IMERG_V07
**数据集 ID**: `NASA/GPM_L3/IMERG_V07`
**数据类型**: ImageCollection
**状态**: 可访问
**生成时间**: 2025-10-06 10:53:30

---
## 📋 数据集描述
> TODO: 添加数据集的详细描述

## 📅 时间信息
- **首张影像日期**: 1998-01-01

## 📊 波段信息
**波段数量**: 9

| 波段名称 | 数据类型 | 描述 |
|---------|---------|------|
| `MWobservationTime` | int | TODO: 添加描述 |
| `MWprecipSource` | int | TODO: 添加描述 |
| `MWprecipitation` | float | TODO: 添加描述 |
| `IRinfluence` | int | TODO: 添加描述 |
| `IRprecipitation` | float | TODO: 添加描述 |
| `precipitation` | float | TODO: 添加描述 |
| `precipitationUncal` | float | TODO: 添加描述 |
| `probabilityLiquidPrecipitation` | int | TODO: 添加描述 |
| `randomError` | float | TODO: 添加描述 |

### 波段详细信息

#### `MWobservationTime`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `MWprecipSource`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `MWprecipitation`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `IRinfluence`
- **数据类型**: int
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `IRprecipitation`
- **数据类型**: float
- **维度**: [3600, 1800]
- **坐标系统**: EPSG:4326

#### `precipitation`
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
| `system:time_start` | `883612800000` |
| `system:footprint` | `dict` |
| `system:time_end` | `883614600000` |
| `system:version` | `1734125368613689` |
| `system:id` | `NASA/GPM_L3/IMERG_V07/19980101000000` |
| `system:asset_size` | `10336829` |
| `status` | `permanent` |
| `system:index` | `19980101000000` |
| `system:bands` | `dict` |
| `system:band_names` | `list` |

## 💻 使用示例
### Python (Earth Engine API)
```python
import ee
ee.Initialize()

# 加载数据集
dataset = ee.ImageCollection("NASA/GPM_L3/IMERG_V07")

# 过滤时间范围
filtered = dataset.filterDate("2021-01-01", "2021-12-31")

# 过滤空间范围
roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
filtered = filtered.filterBounds(roi)

# 选择波段
selected = filtered.select("MWobservationTime")
```

## 🔗 数据访问
- **GEE 数据目录**: https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_V07
- **代码编辑器**: https://code.earthengine.google.com/

## 📚 引用信息
> TODO: 添加数据集的引用信息

## ⚠️ 注意事项
- 本文档由自动脚本生成，部分信息需要人工补充
- 使用前请查阅 GEE 官方文档获取最新信息
- 某些数据集可能需要特定的访问权限

