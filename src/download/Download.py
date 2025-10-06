"""Utilities for downloading Earthdata granules using earthaccess."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple
import logging

try:
	import earthaccess  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - library must be installed by user
	raise ImportError(
		"earthaccess is required to use EarthdataDownloader. Install it via 'pip install earthaccess'."
	) from exc

try:
	import geopandas as gpd  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - library must be installed by user
	raise ImportError(
		"geopandas is required to use EarthdataDownloader. Install it via 'pip install geopandas'."
	) from exc

try:
	from shapely.geometry import MultiPolygon, Polygon, box
	from shapely.geometry.base import BaseGeometry
	from shapely.ops import transform
except ImportError as exc:  # pragma: no cover - library must be installed by user
	raise ImportError(
		"shapely is required to process GeoJSON geometries. Install it via 'pip install shapely'."
	) from exc

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EarthdataDownloader:
	"""Encapsulates authentication, search, and download flows for NASA Earthdata."""

	def __init__(self, dataset_short_name: str, geojson_path: str | Path, local_download_dir: str | Path) -> None:
		"""Prepare the downloader with dataset metadata and persistence paths."""

		self.dataset_short_name = dataset_short_name
		self.geojson_path = Path(geojson_path)
		self.local_download_dir = Path(local_download_dir)

		self.auth: Optional[Any] = None
		self.roi_polygon: Optional[Any] = None
		self.search_results: Sequence[Any] = []
		self.roi_bounds: Optional[Tuple[float, float, float, float]] = None

		logger.info("EarthdataDownloader 实例已创建。")

	def login(self) -> None:
		"""Authenticate against NASA Earthdata."""

		logger.info("正在登录 Earthdata...")
		try:
			self.auth = earthaccess.login(strategy="netrc")
			logger.info("登录成功！")
		except Exception as e:
			logger.error(f"登录失败: {e}")
			raise

	def _load_roi(self) -> None:
		"""Load the region-of-interest from GeoJSON file and extract boundary coordinates."""

		logger.info(f"正在从 {self.geojson_path} 加载地理范围...")
		if not self.geojson_path.exists():
			raise FileNotFoundError(f"错误: GeoJSON 文件 {self.geojson_path} 未找到！")

		try:
			geojson_gdf = gpd.read_file(self.geojson_path)
			if geojson_gdf.empty:
				raise ValueError(f"错误: GeoJSON 文件 {self.geojson_path} 不包含任何几何信息！")

			self.roi_polygon = geojson_gdf.geometry.iloc[0]
			
			# 直接从几何体获取边界框坐标
			bounds = self.roi_polygon.bounds
			self.roi_bounds = bounds  # (minx, miny, maxx, maxy)
			
			minx, miny, maxx, maxy = bounds
			logger.info(f"地理范围加载成功。")
			logger.info(f"边界坐标: 西经 {minx:.6f}, 南纬 {miny:.6f}, 东经 {maxx:.6f}, 北纬 {maxy:.6f}")
			
		except Exception as e:
			logger.error(f"加载地理范围时出错: {e}")
			raise

	def search_data(self, start_time: str, end_time: str) -> Sequence[Any]:
		"""Search for granules matching the configured dataset and ROI using bounding box."""

		if self.auth is None:
			raise RuntimeError("请先调用 login() 完成身份验证再搜索数据。")

		if self.roi_bounds is None:
			raise RuntimeError("请先加载地理范围 (调用 run() 或 _load_roi())。")

		logger.info(f"正在搜索数据集 '{self.dataset_short_name}'...")
		
		# 使用边界框搜索
		minx, miny, maxx, maxy = self.roi_bounds
		logger.info(f"使用边界框搜索: ({minx:.6f}, {miny:.6f}, {maxx:.6f}, {maxy:.6f})")
		
		self.search_results = earthaccess.search_data(
			short_name=self.dataset_short_name,
			bounding_box=(minx, miny, maxx, maxy),
			temporal=(start_time, end_time),
		)
		
		logger.info(f"搜索完成，共找到 {len(self.search_results)} 条数据。")
		return self.search_results

	def download_data(self) -> List[Path]:
		"""Download previously searched granules to the configured local directory."""

		if not self.search_results:
			logger.info("没有找到可供下载的数据。")
			return []

		logger.info(f"准备下载 {len(self.search_results)} 个文件至 {self.local_download_dir}...")
		
		try:
			self.local_download_dir.mkdir(parents=True, exist_ok=True)

			downloaded_files = earthaccess.download(
				granules=self.search_results,
				local_path=str(self.local_download_dir),
			)

			logger.info("所有文件下载完成！")
			return [Path(path) for path in downloaded_files if path]
			
		except Exception as e:
			logger.error(f"下载过程中出错: {e}")
			raise

	def run(self, start_time: str, end_time: str) -> List[Path]:
		"""Execute the full login → ROI load → search → download workflow."""

		try:
			self.login()
			self._load_roi()
			self.search_data(start_time, end_time)
			return self.download_data()
		except Exception as e:
			logger.error(f"运行下载流程时出错: {e}")
			raise


def download_earthdata(
	dataset_short_name: str,
	geojson_path: str | Path,
	local_download_dir: str | Path,
	start_time: str,
	end_time: str,
) -> List[Path]:
	"""Convenience helper mirroring the class-based workflow."""

	downloader = EarthdataDownloader(dataset_short_name, geojson_path, local_download_dir)
	return downloader.run(start_time, end_time)


__all__ = ["EarthdataDownloader", "download_earthdata"]
