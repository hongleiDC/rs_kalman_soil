# MODIS/006/MOD13Q1
**数据集 ID**: `MODIS/006/MOD13Q1`
**数据类型**: ImageCollection
**状态**: 可访问
**生成时间**: 2025-10-06 10:56:43

---
## 📋 数据集描述
> TODO: 添加数据集的详细描述

## 📅 时间信息
- **首张影像日期**: 2000-02-18

## 📊 波段信息
**波段数量**: 12

| 波段名称 | 数据类型 | 描述 |
|---------|---------|------|
| `NDVI` | int | TODO: 添加描述 |
| `EVI` | int | TODO: 添加描述 |
| `DetailedQA` | int | TODO: 添加描述 |
| `sur_refl_b01` | int | TODO: 添加描述 |
| `sur_refl_b02` | int | TODO: 添加描述 |
| `sur_refl_b03` | int | TODO: 添加描述 |
| `sur_refl_b07` | int | TODO: 添加描述 |
| `ViewZenith` | int | TODO: 添加描述 |
| `SolarZenith` | int | TODO: 添加描述 |
| `RelativeAzimuth` | int | TODO: 添加描述 |
| `DayOfYear` | int | TODO: 添加描述 |
| `SummaryQA` | int | TODO: 添加描述 |

### 波段详细信息

#### `NDVI`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `EVI`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `DetailedQA`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `sur_refl_b01`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `sur_refl_b02`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `sur_refl_b03`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `sur_refl_b07`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `ViewZenith`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `SolarZenith`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `RelativeAzimuth`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `DayOfYear`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

#### `SummaryQA`
- **数据类型**: int
- **维度**: [172800, 86400]
- **坐标系统**: SR-ORG:6974

## 🗺️ 空间信息
- **坐标系统**: `SR-ORG:6974`
- **空间分辨率**: 231.65635826395825 度 (约 25713.86 km)

## 🏷️ 属性信息
以下是第一张影像的示例属性：

| 属性名称 | 示例值 |
|---------|--------|
| `system:time_start` | `950832000000` |
| `google:max_source_file_timestamp` | `1493667561435` |
| `system:footprint` | `dict` |
| `system:time_end` | `952214400000` |
| `system:version` | `1638765185312446` |
| `system:id` | `MODIS/006/MOD13Q1/2000_02_18` |
| `system:asset_size` | `28219636986` |
| `system:index` | `2000_02_18` |
| `system:bands` | `dict` |
| `system:band_names` | `list` |

## 💻 使用示例
### Python (Earth Engine API)
```python
import ee
ee.Initialize()

# 加载数据集
dataset = ee.ImageCollection("MODIS/006/MOD13Q1")

# 过滤时间范围
filtered = dataset.filterDate("2021-01-01", "2021-12-31")

# 过滤空间范围
roi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
filtered = filtered.filterBounds(roi)

# 选择波段
selected = filtered.select("NDVI")
```

## 🔗 数据访问
- **GEE 数据目录**: https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD13Q1
- **代码编辑器**: https://code.earthengine.google.com/

## 📚 引用信息
> TODO: 添加数据集的引用信息

## ⚠️ 注意事项
- 本文档由自动脚本生成，部分信息需要人工补充
- 使用前请查阅 GEE 官方文档获取最新信息
- 某些数据集可能需要特定的访问权限

