"""
ERA5 数据下载器

支持从 CDS (Climate Data Store) 或 AWS 公共数据集下载 ERA5 再分析数据。
提供灵活的配置选项，包括变量选择、时间范围、空间范围、重试机制等。

作者: Auto-generated
日期: 2025-10-04
"""

from __future__ import annotations

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass

import cdsapi

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# 支持的数据集
SUPPORTED_DATASETS = [
    "reanalysis-era5-single-levels",
    "reanalysis-era5-pressure-levels",
    "reanalysis-era5-land"
]

# 气压层数据集
PRESSURE_LEVEL_DATASETS = [
    "reanalysis-era5-pressure-levels"
]

# 最小有效文件大小（字节）
MIN_VALID_SIZE = 1024  # 1KB


@dataclass
class DateChunk:
    """日期分块数据结构"""
    year: int
    month: int
    day_list: List[int]
    
    @property
    def start_date(self) -> datetime:
        return datetime(self.year, self.month, min(self.day_list))
    
    @property
    def end_date(self) -> datetime:
        return datetime(self.year, self.month, max(self.day_list))


class ERA5Downloader:
    """
    ERA5 数据下载器
    
    支持从 CDS 或 AWS 下载 ERA5 再分析数据，具有以下特性：
    - 灵活的时间和空间范围配置
    - 按月或按日分块下载
    - 自动重试机制
    - 断点续传支持
    - 多种变量和气压层支持
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 ERA5 下载器
        
        参数:
            config: 配置字典，包含以下键：
                - dataset: 数据集名称（必填）
                - variables: 变量列表（必填）
                - start_date: 开始日期 "YYYY-MM-DD"（必填）
                - end_date: 结束日期 "YYYY-MM-DD"（必填）
                - backend: "cds" 或 "aws"（默认 "cds"）
                - pressure_levels: 气压层列表（气压层数据集必填）
                - hours: 小时列表（默认 ["00","06","12","18"]）
                - area: 地理范围 [N, W, S, E]（可选）
                - grid: 格点分辨率 "0.25/0.25"（可选）
                - product_type: "reanalysis" 等（默认 "reanalysis"）
                - format: "netcdf" 或 "grib"（默认 "netcdf"）
                - chunking: "monthly" 或 "daily"（默认 "monthly"）
                - out_dir: 输出目录（默认 "./era5"）
                - file_naming: 文件命名模板（可选）
                - max_retries: 最大重试次数（默认 5）
                - retry_backoff_sec: 重试退避时间（默认 10）
                - timeout_minutes: 超时时间（默认 120）
                - parallelism: 并发度（默认 1）
                - credentials: 认证信息（可选）
        """
        # 核心配置
        self.backend = config.get("backend", "cds")
        self.dataset = config["dataset"]
        self.variables = config["variables"]
        self.pressure_levels = config.get("pressure_levels", [])
        
        # 时间范围
        self.start_date = config["start_date"]
        self.end_date = config["end_date"]
        self.hours = config.get("hours", ["00", "06", "12", "18"])
        
        # 空间范围
        self.area = config.get("area", None)  # [N, W, S, E]
        self.grid = config.get("grid", None)  # "0.25/0.25"
        
        # 数据产品配置
        self.product_type = config.get("product_type", "reanalysis")
        self.format = config.get("format", "netcdf")
        
        # 下载策略
        self.chunking = config.get("chunking", "monthly")
        self.out_dir = Path(config.get("out_dir", "./era5"))
        self.file_naming = config.get(
            "file_naming",
            "{dataset}_{tag}_{YYYY}{MM}{DD}.{fmt}"
        )
        
        # 重试和超时配置
        self.max_retries = config.get("max_retries", 5)
        self.retry_backoff_sec = config.get("retry_backoff_sec", 10)
        self.timeout_minutes = config.get("timeout_minutes", 120)
        
        # 高级配置
        self.parallelism = config.get("parallelism", 1)
        self.credentials = config.get("credentials", None)
        
        # CDS 客户端（延迟初始化）
        self._cds_client = None
        
        logger.info(f"ERA5Downloader 初始化完成: {self.dataset}")
        logger.info(f"  变量: {self.variables}")
        logger.info(f"  时间范围: {self.start_date} 到 {self.end_date}")
        logger.info(f"  输出目录: {self.out_dir}")
    
    def get_geojson_bounds(self, geojson_path: Union[str, Path]) -> Dict[str, float]:
        """
        从GeoJSON文件中提取四边边界的经纬度。
        
        参数:
            geojson_path: GeoJSON文件的路径
            
        返回:
            包含边界信息的字典，键为:
            - 'min_lon': 最小经度（西边界）
            - 'min_lat': 最小纬度（南边界）
            - 'max_lon': 最大经度（东边界）
            - 'max_lat': 最大纬度（北边界）
            
        异常:
            FileNotFoundError: 当GeoJSON文件不存在时
            ValueError: 当GeoJSON文件为空或无效时
            
        示例:
            >>> bounds = get_geojson_bounds("zhengzhou.geojson")
            >>> print(f"经度范围: {bounds['min_lon']} 到 {bounds['max_lon']}")
            >>> print(f"纬度范围: {bounds['min_lat']} 到 {bounds['max_lat']}")
        """
        geojson_path = Path(geojson_path)
        
        # 检查文件是否存在
        if not geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON文件未找到: {geojson_path}")
        
        # 读取GeoJSON文件
        try:
            gdf = gpd.read_file(geojson_path)
        except Exception as e:
            raise ValueError(f"无法读取GeoJSON文件 {geojson_path}: {e}") from e
        
        # 检查是否为空
        if gdf.empty:
            raise ValueError(f"GeoJSON文件为空: {geojson_path}")
        
        # 获取所有几何体的总边界
        # bounds返回 (minx, miny, maxx, maxy)
        total_bounds = gdf.total_bounds
        
        return {
            'min_lon': float(total_bounds[0]),  # 西边界
            'min_lat': float(total_bounds[1]),  # 南边界
            'max_lon': float(total_bounds[2]),  # 东边界
            'max_lat': float(total_bounds[3])   # 北边界
        }     


    def download(self) -> None:

        dataset = "reanalysis-era5-land"
        request = {
            "variable": [
                "2m_dewpoint_temperature",
                "skin_temperature",
                "volumetric_soil_water_layer_1",
                "surface_solar_radiation_downwards",
                "surface_thermal_radiation_downwards",
                "evaporation_from_bare_soil",
                "evaporation_from_vegetation_transpiration",
                "potential_evaporation",
                "runoff",
                "sub_surface_runoff",
                "surface_runoff",
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "surface_pressure",
                "total_precipitation",
                "high_vegetation_cover",
                "low_vegetation_cover",
                "geopotential",
                "land_sea_mask",
                "soil_type"
            ],
            "year": "2021",
            "month": "07",
            "day": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12",
                "13", "14", "15",
                "16", "17", "18",
                "19", "20", "21",
                "22", "23", "24",
                "25", "26", "27",
                "28", "29", "30",
                "31"
            ],
            "time": [
                "00:00", "01:00", "02:00",
                "03:00", "04:00", "05:00",
                "06:00", "07:00", "08:00",
                "09:00", "10:00", "11:00",
                "12:00", "13:00", "14:00",
                "15:00", "16:00", "17:00",
                "18:00", "19:00", "20:00",
                "21:00", "22:00", "23:00"
            ],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [34.984173, 112.714796, 34.264049, 114.206024]
        }

        client = cdsapi.Client()
        client.retrieve(dataset, request).download()

        
        # 输出统计信息
        logger.info("=" * 60)
        logger.info("下载任务完成")
        logger.info(f"  总任务数: {total_tasks}")
        logger.info(f"  成功下载: {completed_tasks - skipped_tasks - failed_tasks}")
        logger.info(f"  跳过（已存在）: {skipped_tasks}")
        logger.info(f"  失败: {failed_tasks}")
        logger.info("=" * 60)
        
        if failed_tasks > 0:
            logger.warning(f"有 {failed_tasks} 个任务失败，请检查日志")
    
    def validate_config(self) -> None:
        """验证配置参数的有效性"""
        logger.info("验证配置...")
        
        # 检查数据集
        if self.dataset not in SUPPORTED_DATASETS:
            raise ValueError(
                f"不支持的数据集: {self.dataset}。"
                f"支持的数据集: {SUPPORTED_DATASETS}"
            )
        
        # 检查变量
        if not self.variables or len(self.variables) == 0:
            raise ValueError("必须至少指定一个变量")
        
        # 检查格式
        if self.format not in ["netcdf", "grib"]:
            raise ValueError(f"不支持的格式: {self.format}")
        
        # 检查分块方式
        if self.chunking not in ["monthly", "daily"]:
            raise ValueError(f"不支持的分块方式: {self.chunking}")
        
        # 检查日期范围
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            if start > end:
                raise ValueError("开始日期必须早于或等于结束日期")
        except ValueError as e:
            raise ValueError(f"日期格式错误: {e}")
        
        # 检查气压层数据集
        if self.dataset in PRESSURE_LEVEL_DATASETS:
            if not self.pressure_levels or len(self.pressure_levels) == 0:
                raise ValueError(f"气压层数据集 {self.dataset} 必须指定 pressure_levels")
        
        # 检查 CDS 认证
        if self.backend == "cds":
            self._check_cds_credentials()
        
        logger.info("✓ 配置验证通过")
    
    def _check_cds_credentials(self) -> None:
        """检查 CDS API 认证信息"""
        # 检查 .cdsapirc 文件或环境变量
        cdsapirc = Path.home() / ".cdsapirc"
        
        if not cdsapirc.exists():
            if "CDSAPI_URL" not in os.environ or "CDSAPI_KEY" not in os.environ:
                logger.warning(
                    "未找到 CDS API 认证信息。请创建 ~/.cdsapirc 文件或设置环境变量 "
                    "CDSAPI_URL 和 CDSAPI_KEY"
                )
        else:
            logger.info(f"✓ 找到 CDS 认证文件: {cdsapirc}")
    
    def _derive_tags(self) -> List[str]:
        """
        生成下载任务标签
        
        对于气压层数据集，按气压层拆分
        对于单层数据集，按变量拆分（或合并）
        """
        if self.dataset in PRESSURE_LEVEL_DATASETS:
            # 按气压层拆分
            return [f"pl{level}" for level in self.pressure_levels]
        else:
            # 单层数据：按变量拆分或全部合并
            # 这里选择合并所有变量到一个文件（可根据需要调整）
            return ["_".join(self.variables[:3])]  # 使用前3个变量名作为标签
    
    def _split_date_range(self) -> List[DateChunk]:
        """
        将日期范围分割成块
        
        返回:
            DateChunk 对象列表
        """
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        chunks = []
        
        if self.chunking == "monthly":
            # 按月分块
            current = start
            while current <= end:
                year = current.year
                month = current.month
                
                # 计算该月的日期列表
                month_start = max(current, start)
                
                # 下个月第一天
                if month == 12:
                    next_month = datetime(year + 1, 1, 1)
                else:
                    next_month = datetime(year, month + 1, 1)
                
                month_end = min(next_month - timedelta(days=1), end)
                
                # 生成该月的天数列表
                day_list = []
                day_current = month_start
                while day_current <= month_end:
                    day_list.append(day_current.day)
                    day_current += timedelta(days=1)
                
                chunks.append(DateChunk(year, month, day_list))
                
                # 移动到下个月
                current = next_month
        
        elif self.chunking == "daily":
            # 按日分块
            current = start
            while current <= end:
                chunks.append(DateChunk(current.year, current.month, [current.day]))
                current += timedelta(days=1)
        
        return chunks
    
    def _build_output_path(self, tag: str, chunk: DateChunk) -> Path:
        """
        构建输出文件路径
        
        参数:
            tag: 任务标签（变量或气压层）
            chunk: 日期分块
            
        返回:
            输出文件的完整路径
        """
        year = f"{chunk.year:04d}"
        month = f"{chunk.month:02d}"
        day = f"{min(chunk.day_list):02d}"
        
        fmt_ext = "nc" if self.format == "netcdf" else "grib"
        
        # 替换文件名模板中的占位符
        filename = self.file_naming
        filename = filename.replace("{dataset}", self.dataset)
        filename = filename.replace("{tag}", tag)
        filename = filename.replace("{YYYY}", year)
        filename = filename.replace("{MM}", month)
        filename = filename.replace("{DD}", day)
        filename = filename.replace("{fmt}", fmt_ext)
        
        # 构建分层目录结构: out_dir/YYYY/MM/filename
        output_path = self.out_dir / year / month / filename
        
        return output_path
    
    def _build_cds_payload(self, tag: str, chunk: DateChunk) -> Dict[str, Any]:
        """
        构建 CDS API 请求负载
        
        参数:
            tag: 任务标签
            chunk: 日期分块
            
        返回:
            CDS API 请求字典
        """
        payload = {
            "product_type": self.product_type,
            "format": self.format,
            "time": self.hours,
        }
        
        # 处理变量和气压层
        if self.dataset in PRESSURE_LEVEL_DATASETS:
            # 从标签中提取气压层
            level = tag.replace("pl", "")
            payload["variable"] = self.variables
            payload["pressure_level"] = [level]
        else:
            # 单层数据
            payload["variable"] = self.variables
        
        # 日期维度
        payload["year"] = [f"{chunk.year:04d}"]
        payload["month"] = [f"{chunk.month:02d}"]
        payload["day"] = [f"{d:02d}" for d in chunk.day_list]
        
        # 可选的空间范围
        if self.area is not None:
            payload["area"] = self.area  # [N, W, S, E]
        
        if self.grid is not None:
            payload["grid"] = self.grid  # "0.25/0.25"
        
        return payload
    
    def _cds_retrieve_and_download(
        self,
        payload: Dict[str, Any],
        tmp_path: Path
    ) -> None:
        """
        使用 CDS API 检索并下载数据
        
        参数:
            payload: CDS API 请求负载
            tmp_path: 临时文件路径
        """
        # 延迟导入 cdsapi
        try:
            import cdsapi
        except ImportError:
            raise ImportError(
                "需要安装 cdsapi 包。请运行: pip install cdsapi"
            )
        
        # 初始化客户端（仅一次）
        if self._cds_client is None:
            if self.credentials:
                self._cds_client = cdsapi.Client(
                    url=self.credentials.get("url"),
                    key=self.credentials.get("key")
                )
            else:
                self._cds_client = cdsapi.Client()
        
        # 确保临时文件目录存在
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 发起请求
        logger.info(f"CDS 请求: {self.dataset}")
        logger.debug(f"请求参数: {payload}")
        
        self._cds_client.retrieve(
            self.dataset,
            payload,
            str(tmp_path)
        )
        
        # 验证下载的文件
        if not tmp_path.exists() or tmp_path.stat().st_size < MIN_VALID_SIZE:
            raise RuntimeError(f"下载的文件无效或为空: {tmp_path}")
        
        logger.info(f"文件大小: {tmp_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    def _file_exists_and_complete(self, path: Path) -> bool:
        """检查文件是否存在且完整"""
        return path.exists() and path.stat().st_size > MIN_VALID_SIZE
    
    def _atomic_rename(self, tmp_path: Path, final_path: Path) -> None:
        """原子性地重命名文件"""
        final_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.rename(final_path)
    
    def _backoff_time(self, attempt: int) -> int:
        """计算指数退避时间"""
        return self.retry_backoff_sec * (2 ** (attempt - 1))
    
    def _is_fatal_error(self, error_msg: str) -> bool:
        """判断是否为致命错误（不应重试）"""
        fatal_keywords = [
            "invalid variable",
            "invalid dataset",
            "authentication failed",
            "permission denied",
            "not found",
        ]
        
        error_lower = error_msg.lower()
        return any(keyword in error_lower for keyword in fatal_keywords)


# 便捷函数
def download_era5(config: Dict[str, Any]) -> None:
    """
    便捷函数：创建下载器并执行下载
    
    参数:
        config: 配置字典
    """
    downloader = ERA5Downloader(config)
    downloader.download()


__all__ = ["ERA5Downloader", "download_era5"]
