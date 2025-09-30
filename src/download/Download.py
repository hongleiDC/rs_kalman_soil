"""Utilities for downloading Earthdata granules using earthaccess."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Sequence

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

		print("EarthdataDownloader 实例已创建。")

	def login(self) -> None:
		"""Authenticate against NASA Earthdata."""

		print("正在登录 Earthdata...")
		self.auth = earthaccess.login()
		print("登录成功！")

	def _load_roi(self) -> None:
		"""Load the region-of-interest polygon from the configured GeoJSON file."""

		print(f"正在从 {self.geojson_path} 加载地理范围...")
		if not self.geojson_path.exists():
			raise FileNotFoundError(f"错误: GeoJSON 文件 {self.geojson_path} 未找到！")

		geojson_gdf = gpd.read_file(self.geojson_path)
		if geojson_gdf.empty:
			raise ValueError(f"错误: GeoJSON 文件 {self.geojson_path} 不包含任何几何信息！")

		self.roi_polygon = geojson_gdf.geometry.iloc[0]
		print("地理范围加载成功。")

	def search_data(self, start_time: str, end_time: str) -> Sequence[Any]:
		"""Search for granules matching the configured dataset and ROI."""

		if self.auth is None:
			raise RuntimeError("请先调用 login() 完成身份验证再搜索数据。")

		if self.roi_polygon is None:
			raise RuntimeError("请先加载地理范围 (调用 run() 或 _load_roi())。")

		print(f"正在搜索数据集 '{self.dataset_short_name}'...")
		geo_interface = getattr(self.roi_polygon, "__geo_interface__", None)
		if geo_interface is None:
			raise TypeError("ROI 几何对象不支持 __geo_interface__，无法传递给 earthaccess。")

		self.search_results = earthaccess.search_data(
			short_name=self.dataset_short_name,
			polygon=geo_interface,
			temporal=(start_time, end_time),
		)
		print(f"搜索完成，共找到 {len(self.search_results)} 条数据。")
		return self.search_results

	def download_data(self) -> List[Path]:
		"""Download previously searched granules to the configured local directory."""

		if not self.search_results:
			print("没有找到可供下载的数据。")
			return []

		print(
			f"准备下载 {len(self.search_results)} 个文件至 {self.local_download_dir}..."
		)
		self.local_download_dir.mkdir(parents=True, exist_ok=True)

		downloaded_files = earthaccess.download(
			granules=self.search_results,
			local_path=str(self.local_download_dir),
		)

		print("所有文件下载完成！")
		return [Path(path) for path in downloaded_files]

	def run(self, start_time: str, end_time: str) -> List[Path]:
		"""Execute the full login → ROI load → search → download workflow."""

		self.login()
		self._load_roi()
		self.search_data(start_time, end_time)
		return self.download_data()


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
