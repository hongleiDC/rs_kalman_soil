# ERA5 数据下载器

基于伪代码实现的完整 ERA5 再分析数据下载工具。

## 功能特性

✅ **多数据集支持**
- 单层数据 (reanalysis-era5-single-levels)
- 气压层数据 (reanalysis-era5-pressure-levels)
- 陆地数据 (reanalysis-era5-land)

✅ **灵活配置**
- 自定义时间范围和时间分辨率
- 空间范围裁剪（边界框）
- 格点分辨率自定义
- 多种输出格式（NetCDF、GRIB）

✅ **可靠下载**
- 自动重试机制（指数退避）
- 断点续传支持
- 详细日志记录
- 错误分类（瞬态错误 vs 致命错误）

✅ **智能分块**
- 按月或按日分块下载
- 避免单次请求过大
- 分层目录结构组织

## 快速开始

### 1. 安装依赖

```bash
pip install cdsapi
```

### 2. 配置 CDS API 认证

创建文件 `~/.cdsapirc`:

```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR-UID:YOUR-API-KEY
```

在 [CDS API 页面](https://cds.climate.copernicus.eu/api-how-to) 获取你的 API 密钥。

### 3. 基本用法

```python
from download.ERA5Downloader import ERA5Downloader

config = {
    "dataset": "reanalysis-era5-single-levels",
    "variables": ["2m_temperature", "total_precipitation"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "hours": ["00", "06", "12", "18"],
    "area": [35, 112, 34, 115],  # [N, W, S, E]
    "grid": "0.25/0.25",
    "format": "netcdf",
    "out_dir": "./era5_data"
}

downloader = ERA5Downloader(config)
downloader.download()
```

## 配置选项

### 必填参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `dataset` | str | 数据集名称 | `"reanalysis-era5-single-levels"` |
| `variables` | list | 变量列表 | `["2m_temperature"]` |
| `start_date` | str | 开始日期 | `"2020-07-01"` |
| `end_date` | str | 结束日期 | `"2020-07-31"` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backend` | str | `"cds"` | 下载后端（`"cds"` 或 `"aws"`） |
| `pressure_levels` | list | `[]` | 气压层列表（气压层数据集必填） |
| `hours` | list | `["00","06","12","18"]` | 小时列表 |
| `area` | list | `None` | 地理范围 `[N, W, S, E]` |
| `grid` | str | `None` | 格点分辨率 `"0.25/0.25"` |
| `product_type` | str | `"reanalysis"` | 产品类型 |
| `format` | str | `"netcdf"` | 输出格式（`"netcdf"` 或 `"grib"`） |
| `chunking` | str | `"monthly"` | 分块方式（`"monthly"` 或 `"daily"`） |
| `out_dir` | str | `"./era5"` | 输出目录 |
| `file_naming` | str | 见下文 | 文件命名模板 |
| `max_retries` | int | `5` | 最大重试次数 |
| `retry_backoff_sec` | int | `10` | 重试退避时间（秒） |
| `timeout_minutes` | int | `120` | 超时时间（分钟） |

### 文件命名模板

默认模板: `"{dataset}_{tag}_{YYYY}{MM}{DD}.{fmt}"`

可用占位符:
- `{dataset}`: 数据集名称
- `{tag}`: 变量或气压层标签
- `{YYYY}`: 年份（4位）
- `{MM}`: 月份（2位）
- `{DD}`: 日期（2位）
- `{fmt}`: 文件格式扩展名

示例: `ERA5_2m_temperature_202007.nc`

## 使用示例

### 示例 1: 下载单层数据

```python
config = {
    "dataset": "reanalysis-era5-single-levels",
    "variables": ["2m_temperature", "total_precipitation"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "area": [35, 112, 34, 115],  # 郑州地区
    "out_dir": "./era5_single"
}

downloader = ERA5Downloader(config)
downloader.download()
```

### 示例 2: 下载气压层数据

```python
config = {
    "dataset": "reanalysis-era5-pressure-levels",
    "variables": ["temperature", "specific_humidity"],
    "pressure_levels": ["850", "500", "250"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "out_dir": "./era5_pressure"
}

downloader = ERA5Downloader(config)
downloader.download()
```

### 示例 3: 结合 GeoJSON 边界

```python
from Utils.geojson_bounds import get_geojson_bounds_tuple

# 从 GeoJSON 获取边界
bbox = get_geojson_bounds_tuple('boundary/zhengzhou.geojson')
area = [bbox[3], bbox[0], bbox[1], bbox[2]]  # 转换为 [N, W, S, E]

config = {
    "dataset": "reanalysis-era5-single-levels",
    "variables": ["2m_temperature"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "area": area,
    "out_dir": "./era5_zhengzhou"
}

downloader = ERA5Downloader(config)
downloader.download()
```

### 示例 4: 高时间分辨率下载

```python
config = {
    "dataset": "reanalysis-era5-single-levels",
    "variables": ["10m_u_component_of_wind", "10m_v_component_of_wind"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-03",
    "hours": [f"{h:02d}" for h in range(24)],  # 每小时
    "chunking": "daily",
    "out_dir": "./era5_hourly"
}

downloader = ERA5Downloader(config)
downloader.download()
```

## 输出目录结构

```
era5_data/
├── 2020/
│   ├── 07/
│   │   ├── reanalysis-era5-single-levels_2m_temperature_202007.nc
│   │   └── reanalysis-era5-single-levels_total_precipitation_202007.nc
│   └── 08/
│       └── ...
└── ...
```

## 错误处理

下载器会自动处理以下错误:

**瞬态错误（会重试）:**
- 网络超时
- 服务器暂时不可用
- 连接中断

**致命错误（不会重试）:**
- 无效的变量名
- 无效的数据集
- 认证失败
- 权限不足

## 日志示例

```
2025-10-04 10:00:00 [INFO] ERA5Downloader 初始化完成: reanalysis-era5-single-levels
2025-10-04 10:00:00 [INFO]   变量: ['2m_temperature', 'total_precipitation']
2025-10-04 10:00:00 [INFO]   时间范围: 2020-07-01 到 2020-07-31
2025-10-04 10:00:01 [INFO] ✓ 配置验证通过
2025-10-04 10:00:01 [INFO] 生成了 1 个时间分块
2025-10-04 10:00:01 [INFO] 任务进度: 1/1
2025-10-04 10:00:01 [INFO] 开始下载 2m_temperature_total_precipitation / 2020-07 (尝试 1/5)
2025-10-04 10:05:23 [INFO] 文件大小: 45.32 MB
2025-10-04 10:05:23 [INFO] ✓ 下载完成: ./era5_data/2020/07/ERA5_xxx_202007.nc
2025-10-04 10:05:23 [INFO] ============================================================
2025-10-04 10:05:23 [INFO] 下载任务完成
2025-10-04 10:05:23 [INFO]   总任务数: 1
2025-10-04 10:05:23 [INFO]   成功下载: 1
2025-10-04 10:05:23 [INFO]   跳过（已存在）: 0
2025-10-04 10:05:23 [INFO]   失败: 0
```

## 常见变量

### 单层数据常用变量

- `2m_temperature` - 2米气温
- `total_precipitation` - 总降水量
- `10m_u_component_of_wind` - 10米U风分量
- `10m_v_component_of_wind` - 10米V风分量
- `surface_pressure` - 地面气压
- `mean_sea_level_pressure` - 海平面气压
- `total_cloud_cover` - 总云量

### 气压层数据常用变量

- `temperature` - 温度
- `specific_humidity` - 比湿
- `u_component_of_wind` - U风分量
- `v_component_of_wind` - V风分量
- `geopotential` - 位势高度

### 常用气压层

- `1000`, `925`, `850`, `700`, `500`, `300`, `250`, `200`, `100` hPa

## 注意事项

1. **API 限制**: CDS API 对请求大小和频率有限制，建议合理设置分块策略
2. **存储空间**: ERA5 数据文件较大，确保有足够的磁盘空间
3. **下载时间**: 下载时间取决于请求大小和服务器负载，大请求可能需要数小时
4. **认证信息**: 保护好你的 API 密钥，不要提交到版本控制系统

## 许可证

本代码基于伪代码实现，遵循项目整体许可证。

## 参考资源

- [CDS API 文档](https://cds.climate.copernicus.eu/api-how-to)
- [ERA5 数据集文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [变量列表](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation)
