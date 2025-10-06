# Google Earth Engine 数据集汇总文档

本文档汇总了项目中使用的所有 GEE 数据集的详细信息。

**生成时间**: 2025-10-06  
**项目**: rs_kalman_soil - GNSS-R 土壤湿度卡尔曼滤波同化系统

---

## 📑 目录

1. [GPM IMERG 降水数据](#1-gpm-imerg-降水数据)
   - [NASA/GPM_L3/IMERG_V07](#11-nasagpm_l3imerg_v07-推荐)
   - [NASA/GPM_L3/IMERG_V06](#12-nasagpm_l3imerg_v06-已弃用)

2. [ERA5-Land 再分析数据](#2-era5-land-再分析数据)
   - [ECMWF/ERA5_LAND/DAILY_AGGR](#21-ecmwfera5_landdaily_aggr-推荐)
   - [ECMWF/ERA5_LAND/HOURLY](#22-ecmwfera5_landhourly)

3. [MODIS NDVI 植被指数](#3-modis-ndvi-植被指数)
   - [MODIS/061/MOD13Q1](#31-modis061mod13q1-推荐)
   - [MODIS/006/MOD13Q1](#32-modis006mod13q1-已弃用)
   - [MODIS/061/MYD13Q1](#33-modis061myd13q1)

4. [数据集对比](#4-数据集对比)
5. [使用建议](#5-使用建议)

---

## 1. GPM IMERG 降水数据

### 1.1 NASA/GPM_L3/IMERG_V07 (推荐)

**数据集 ID**: `NASA/GPM_L3/IMERG_V07`

#### 基本信息
- **全称**: Global Precipitation Measurement (GPM) Integrated Multi-satellitE Retrievals for GPM (IMERG) V07
- **时间范围**: 1998-01-01 至今
- **时间分辨率**: 30 分钟
- **空间分辨率**: 0.1° (~11 km)
- **覆盖范围**: 全球 (90°S - 90°N)
- **数据类型**: ImageCollection

#### 主要波段
| 波段名称 | 数据类型 | 单位 | 说明 |
|---------|---------|------|------|
| `precipitation` | float | mm/hr | **综合降水率** (推荐使用) |
| `precipitationUncal` | float | mm/hr | 未校准降水率 |
| `MWprecipitation` | float | mm/hr | 微波降水率 |
| `IRprecipitation` | float | mm/hr | 红外降水率 |
| `randomError` | float | mm/hr | 随机误差估计 |
| `probabilityLiquidPrecipitation` | int | % | 液态降水概率 |
| `MWobservationTime` | int | minutes | 微波观测时间 |
| `MWprecipSource` | int | - | 微波数据源标识 |
| `IRinfluence` | int | % | 红外影响百分比 |

#### 使用示例
```python
import ee
ee.Initialize()

# 加载 IMERG V07 数据
imerg = ee.ImageCollection("NASA/GPM_L3/IMERG_V07")

# 过滤时间和空间
roi = ee.Geometry.Rectangle([113.0, 34.0, 114.0, 35.0])  # 郑州区域
filtered = imerg.filterDate("2021-07-01", "2021-07-31") \
                .filterBounds(roi) \
                .select("precipitation")

# 计算日降水量 (mm/day)
# IMERG 是 30 分钟数据，每天 48 个时次
daily_precip = filtered.map(lambda img: img.multiply(0.5))  # 30min -> hour
daily_sum = daily_precip.sum()

# 获取区域平均值
mean_precip = daily_sum.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=roi,
    scale=11000
).getInfo()
```

#### 数据质量说明
- **优势**: 
  - 最新版本，数据质量最优
  - 融合了多个卫星传感器数据
  - 提供误差估计
  - 时间分辨率高（30分钟）
  
- **注意事项**:
  - 降水率单位是 mm/hr，需要根据时间间隔转换为累积降水量
  - 早期数据（2000年前）仅基于红外估算，精度较低
  - 高纬度地区（>60°）精度下降

#### 详细文档
📄 [GEE_NASA_GPM_L3_IMERG_V07.md](./GEE_NASA_GPM_L3_IMERG_V07.md)

---

### 1.2 NASA/GPM_L3/IMERG_V06 (已弃用)

**数据集 ID**: `NASA/GPM_L3/IMERG_V06`

⚠️ **此版本已被弃用，建议使用 V07**

#### 基本信息
- **时间范围**: 2000-06-01 至 2023-12-31
- **时间分辨率**: 30 分钟
- **空间分辨率**: 0.1° (~11 km)

#### 详细文档
📄 [GEE_NASA_GPM_L3_IMERG_V06.md](./GEE_NASA_GPM_L3_IMERG_V06.md)

---

## 2. ERA5-Land 再分析数据

### 2.1 ECMWF/ERA5_LAND/DAILY_AGGR (推荐)

**数据集 ID**: `ECMWF/ERA5_LAND/DAILY_AGGR`

#### 基本信息
- **全称**: ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis
- **时间范围**: 1950-01-02 至今
- **时间分辨率**: 日
- **空间分辨率**: 0.1° (~11 km)
- **覆盖范围**: 全球
- **波段数量**: 150+

#### 关键波段（土壤湿度相关）
| 波段名称 | 数据类型 | 单位 | 说明 |
|---------|---------|------|------|
| `volumetric_soil_water_layer_1` | float | m³/m³ | **0-7cm 土壤体积含水量** |
| `volumetric_soil_water_layer_2` | float | m³/m³ | 7-28cm 土壤体积含水量 |
| `volumetric_soil_water_layer_3` | float | m³/m³ | 28-100cm 土壤体积含水量 |
| `volumetric_soil_water_layer_4` | float | m³/m³ | 100-289cm 土壤体积含水量 |
| `surface_pressure` | float | Pa | 地表气压 |
| `temperature_2m` | float | K | 2米气温 |
| `dewpoint_temperature_2m` | float | K | 2米露点温度 |
| `total_precipitation_sum` | float | m | 总降水量 |
| `potential_evaporation_sum` | float | m | 潜在蒸散发 |
| `total_evaporation_sum` | float | m | 总蒸散发 |
| `skin_temperature` | float | K | 地表温度 |
| `soil_temperature_level_1` | float | K | 0-7cm 土壤温度 |
| `soil_temperature_level_2` | float | K | 7-28cm 土壤温度 |
| `soil_temperature_level_3` | float | K | 28-100cm 土壤温度 |
| `soil_temperature_level_4` | float | K | 100-289cm 土壤温度 |

#### 使用示例
```python
import ee
ee.Initialize()

# 加载 ERA5-Land 日聚合数据
era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")

# 过滤时间和空间
roi = ee.Geometry.Rectangle([113.0, 34.0, 114.0, 35.0])
filtered = era5.filterDate("2021-07-01", "2021-07-31") \
               .filterBounds(roi)

# 选择关键变量
sm_temp = filtered.select([
    'volumetric_soil_water_layer_1',  # 表层土壤湿度
    'temperature_2m',                  # 2米气温
    'total_precipitation_sum',         # 总降水
    'potential_evaporation_sum'        # 潜在蒸散发
])

# 提取时间序列
def extract_values(image):
    # 单位转换
    precip = image.select('total_precipitation_sum').multiply(1000)  # m -> mm
    pet = image.select('potential_evaporation_sum').multiply(-1000)  # m -> mm (注意符号)
    temp = image.select('temperature_2m').subtract(273.15)  # K -> °C
    sm = image.select('volumetric_soil_water_layer_1')
    
    stats = ee.Image.cat([sm, temp, precip, pet]).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=11000
    )
    
    return ee.Feature(None, {
        'date': image.date().format('YYYY-MM-dd'),
        'soil_moisture': stats.get('volumetric_soil_water_layer_1'),
        'temperature': stats.get('temperature_2m'),
        'precipitation': stats.get('total_precipitation_sum'),
        'pet': stats.get('potential_evaporation_sum')
    })

time_series = sm_temp.map(extract_values).getInfo()
```

#### 数据质量说明
- **优势**:
  - 日聚合数据，直接可用，无需额外处理
  - 时间序列长，适合长期分析
  - 变量齐全，包含土壤湿度、温度、降水等
  - 空间分辨率较高（0.1°）

- **注意事项**:
  - 土壤湿度是模型模拟值，非直接观测
  - 潜在蒸散发为负值，使用时需要取反
  - 降水、蒸散发单位是米（m），需转换为毫米（mm）
  - 温度单位是开尔文（K），需转换为摄氏度（°C）

#### 详细文档
📄 [GEE_ECMWF_ERA5_LAND_DAILY_AGGR.md](./GEE_ECMWF_ERA5_LAND_DAILY_AGGR.md)

---

### 2.2 ECMWF/ERA5_LAND/HOURLY

**数据集 ID**: `ECMWF/ERA5_LAND/HOURLY`

#### 基本信息
- **时间范围**: 1950-01-01 至今
- **时间分辨率**: 小时
- **空间分辨率**: 0.1° (~11 km)
- **波段数量**: 69

#### 说明
- 提供小时分辨率数据，适合高时间分辨率分析
- 波段与日聚合版本类似，但数据量更大
- 如无特殊需求，建议使用日聚合版本

#### 详细文档
📄 [GEE_ECMWF_ERA5_LAND_HOURLY.md](./GEE_ECMWF_ERA5_LAND_HOURLY.md)

---

## 3. MODIS NDVI 植被指数

### 3.1 MODIS/061/MOD13Q1 (推荐)

**数据集 ID**: `MODIS/061/MOD13Q1`

#### 基本信息
- **全称**: MODIS Terra Vegetation Indices 16-Day Global 250m (Collection 6.1)
- **卫星**: Terra
- **时间范围**: 2000-02-18 至今
- **时间分辨率**: 16 天
- **空间分辨率**: 250 m
- **覆盖范围**: 全球

#### 主要波段
| 波段名称 | 数据类型 | 范围 | 说明 |
|---------|---------|------|------|
| `NDVI` | int16 | -2000 to 10000 | **归一化植被指数** (实际值 = NDVI / 10000) |
| `EVI` | int16 | -2000 to 10000 | 增强植被指数 |
| `sur_refl_b01` | int16 | 0 to 10000 | 红光波段反射率 |
| `sur_refl_b02` | int16 | 0 to 10000 | 近红外波段反射率 |
| `sur_refl_b03` | int16 | 0 to 10000 | 蓝光波段反射率 |
| `sur_refl_b07` | int16 | 0 to 10000 | 中红外波段反射率 |
| `ViewZenith` | int16 | 0 to 18000 | 观测天顶角 (度 * 100) |
| `SolarZenith` | int16 | 0 to 18000 | 太阳天顶角 (度 * 100) |
| `RelativeAzimuth` | int16 | -18000 to 18000 | 相对方位角 (度 * 100) |
| `DayOfYear` | int16 | 1 to 366 | 年积日 |
| `SummaryQA` | int16 | 0 to 3 | 质量评估 |
| `DetailedQA` | uint16 | 0 to 65534 | 详细质量标识 |

#### 使用示例
```python
import ee
ee.Initialize()

# 加载 MODIS NDVI 数据
modis = ee.ImageCollection("MODIS/061/MOD13Q1")

# 过滤时间和空间
roi = ee.Geometry.Rectangle([113.0, 34.0, 114.0, 35.0])
filtered = modis.filterDate("2021-07-01", "2021-07-31") \
                .filterBounds(roi)

# 选择 NDVI 并进行缩放
def scale_ndvi(image):
    ndvi = image.select('NDVI').multiply(0.0001)  # 缩放到 -0.2 ~ 1.0
    
    # 质量过滤
    qa = image.select('SummaryQA')
    # 0 = 好, 1 = 一般, 2 = 雪/冰, 3 = 云
    mask = qa.lte(1)  # 只保留好和一般的数据
    
    return ndvi.updateMask(mask).copyProperties(image, ['system:time_start'])

ndvi_scaled = filtered.map(scale_ndvi)

# 计算均值
mean_ndvi = ndvi_scaled.mean().reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=roi,
    scale=250
).getInfo()

print(f"平均 NDVI: {mean_ndvi.get('NDVI')}")
```

#### 数据质量说明
- **优势**:
  - 最新 Collection 6.1，质量控制更严格
  - 空间分辨率高（250m）
  - 提供详细的质量标识
  - 长时间序列（2000年至今）

- **注意事项**:
  - NDVI 值需要除以 10000 进行缩放
  - 云、雪、冰会影响数据质量，需要使用质量波段过滤
  - 16天合成产品，不是每日数据
  - 使用前建议进行质量控制

#### 质量标识说明
**SummaryQA** 值:
- 0: 好质量
- 1: 一般质量
- 2: 雪/冰覆盖
- 3: 云覆盖

#### 详细文档
📄 [GEE_MODIS_061_MOD13Q1.md](./GEE_MODIS_061_MOD13Q1.md)

---

### 3.2 MODIS/006/MOD13Q1 (已弃用)

**数据集 ID**: `MODIS/006/MOD13Q1`

⚠️ **此版本已被弃用，建议使用 Collection 6.1 (MODIS/061/MOD13Q1)**

#### 详细文档
📄 [GEE_MODIS_006_MOD13Q1.md](./GEE_MODIS_006_MOD13Q1.md)

---

### 3.3 MODIS/061/MYD13Q1

**数据集 ID**: `MODIS/061/MYD13Q1`

#### 基本信息
- **卫星**: Aqua (相对于 MOD13Q1 的 Terra)
- **时间范围**: 2002-07-04 至今
- **其他特性**: 与 MOD13Q1 相同

#### 说明
- 来自 Aqua 卫星，观测时间与 Terra 不同（下午过境）
- 可与 MOD13Q1 结合使用，提高时间覆盖
- 波段结构与 MOD13Q1 完全相同

#### 详细文档
📄 [GEE_MODIS_061_MYD13Q1.md](./GEE_MODIS_061_MYD13Q1.md)

---

## 4. 数据集对比

### 4.1 版本对比

| 数据集类型 | 推荐版本 | 弃用版本 | 主要区别 |
|----------|---------|---------|---------|
| GPM IMERG | V07 | V06 | V07 算法改进，精度提升 |
| ERA5-Land | DAILY_AGGR | HOURLY | 日聚合更便于使用 |
| MODIS NDVI | 061/MOD13Q1 | 006/MOD13Q1 | Collection 6.1 质量更高 |

### 4.2 时空分辨率对比

| 数据集 | 空间分辨率 | 时间分辨率 | 数据起始 |
|-------|----------|----------|---------|
| IMERG V07 | 0.1° (~11 km) | 30 分钟 | 1998-01-01 |
| ERA5-Land Daily | 0.1° (~11 km) | 日 | 1950-01-02 |
| ERA5-Land Hourly | 0.1° (~11 km) | 小时 | 1950-01-01 |
| MODIS MOD13Q1 | 250 m | 16 天 | 2000-02-18 |
| MODIS MYD13Q1 | 250 m | 16 天 | 2002-07-04 |

### 4.3 数据量对比

| 数据集 | 波段数 | 单个影像大小 | 建议使用场景 |
|-------|-------|------------|-------------|
| IMERG V07 | 9 | ~10 MB | 降水监测、水文分析 |
| ERA5-Land Daily | 150+ | 较大 | 土壤湿度、气象分析 |
| ERA5-Land Hourly | 69 | 大 | 高时间分辨率分析 |
| MODIS MOD13Q1 | 12 | 适中 | 植被监测、农业应用 |

---

## 5. 使用建议

### 5.1 数据选择策略

**对于土壤湿度同化项目**:
1. **降水数据**: 优先使用 `NASA/GPM_L3/IMERG_V07`
   - 时间分辨率高，适合日尺度同化
   - 全球覆盖，数据质量好

2. **土壤湿度/气象**: 优先使用 `ECMWF/ERA5_LAND/DAILY_AGGR`
   - 直接提供土壤湿度，可作为背景场或验证
   - 日聚合数据，便于处理

3. **植被指数**: 优先使用 `MODIS/061/MOD13Q1`
   - 空间分辨率最高（250m）
   - 长时间序列，数据稳定

### 5.2 数据处理流程

```python
import ee
ee.Initialize()

def prepare_daily_data(roi, start_date, end_date):
    """准备日尺度的多源数据"""
    
    # 1. IMERG 降水 (30分钟 -> 日)
    imerg = ee.ImageCollection("NASA/GPM_L3/IMERG_V07") \
        .filterDate(start_date, end_date) \
        .filterBounds(roi) \
        .select('precipitation')
    
    # 聚合到日尺度 (mm/day)
    def daily_precip(date):
        d = ee.Date(date)
        daily = imerg.filterDate(d, d.advance(1, 'day')).sum().multiply(0.5)
        return daily.set('system:time_start', d.millis())
    
    dates = ee.List.sequence(0, ee.Date(end_date).difference(ee.Date(start_date), 'day'))
    daily_precip_ic = ee.ImageCollection(dates.map(
        lambda d: daily_precip(ee.Date(start_date).advance(d, 'day'))
    ))
    
    # 2. ERA5-Land (已经是日数据)
    era5 = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR") \
        .filterDate(start_date, end_date) \
        .filterBounds(roi)
    
    # 选择关键变量并单位转换
    def process_era5(img):
        sm = img.select('volumetric_soil_water_layer_1')
        temp = img.select('temperature_2m').subtract(273.15)  # K -> °C
        pet = img.select('potential_evaporation_sum').multiply(-1000)  # m -> mm
        return ee.Image.cat([sm, temp, pet]).copyProperties(img, ['system:time_start'])
    
    era5_processed = era5.map(process_era5)
    
    # 3. MODIS NDVI (16天 -> 插值到日)
    modis = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterDate(start_date, end_date) \
        .filterBounds(roi) \
        .select('NDVI')
    
    def scale_and_filter(img):
        ndvi = img.select('NDVI').multiply(0.0001)
        qa = img.select('SummaryQA')
        return ndvi.updateMask(qa.lte(1)).copyProperties(img, ['system:time_start'])
    
    modis_scaled = modis.map(scale_and_filter)
    
    return {
        'precipitation': daily_precip_ic,
        'era5': era5_processed,
        'ndvi': modis_scaled
    }

# 使用示例
roi = ee.Geometry.Rectangle([113.0, 34.0, 114.0, 35.0])
data = prepare_daily_data(roi, "2021-07-01", "2021-07-31")
```

### 5.3 注意事项

1. **单位转换**:
   - IMERG: mm/hr -> mm/day (乘以 0.5，因为是30分钟数据)
   - ERA5-Land: K -> °C (减 273.15), m -> mm (乘 1000)
   - MODIS NDVI: 缩放因子 0.0001

2. **质量控制**:
   - MODIS 使用 SummaryQA 过滤
   - IMERG 检查 randomError 波段
   - ERA5-Land 通常不需要额外质量控制

3. **时间匹配**:
   - IMERG 和 ERA5 可直接匹配到日
   - MODIS 16天合成需要插值或直接使用

4. **空间尺度**:
   - 考虑不同数据集的分辨率差异
   - 统一到合适的分析尺度（如0.1°或250m）

---

## 📎 附录

### A. 所有数据集详细文档

1. [GEE_NASA_GPM_L3_IMERG_V07.md](./GEE_NASA_GPM_L3_IMERG_V07.md)
2. [GEE_NASA_GPM_L3_IMERG_V06.md](./GEE_NASA_GPM_L3_IMERG_V06.md)
3. [GEE_ECMWF_ERA5_LAND_DAILY_AGGR.md](./GEE_ECMWF_ERA5_LAND_DAILY_AGGR.md)
4. [GEE_ECMWF_ERA5_LAND_HOURLY.md](./GEE_ECMWF_ERA5_LAND_HOURLY.md)
5. [GEE_MODIS_061_MOD13Q1.md](./GEE_MODIS_061_MOD13Q1.md)
6. [GEE_MODIS_006_MOD13Q1.md](./GEE_MODIS_006_MOD13Q1.md)
7. [GEE_MODIS_061_MYD13Q1.md](./GEE_MODIS_061_MYD13Q1.md)

### B. 相关资源

- **GEE 官方文档**: https://developers.google.com/earth-engine
- **GEE 数据目录**: https://developers.google.com/earth-engine/datasets
- **GEE Python API**: https://developers.google.com/earth-engine/guides/python_install

### C. 更新记录

- 2025-10-06: 初始版本，包含所有7个数据集的详细信息

---

**文档维护**: 本文档由自动化脚本生成，如有更新需求请修改 `gee_dataset_inspector.py`
