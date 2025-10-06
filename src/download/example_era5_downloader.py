"""
ERA5 下载器使用示例

展示如何使用 ERA5Downloader 类下载不同类型的 ERA5 数据。
"""

import sys
sys.path.append('..')

from download.ERA5Downloader import ERA5Downloader, download_era5

# ============================================
# 示例 1: 下载单层数据（2米温度和降水）
# ============================================
print("=" * 70)
print("示例 1: 下载 ERA5 单层数据 - 2米温度和总降水量")
print("=" * 70)

config_single_level = {
    "backend": "cds",
    "dataset": "reanalysis-era5-single-levels",
    "variables": [
        "2m_temperature",
        "total_precipitation"
    ],
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "hours": ["00", "06", "12", "18"],
    "area": [35, 112, 34, 115],  # [N, W, S, E] - 郑州地区
    "grid": "0.25/0.25",
    "product_type": "reanalysis",
    "format": "netcdf",
    "chunking": "monthly",
    "out_dir": "./era5_data/single_level",
    "file_naming": "{dataset}_{tag}_{YYYY}{MM}.{fmt}",
    "max_retries": 3,
    "retry_backoff_sec": 10,
    "timeout_minutes": 120
}

print("\n配置:")
print(f"  数据集: {config_single_level['dataset']}")
print(f"  变量: {config_single_level['variables']}")
print(f"  时间: {config_single_level['start_date']} 到 {config_single_level['end_date']}")
print(f"  区域: {config_single_level['area']}")
print(f"  输出: {config_single_level['out_dir']}")

# 取消注释以执行下载
# downloader1 = ERA5Downloader(config_single_level)
# downloader1.download()

print("\n提示: 取消注释代码以执行实际下载")


# ============================================
# 示例 2: 下载气压层数据（温度和比湿）
# ============================================
print("\n" + "=" * 70)
print("示例 2: 下载 ERA5 气压层数据 - 温度和比湿")
print("=" * 70)

config_pressure_levels = {
    "backend": "cds",
    "dataset": "reanalysis-era5-pressure-levels",
    "variables": [
        "temperature",
        "specific_humidity"
    ],
    "pressure_levels": ["850", "500", "250"],  # hPa
    "start_date": "2020-07-01",
    "end_date": "2020-07-07",
    "hours": ["00", "12"],
    "area": [35, 112, 34, 115],
    "grid": "0.25/0.25",
    "product_type": "reanalysis",
    "format": "netcdf",
    "chunking": "daily",
    "out_dir": "./era5_data/pressure_levels",
    "file_naming": "{dataset}_{tag}_{YYYY}{MM}{DD}.{fmt}",
    "max_retries": 5
}

print("\n配置:")
print(f"  数据集: {config_pressure_levels['dataset']}")
print(f"  变量: {config_pressure_levels['variables']}")
print(f"  气压层: {config_pressure_levels['pressure_levels']} hPa")
print(f"  时间: {config_pressure_levels['start_date']} 到 {config_pressure_levels['end_date']}")
print(f"  分块: {config_pressure_levels['chunking']}")

# 取消注释以执行下载
# downloader2 = ERA5Downloader(config_pressure_levels)
# downloader2.download()

print("\n提示: 取消注释代码以执行实际下载")


# ============================================
# 示例 3: 使用便捷函数下载
# ============================================
print("\n" + "=" * 70)
print("示例 3: 使用便捷函数 download_era5()")
print("=" * 70)

config_simple = {
    "dataset": "reanalysis-era5-single-levels",
    "variables": ["2m_temperature"],
    "start_date": "2020-07-01",
    "end_date": "2020-07-03",
    "hours": ["00", "12"],
    "out_dir": "./era5_data/simple",
    "chunking": "daily"
}

print("\n使用便捷函数:")
print("```python")
print("from download.ERA5Downloader import download_era5")
print("")
print("download_era5(config)")
print("```")

# 取消注释以执行下载
# download_era5(config_simple)

print("\n提示: 取消注释代码以执行实际下载")


# ============================================
# 示例 4: 使用 GeoJSON 边界
# ============================================
print("\n" + "=" * 70)
print("示例 4: 结合 GeoJSON 边界文件")
print("=" * 70)

print("\n可以结合之前创建的 geojson_bounds 工具:")
print("```python")
print("import sys")
print("sys.path.append('..')")
print("")
print("from Utils.geojson_bounds import get_geojson_bounds_tuple")
print("from download.ERA5Downloader import ERA5Downloader")
print("")
print("# 获取郑州市边界")
print("bbox = get_geojson_bounds_tuple('../../boundary/zhengzhou.geojson')")
print("# bbox = (112.714796, 34.264049, 114.206024, 34.984173)")
print("")
print("# 转换为 ERA5 area 格式 [N, W, S, E]")
print("area = [bbox[3], bbox[0], bbox[1], bbox[2]]")
print("")
print("config = {")
print("    'dataset': 'reanalysis-era5-single-levels',")
print("    'variables': ['2m_temperature'],")
print("    'start_date': '2020-07-01',")
print("    'end_date': '2020-07-31',")
print("    'area': area,  # 使用从 GeoJSON 提取的边界")
print("    'out_dir': './era5_zhengzhou'")
print("}")
print("")
print("downloader = ERA5Downloader(config)")
print("downloader.download()")
print("```")


# ============================================
# 示例 5: 完整的配置示例（带所有选项）
# ============================================
print("\n" + "=" * 70)
print("示例 5: 完整配置示例（所有可选参数）")
print("=" * 70)

config_full = {
    # 核心配置
    "backend": "cds",                    # "cds" 或 "aws" (AWS尚未实现)
    "dataset": "reanalysis-era5-single-levels",
    "variables": [
        "2m_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation",
        "surface_pressure"
    ],
    
    # 时间配置
    "start_date": "2020-07-01",
    "end_date": "2020-07-31",
    "hours": ["00", "03", "06", "09", "12", "15", "18", "21"],  # 每3小时
    
    # 空间配置
    "area": [35, 112, 34, 115],          # [N, W, S, E]
    "grid": "0.25/0.25",                 # 0.25度分辨率
    
    # 产品配置
    "product_type": "reanalysis",
    "format": "netcdf",                  # "netcdf" 或 "grib"
    
    # 下载策略
    "chunking": "monthly",               # "monthly" 或 "daily"
    "out_dir": "./era5_full",
    "file_naming": "ERA5_{tag}_{YYYY}{MM}{DD}.{fmt}",
    
    # 重试和超时
    "max_retries": 5,
    "retry_backoff_sec": 10,
    "timeout_minutes": 120,
    
    # 高级选项
    "parallelism": 1,                    # 并发度（当前未实现并行）
    "credentials": None                  # 自定义认证（通常使用 ~/.cdsapirc）
}

print("\n完整配置字典:")
for key, value in config_full.items():
    print(f"  {key}: {value}")


# ============================================
# 使用说明
# ============================================
print("\n" + "=" * 70)
print("使用步骤")
print("=" * 70)

print("""
1. 安装依赖:
   pip install cdsapi

2. 配置 CDS API:
   创建文件 ~/.cdsapirc，内容如下:
   
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR-UID:YOUR-API-KEY
   
   在 https://cds.climate.copernicus.eu/api-how-to 获取你的 API 密钥

3. 运行下载:
   python example_era5_downloader.py
   
   或在你的代码中:
   
   from download.ERA5Downloader import ERA5Downloader
   
   config = {...}
   downloader = ERA5Downloader(config)
   downloader.download()

4. 监控进度:
   下载器会输出详细的日志信息，包括:
   - 任务进度
   - 下载速度
   - 文件大小
   - 错误和重试信息

5. 断点续传:
   如果下载中断，重新运行相同配置即可。
   已完成的文件会被自动跳过。
""")

print("=" * 70)
print("更多信息请参考 ERA5Downloader.py 的文档字符串")
print("=" * 70)
