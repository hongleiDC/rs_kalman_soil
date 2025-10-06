"""
数据预处理模块
整合 CYGNSS、ERA5-Land、MODIS NDVI 和 GPM IMERG 数据的预处理流程

基于 GEE 数据集文档：
- NASA/GPM_L3/IMERG_V07: 降水数据
- ECMWF/ERA5_LAND/DAILY_AGGR: 土壤湿度、气象数据
- MODIS/061/MOD13Q1: 植被指数
"""

from __future__ import annotations

import os
import glob
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import netCDF4 as nc

try:
    import ee
    import geemap
except ImportError as exc:
    raise ImportError(
        "ee and geemap are required. Install via 'pip install earthengine-api geemap'."
    ) from exc

from shapely.geometry import Point, shape

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    多源遥感数据预处理器
    
    功能：
    1. 读取本地 CYGNSS L1 v3.2 数据
    2. 从 GEE 获取并处理 ERA5-Land 数据（土壤湿度、气温、降水、蒸散发）
    3. 从 GEE 获取并处理 MODIS NDVI 数据
    4. 从 GEE 获取并处理 GPM IMERG 降水数据
    5. 数据质量检查和网格化
    """
    
    # GEE 数据集 ID（基于文档推荐版本）
    IMERG_DATASET = "NASA/GPM_L3/IMERG_V07"
    ERA5_DATASET = "ECMWF/ERA5_LAND/DAILY_AGGR"
    MODIS_DATASET = "MODIS/061/MOD13Q1"
    
    def __init__(
        self,
        aoi_geojson_path: str | Path,
        local_cygnss_dir: str | Path,
        start_date: str,
        end_date: str,
        output_dir: str | Path = "./preprocessed_data",
        gee_project_id: str = "solid-terra-465503-p1"
    ):
        """
        初始化数据预处理器
        
        Parameters
        ----------
        aoi_geojson_path : str | Path
            研究区域 GeoJSON 文件路径
        local_cygnss_dir : str | Path
            本地 CYGNSS 数据目录
        start_date : str
            起始日期，格式：'YYYY-MM-DD'
        end_date : str
            结束日期，格式：'YYYY-MM-DD'
        output_dir : str | Path
            输出目录
        gee_project_id : str
            Google Earth Engine 项目 ID
        """
        self.aoi_geojson_path = Path(aoi_geojson_path)
        self.local_cygnss_dir = Path(local_cygnss_dir)
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = Path(output_dir)
        self.gee_project_id = gee_project_id
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据存储
        self.roi_polygon = None
        self.roi_ee = None
        self.cygnss_data = None
        self.era5_data = None
        self.modis_data = None
        self.imerg_data = None
        
        # 日期范围
        self.dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        logger.info(f"DataPreprocessor 初始化完成")
        logger.info(f"  - 研究区域: {aoi_geojson_path}")
        logger.info(f"  - 时间范围: {start_date} 至 {end_date}")
        logger.info(f"  - 输出目录: {output_dir}")
    
    def initialize_gee(self):
        """初始化 Google Earth Engine"""
        try:
            ee.Initialize(project=self.gee_project_id)
            logger.info(f"✅ GEE 初始化成功 (项目: {self.gee_project_id})")
        except Exception as e:
            logger.warning(f"⚠️ GEE 初始化失败，尝试认证...")
            ee.Authenticate()
            ee.Initialize(project=self.gee_project_id)
            logger.info(f"✅ GEE 认证并初始化成功")
    
    def load_aoi(self):
        """加载研究区域 (AOI)"""
        logger.info(f"正在加载 AOI: {self.aoi_geojson_path}")
        
        if not self.aoi_geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON 文件不存在: {self.aoi_geojson_path}")
        
        gdf = gpd.read_file(self.aoi_geojson_path)
        
        # 如果有多个几何体，合并
        if len(gdf) > 1:
            gdf = gdf.dissolve().reset_index(drop=True)
        
        geom = gdf.geometry.iloc[0]
        if geom.geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError("AOI 几何体必须是 Polygon 或 MultiPolygon")
        
        self.roi_polygon = shape(geom)
        self.roi_ee = geemap.geopandas_to_ee(gdf)
        
        bounds = self.roi_polygon.bounds
        logger.info(f"✅ AOI 加载成功")
        logger.info(f"   边界: 西经 {bounds[0]:.4f}, 南纬 {bounds[1]:.4f}, "
                   f"东经 {bounds[2]:.4f}, 北纬 {bounds[3]:.4f}")
    
    # ==================== CYGNSS 数据处理 ====================
    
    def read_cygnss_files(self) -> pd.DataFrame:
        """
        读取本地 CYGNSS L1 v3.2 文件并处理
        
        Returns
        -------
        pd.DataFrame
            包含时间、位置、反射率、入射角等信息的 DataFrame
        """
        logger.info("正在读取 CYGNSS 数据...")
        
        # 递归查找 .nc 文件
        nc_files = list(self.local_cygnss_dir.glob("**/*.nc"))
        
        if not nc_files:
            raise FileNotFoundError(f"在 {self.local_cygnss_dir} 中未找到 .nc 文件")
        
        logger.info(f"找到 {len(nc_files)} 个 CYGNSS 文件")
        
        dfs = []
        for nc_file in nc_files:
            try:
                df = self._read_single_cygnss_file(nc_file)
                if not df.empty:
                    dfs.append(df)
            except Exception as e:
                logger.warning(f"读取文件失败，跳过: {nc_file.name} - {e}")
        
        if not dfs:
            raise RuntimeError("未能从任何 CYGNSS 文件中提取数据")
        
        # 合并所有数据
        all_data = pd.concat(dfs, ignore_index=True)
        
        # 时间过滤
        all_data = all_data[
            (all_data['time'] >= self.start_date) & 
            (all_data['time'] <= self.end_date)
        ]
        
        # 空间过滤（AOI 内）
        all_data = self._filter_by_aoi(all_data)
        
        self.cygnss_data = all_data
        
        logger.info(f"✅ CYGNSS 数据读取完成")
        logger.info(f"   总观测点数: {len(all_data)}")
        logger.info(f"   时间范围: {all_data['time'].min()} 至 {all_data['time'].max()}")
        
        return all_data
    
    def _read_single_cygnss_file(self, file_path: Path) -> pd.DataFrame:
        """读取单个 CYGNSS NetCDF 文件"""
        with nc.Dataset(file_path, 'r') as ds:
            # 提取时间、位置、观测数据
            # 时间变量候选
            time_vars = ['ddm_timestamp_utc', 'sample_time', 'time']
            time_data = None
            for var in time_vars:
                if var in ds.variables:
                    time_data = ds.variables[var][:]
                    break
            
            if time_data is None:
                return pd.DataFrame()
            
            # 位置变量
            lat_vars = ['sp_lat', 'lat', 'latitude']
            lon_vars = ['sp_lon', 'lon', 'longitude']
            
            lat_data = None
            lon_data = None
            for var in lat_vars:
                if var in ds.variables:
                    lat_data = ds.variables[var][:]
                    break
            for var in lon_vars:
                if var in ds.variables:
                    lon_data = ds.variables[var][:]
                    break
            
            if lat_data is None or lon_data is None:
                return pd.DataFrame()
            
            # 反射率和入射角
            refl_vars = ['peak_reflectivity', 'brcs', 'ddm_snr']
            inc_vars = ['sp_inc_angle', 'incidence_angle']
            
            refl_data = None
            inc_data = None
            for var in refl_vars:
                if var in ds.variables:
                    refl_data = ds.variables[var][:]
                    break
            for var in inc_vars:
                if var in ds.variables:
                    inc_data = ds.variables[var][:]
                    break
            
            # 展平为一维
            n = min(len(time_data.flatten()), len(lat_data.flatten()), 
                   len(lon_data.flatten()))
            
            df = pd.DataFrame({
                'time': pd.to_datetime(time_data.flatten()[:n], unit='s', 
                                      origin='unix', errors='coerce'),
                'lat': lat_data.flatten()[:n],
                'lon': lon_data.flatten()[:n],
            })
            
            if refl_data is not None:
                df['reflectivity'] = refl_data.flatten()[:n]
            if inc_data is not None:
                df['incidence_angle'] = inc_data.flatten()[:n]
            
            # 移除无效数据
            df = df.dropna(subset=['time', 'lat', 'lon'])
            
            return df
    
    def _filter_by_aoi(self, df: pd.DataFrame) -> pd.DataFrame:
        """根据 AOI 过滤数据点"""
        if self.roi_polygon is None:
            return df
        
        minx, miny, maxx, maxy = self.roi_polygon.bounds
        
        # 粗过滤：边界框
        df = df[
            (df['lon'] >= minx) & (df['lon'] <= maxx) &
            (df['lat'] >= miny) & (df['lat'] <= maxy)
        ]
        
        if df.empty:
            return df
        
        # 精过滤：多边形内部
        mask = df.apply(
            lambda row: self.roi_polygon.contains(Point(row['lon'], row['lat'])),
            axis=1
        )
        
        return df[mask].copy()
    
    # ==================== ERA5-Land 数据处理 ====================
    
    def process_era5_data(self) -> pd.DataFrame:
        """
        从 GEE 获取并处理 ERA5-Land 数据
        
        提取变量：
        - volumetric_soil_water_layer_1: 0-7cm 土壤体积含水量 (m³/m³)
        - temperature_2m: 2米气温 (K -> °C)
        - total_precipitation_sum: 总降水 (m -> mm)
        - potential_evaporation_sum: 潜在蒸散发 (m -> mm, 需取反)
        
        Returns
        -------
        pd.DataFrame
            包含日期和各变量均值的 DataFrame
        """
        logger.info("正在从 GEE 获取 ERA5-Land 数据...")
        
        if self.roi_ee is None:
            raise RuntimeError("请先调用 load_aoi() 加载研究区域")
        
        # 加载 ERA5-Land 数据集
        era5 = ee.ImageCollection(self.ERA5_DATASET) \
            .filterDate(self.start_date, self.end_date) \
            .filterBounds(self.roi_ee.geometry())
        
        # 检查数据可用性
        count = era5.size().getInfo()
        logger.info(f"找到 {count} 张 ERA5-Land 影像")
        
        if count == 0:
            logger.warning("⚠️ 未找到 ERA5-Land 数据")
            return pd.DataFrame()
        
        # 选择关键变量
        selected_bands = [
            'volumetric_soil_water_layer_1',  # 表层土壤湿度
            'temperature_2m',                  # 2米气温
            'total_precipitation_sum',         # 总降水
            'potential_evaporation_sum'        # 潜在蒸散发
        ]
        
        era5_filtered = era5.select(selected_bands)
        
        # 提取时间序列
        def extract_era5_values(image):
            # 单位转换
            sm = image.select('volumetric_soil_water_layer_1')  # m³/m³ (无需转换)
            temp = image.select('temperature_2m').subtract(273.15)  # K -> °C
            precip = image.select('total_precipitation_sum').multiply(1000)  # m -> mm
            pet = image.select('potential_evaporation_sum').multiply(-1000)  # m -> mm (取反)
            
            # 计算区域统计
            combined = ee.Image.cat([sm, temp, precip, pet])
            stats = combined.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.roi_ee.geometry(),
                scale=11000,  # ~0.1° 分辨率
                maxPixels=1e9
            )
            
            return ee.Feature(None, {
                'date': image.date().format('YYYY-MM-dd'),
                'soil_moisture': stats.get('volumetric_soil_water_layer_1'),
                'temperature': stats.get('temperature_2m'),
                'precipitation': stats.get('total_precipitation_sum'),
                'pet': stats.get('potential_evaporation_sum')
            })
        
        # 提取数据
        time_series = era5_filtered.map(extract_era5_values).getInfo()
        
        # 转换为 DataFrame
        records = []
        for feature in time_series['features']:
            props = feature['properties']
            records.append({
                'date': pd.to_datetime(props['date']),
                'soil_moisture': props.get('soil_moisture'),
                'temperature': props.get('temperature'),
                'precipitation': props.get('precipitation'),
                'pet': props.get('pet')
            })
        
        df = pd.DataFrame(records)
        df = df.sort_values('date').reset_index(drop=True)
        
        self.era5_data = df
        
        logger.info(f"✅ ERA5-Land 数据处理完成")
        logger.info(f"   记录数: {len(df)}")
        logger.info(f"   变量: {df.columns.tolist()}")
        
        return df
    
    # ==================== MODIS NDVI 数据处理 ====================
    
    def process_modis_data(self) -> pd.DataFrame:
        """
        从 GEE 获取并处理 MODIS NDVI 数据
        
        使用数据集: MODIS/061/MOD13Q1
        时间分辨率: 16 天
        空间分辨率: 250m
        
        Returns
        -------
        pd.DataFrame
            包含日期和 NDVI 均值的 DataFrame
        """
        logger.info("正在从 GEE 获取 MODIS NDVI 数据...")
        
        if self.roi_ee is None:
            raise RuntimeError("请先调用 load_aoi() 加载研究区域")
        
        # 加载 MODIS 数据集
        modis = ee.ImageCollection(self.MODIS_DATASET) \
            .filterDate(self.start_date, self.end_date) \
            .filterBounds(self.roi_ee.geometry())
        
        count = modis.size().getInfo()
        logger.info(f"找到 {count} 张 MODIS 影像")
        
        if count == 0:
            logger.warning("⚠️ 未找到 MODIS 数据")
            return pd.DataFrame()
        
        # 处理 NDVI：缩放 + 质量过滤
        def process_modis_image(image):
            # NDVI 缩放：除以 10000
            ndvi = image.select('NDVI').multiply(0.0001)
            
            # 质量过滤：SummaryQA <= 1 (0=好, 1=一般)
            qa = image.select('SummaryQA')
            mask = qa.lte(1)
            
            ndvi_masked = ndvi.updateMask(mask)
            
            # 计算区域均值
            stats = ndvi_masked.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.roi_ee.geometry(),
                scale=250,  # 250m 分辨率
                maxPixels=1e9
            )
            
            return ee.Feature(None, {
                'date': image.date().format('YYYY-MM-dd'),
                'ndvi': stats.get('NDVI')
            })
        
        # 提取数据
        time_series = modis.map(process_modis_image).getInfo()
        
        # 转换为 DataFrame
        records = []
        for feature in time_series['features']:
            props = feature['properties']
            records.append({
                'date': pd.to_datetime(props['date']),
                'ndvi': props.get('ndvi')
            })
        
        df = pd.DataFrame(records)
        df = df.sort_values('date').reset_index(drop=True)
        
        self.modis_data = df
        
        logger.info(f"✅ MODIS NDVI 数据处理完成")
        logger.info(f"   记录数: {len(df)}")
        if not df.empty:
            logger.info(f"   NDVI 范围: {df['ndvi'].min():.3f} - {df['ndvi'].max():.3f}")
        
        return df
    
    # ==================== GPM IMERG 数据处理 ====================
    
    def process_imerg_data(self) -> pd.DataFrame:
        """
        从 GEE 获取并处理 GPM IMERG 降水数据
        
        使用数据集: NASA/GPM_L3/IMERG_V07
        时间分辨率: 30 分钟
        空间分辨率: 0.1° (~11 km)
        
        返回日降水量 (mm/day)
        
        Returns
        -------
        pd.DataFrame
            包含日期和日降水量的 DataFrame
        """
        logger.info("正在从 GEE 获取 GPM IMERG 数据...")
        
        if self.roi_ee is None:
            raise RuntimeError("请先调用 load_aoi() 加载研究区域")
        
        # 加载 IMERG 数据集
        imerg = ee.ImageCollection(self.IMERG_DATASET) \
            .filterDate(self.start_date, self.end_date) \
            .filterBounds(self.roi_ee.geometry()) \
            .select('precipitation')  # mm/hr
        
        count = imerg.size().getInfo()
        logger.info(f"找到 {count} 张 IMERG 影像 (30分钟分辨率)")
        
        if count == 0:
            logger.warning("⚠️ 未找到 IMERG 数据")
            return pd.DataFrame()
        
        # 聚合到日尺度
        def daily_precipitation(date):
            d = ee.Date(date)
            daily = imerg.filterDate(d, d.advance(1, 'day')) \
                         .sum() \
                         .multiply(0.5)  # mm/hr * 0.5 hr = mm/30min
            
            stats = daily.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.roi_ee.geometry(),
                scale=11000,
                maxPixels=1e9
            )
            
            return ee.Feature(None, {
                'date': d.format('YYYY-MM-dd'),
                'precipitation': stats.get('precipitation')
            })
        
        # 生成日期序列
        dates = pd.date_range(self.start_date, self.end_date, freq='D')
        date_list = ee.List([ee.Date(str(d.date())) for d in dates])
        
        # 提取日降水量
        daily_precip = ee.FeatureCollection(date_list.map(daily_precipitation)).getInfo()
        
        # 转换为 DataFrame
        records = []
        for feature in daily_precip['features']:
            props = feature['properties']
            records.append({
                'date': pd.to_datetime(props['date']),
                'precipitation': props.get('precipitation')
            })
        
        df = pd.DataFrame(records)
        df = df.sort_values('date').reset_index(drop=True)
        
        self.imerg_data = df
        
        logger.info(f"✅ IMERG 降水数据处理完成")
        logger.info(f"   记录数: {len(df)}")
        if not df.empty:
            logger.info(f"   降水范围: {df['precipitation'].min():.2f} - "
                       f"{df['precipitation'].max():.2f} mm/day")
        
        return df
    
    # ==================== 数据质量检查 ====================
    
    def check_data_quality(self) -> Dict[str, Any]:
        """
        检查所有数据的质量
        
        Returns
        -------
        Dict[str, Any]
            质量检查报告
        """
        logger.info("正在进行数据质量检查...")
        
        report = {
            'cygnss': self._check_cygnss_quality(),
            'era5': self._check_era5_quality(),
            'modis': self._check_modis_quality(),
            'imerg': self._check_imerg_quality()
        }
        
        logger.info("✅ 数据质量检查完成")
        return report
    
    def _check_cygnss_quality(self) -> Dict[str, Any]:
        """检查 CYGNSS 数据质量"""
        if self.cygnss_data is None or self.cygnss_data.empty:
            return {'status': 'no_data'}
        
        df = self.cygnss_data
        
        quality = {
            'status': 'ok',
            'total_points': len(df),
            'date_range': (df['time'].min(), df['time'].max()),
            'missing_values': df.isnull().sum().to_dict(),
            'spatial_coverage': {
                'lat_range': (df['lat'].min(), df['lat'].max()),
                'lon_range': (df['lon'].min(), df['lon'].max())
            }
        }
        
        if 'reflectivity' in df.columns:
            quality['reflectivity_stats'] = {
                'mean': df['reflectivity'].mean(),
                'std': df['reflectivity'].std(),
                'min': df['reflectivity'].min(),
                'max': df['reflectivity'].max()
            }
        
        return quality
    
    def _check_era5_quality(self) -> Dict[str, Any]:
        """检查 ERA5 数据质量"""
        if self.era5_data is None or self.era5_data.empty:
            return {'status': 'no_data'}
        
        df = self.era5_data
        
        return {
            'status': 'ok',
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'missing_values': df.isnull().sum().to_dict(),
            'variables': {
                'soil_moisture': {
                    'mean': df['soil_moisture'].mean() if 'soil_moisture' in df else None,
                    'range': (df['soil_moisture'].min(), df['soil_moisture'].max()) if 'soil_moisture' in df else None
                },
                'temperature': {
                    'mean': df['temperature'].mean() if 'temperature' in df else None,
                    'range': (df['temperature'].min(), df['temperature'].max()) if 'temperature' in df else None
                }
            }
        }
    
    def _check_modis_quality(self) -> Dict[str, Any]:
        """检查 MODIS 数据质量"""
        if self.modis_data is None or self.modis_data.empty:
            return {'status': 'no_data'}
        
        df = self.modis_data
        
        return {
            'status': 'ok',
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'missing_values': df.isnull().sum().to_dict(),
            'ndvi_stats': {
                'mean': df['ndvi'].mean(),
                'std': df['ndvi'].std(),
                'range': (df['ndvi'].min(), df['ndvi'].max())
            }
        }
    
    def _check_imerg_quality(self) -> Dict[str, Any]:
        """检查 IMERG 数据质量"""
        if self.imerg_data is None or self.imerg_data.empty:
            return {'status': 'no_data'}
        
        df = self.imerg_data
        
        return {
            'status': 'ok',
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'missing_values': df.isnull().sum().to_dict(),
            'precipitation_stats': {
                'total': df['precipitation'].sum(),
                'mean_daily': df['precipitation'].mean(),
                'max_daily': df['precipitation'].max()
            }
        }
    
    # ==================== 数据网格化 ====================
    
    def grid_data(
        self,
        grid_resolution: float = 0.1,
        method: str = 'mean'
    ) -> xr.Dataset:
        """
        对数据进行网格化处理
        
        Parameters
        ----------
        grid_resolution : float
            网格分辨率（度），默认 0.1°
        method : str
            聚合方法：'mean', 'median', 'sum'
        
        Returns
        -------
        xr.Dataset
            网格化后的数据集
        """
        logger.info(f"正在进行数据网格化 (分辨率: {grid_resolution}°)...")
        
        if self.cygnss_data is None or self.cygnss_data.empty:
            raise RuntimeError("CYGNSS 数据为空，无法网格化")
        
        # 创建网格
        minx, miny, maxx, maxy = self.roi_polygon.bounds
        
        lon_bins = np.arange(minx, maxx + grid_resolution, grid_resolution)
        lat_bins = np.arange(miny, maxy + grid_resolution, grid_resolution)
        
        # 网格中心点
        lon_centers = (lon_bins[:-1] + lon_bins[1:]) / 2
        lat_centers = (lat_bins[:-1] + lat_bins[1:]) / 2
        
        # 对 CYGNSS 数据进行网格化
        df = self.cygnss_data.copy()
        df['lon_bin'] = pd.cut(df['lon'], bins=lon_bins, labels=lon_centers)
        df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_centers)
        
        # 按网格和日期聚合
        df['date'] = df['time'].dt.floor('D')
        
        if method == 'mean':
            gridded = df.groupby(['date', 'lat_bin', 'lon_bin']).mean()
        elif method == 'median':
            gridded = df.groupby(['date', 'lat_bin', 'lon_bin']).median()
        elif method == 'sum':
            gridded = df.groupby(['date', 'lat_bin', 'lon_bin']).sum()
        else:
            raise ValueError(f"未知的聚合方法: {method}")
        
        # 转换为 xarray Dataset
        gridded = gridded.reset_index()
        
        ds = xr.Dataset(
            {
                'reflectivity': (
                    ['time', 'lat', 'lon'],
                    gridded.pivot_table(
                        index='date',
                        columns=['lat_bin', 'lon_bin'],
                        values='reflectivity'
                    ).values.reshape(len(gridded['date'].unique()), 
                                    len(lat_centers), len(lon_centers))
                )
            },
            coords={
                'time': gridded['date'].unique(),
                'lat': lat_centers,
                'lon': lon_centers
            }
        )
        
        logger.info(f"✅ 数据网格化完成")
        logger.info(f"   网格尺寸: {len(lat_centers)} × {len(lon_centers)}")
        
        return ds
    
    # ==================== 数据导出 ====================
    
    def export_data(self):
        """导出所有处理后的数据"""
        logger.info("正在导出数据...")
        
        if self.cygnss_data is not None:
            output_path = self.output_dir / "cygnss_processed.csv"
            self.cygnss_data.to_csv(output_path, index=False)
            logger.info(f"✅ CYGNSS 数据已导出: {output_path}")
        
        if self.era5_data is not None:
            output_path = self.output_dir / "era5_processed.csv"
            self.era5_data.to_csv(output_path, index=False)
            logger.info(f"✅ ERA5 数据已导出: {output_path}")
        
        if self.modis_data is not None:
            output_path = self.output_dir / "modis_processed.csv"
            self.modis_data.to_csv(output_path, index=False)
            logger.info(f"✅ MODIS 数据已导出: {output_path}")
        
        if self.imerg_data is not None:
            output_path = self.output_dir / "imerg_processed.csv"
            self.imerg_data.to_csv(output_path, index=False)
            logger.info(f"✅ IMERG 数据已导出: {output_path}")
    
    # ==================== 完整流程 ====================
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        运行完整的数据预处理流程
        
        Returns
        -------
        Dict[str, Any]
            包含所有处理结果的字典
        """
        logger.info("=" * 60)
        logger.info("开始数据预处理流程")
        logger.info("=" * 60)
        
        # 1. 初始化 GEE
        self.initialize_gee()
        
        # 2. 加载 AOI
        self.load_aoi()
        
        # 3. 读取 CYGNSS 数据
        cygnss_df = self.read_cygnss_files()
        
        # 4. 处理 ERA5-Land 数据
        era5_df = self.process_era5_data()
        
        # 5. 处理 MODIS 数据
        modis_df = self.process_modis_data()
        
        # 6. 处理 IMERG 数据
        imerg_df = self.process_imerg_data()
        
        # 7. 数据质量检查
        quality_report = self.check_data_quality()
        
        # 8. 导出数据
        self.export_data()
        
        logger.info("=" * 60)
        logger.info("✅ 数据预处理流程完成！")
        logger.info("=" * 60)
        
        return {
            'cygnss': cygnss_df,
            'era5': era5_df,
            'modis': modis_df,
            'imerg': imerg_df,
            'quality_report': quality_report
        }


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例配置
    preprocessor = DataPreprocessor(
        aoi_geojson_path="../boundary/zhengzhou.geojson",
        local_cygnss_dir="/media/hl/Expansion/CYGNSS/CYGNSS_L1_V3.2/2021/7/",
        start_date="2021-07-01",
        end_date="2021-07-31",
        output_dir="./preprocessed_data"
    )
    
    # 运行完整流程
    results = preprocessor.run_full_pipeline()
    
    # 查看结果
    print("\n数据预处理结果:")
    print(f"  - CYGNSS 观测点数: {len(results['cygnss'])}")
    print(f"  - ERA5 记录数: {len(results['era5'])}")
    print(f"  - MODIS 记录数: {len(results['modis'])}")
    print(f"  - IMERG 记录数: {len(results['imerg'])}")
