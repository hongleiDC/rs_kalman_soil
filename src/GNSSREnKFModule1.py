# gnssr_module1.py
# -*- coding: utf-8 -*-
"""
模块一：主控制脚本（面向对象版本）
--------------------------------
功能概述：
1) 根据用户提供的 GeoJSON 读取 AOI；
2) 使用 GEE + geemap 探测可用的数据集（IMERG/ERA5-Land/MODIS NDVI）；
3) 从本地读取 CYGNSS 数据，自动判定每日是否存在观测；
4) 在主程序中配置 EnKF 初始参数与 Q/R；
5) 生成参数敏感性分析（LHS）样本集合；
6) 输出制品（availability_report.json, daily_run_plan.csv, enkf_config.json, lhs_params.csv）。

注意：
- 本模块“只做探测与计划”，不在此处做大量数据下载或同化运算；
- CYGNSS 采用本地读取（NetCDF/HDF 等），GEE 仅用于检查“是否能获取”；
- LHS 仅生成参数组合表，具体批量同化请在模块二中实现。

依赖：
    pip install geemap earthengine-api geopandas shapely xarray scipy pandas numpy

作者：你
"""

from __future__ import annotations
import os
import json
import warnings
from typing import List, Dict, Any, Optional, Tuple

warnings.filterwarnings("ignore")

# 基础科学与数据处理
import numpy as np
import pandas as pd

# 地理与GEE
import ee
import geemap
import geopandas as gpd
from shapely.geometry import shape, Point, Polygon, MultiPolygon

# 本地 CYGNSS（NetCDF/HDF）
try:
    import xarray as xr
except Exception as _e:
    xr = None

# LHS 采样
try:
    from scipy.stats.qmc import LatinHypercube
except Exception as _e:
    LatinHypercube = None


class GNSSREnKFModule1:
    """
    模块一主类：负责 AOI 加载、GEE可用性探测、本地CYGNSS覆盖统计、
    EnKF参数配置与LHS样本集生成，并导出制品与返回结果。
    """

    # ---- 常量：GEE候选数据集ID ----
    _CANDIDATES = {
        "imerg": ["NASA/GPM_L3/IMERG_V07", "NASA/GPM_L3/IMERG_V06"],
        "era5_land": ["ECMWF/ERA5_LAND/DAILY_AGGR", "ECMWF/ERA5_LAND/HOURLY"],
        "modis_ndvi": ["MODIS/061/MOD13Q1", "MODIS/006/MOD13Q1", "MODIS/061/MYD13Q1"]
    }

    def __init__(
        self,
        aoi_geojson_path: str,
        local_cygnss_files: List[str],
        start_date: str,
        end_date: str,
        output_dir: str = "./out_module1",
        min_hits_per_day: int = 10,
        lhs_samples: int = 50,
        random_seed: int = 42
    ):
        self.aoi_geojson_path = aoi_geojson_path
        self.local_cygnss_files = local_cygnss_files
        self.start_date = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        self.end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")
        self.output_dir = output_dir
        self.min_hits_per_day = int(min_hits_per_day)
        self.lhs_samples = int(lhs_samples)
        self.random_seed = int(random_seed)

        os.makedirs(self.output_dir, exist_ok=True)

        # 运行中生成的对象
        self.roi_ee = None              # ee.FeatureCollection/ee.Geometry
        self.roi_polygon = None         # shapely Polygon/MultiPolygon
        self.dates = pd.date_range(self.start_date, self.end_date, freq="D", tz="UTC")

        self.availability: Dict[str, Dict[str, Any]] = {}
        self.cygnss_points_df: Optional[pd.DataFrame] = None
        self.coverage_series: Optional[pd.Series] = None
        self.daily_plan: Optional[pd.DataFrame] = None

        self.enkf_config: Dict[str, Any] = {}
        self.lhs_params: Optional[pd.DataFrame] = None

    # -------------- 对外主流程 --------------
    def run(self) -> Dict[str, Any]:
        """执行模块一完整流程，返回关键结果对象。"""
        self._init_gee()
        self._read_aoi()
        self._check_gee_availability()
        self._read_local_cygnss_and_coverage()
        self._build_daily_plan()
        self._build_enkf_config()
        self._build_lhs_samples()
        self.export_artifacts()
        return {
            "aoi_ee": self.roi_ee,
            "aoi_polygon": self.roi_polygon,
            "availability": self.availability,
            "daily_plan": self.daily_plan,
            "enkf_config": self.enkf_config,
            "lhs_params": self.lhs_params,
            "cygnss_points": self.cygnss_points_df
        }

    def set_local_fallback(self, *, imerg: Optional[bool] = None, era5: Optional[bool] = None, ndvi: Optional[bool] = None):
        """
        设置本地数据回退标志，并更新 ready_for_assim。
        调用时需保证 self.daily_plan 已构建。
        """
        if self.daily_plan is None:
            raise RuntimeError("daily_plan 尚未生成，请先调用 run() 或 _build_daily_plan().")

        if imerg is not None:
            self.daily_plan["local_imerg"] = bool(imerg)
        if era5 is not None:
            self.daily_plan["local_era5"] = bool(era5)
        if ndvi is not None:
            self.daily_plan["local_ndvi"] = bool(ndvi)

        self._update_ready_flag()

    def export_artifacts(self):
        """导出制品：availability_report.json, daily_run_plan.csv, enkf_config.json, lhs_params.csv。"""
        with open(os.path.join(self.output_dir, "availability_report.json"), "w", encoding="utf-8") as f:
            json.dump(self.availability, f, ensure_ascii=False, indent=2)
        if self.daily_plan is not None:
            self.daily_plan.to_csv(os.path.join(self.output_dir, "daily_run_plan.csv"), index=False)
        with open(os.path.join(self.output_dir, "enkf_config.json"), "w", encoding="utf-8") as f:
            json.dump(self.enkf_config, f, ensure_ascii=False, indent=2)
        if self.lhs_params is not None:
            self.lhs_params.to_csv(os.path.join(self.output_dir, "lhs_params.csv"), index=False)

    # -------------- 内部步骤：GEE & AOI --------------
    def _init_gee(self):
        """初始化 Google Earth Engine。"""
        try:
            ee.Initialize(project="solid-terra-465503-p1")
        except Exception:
            ee.Authenticate()
            ee.Initialize(project="solid-terra-465503-p1")

    def _read_aoi(self):
        """读取 AOI GeoJSON -> (ee 对象, shapely polygon)。"""
        gdf = gpd.read_file(self.aoi_geojson_path)
        if len(gdf) > 1:
            gdf = gdf.dissolve().reset_index(drop=True)
        geom = gdf.geometry.iloc[0]
        if geom.geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError("AOI 几何必须为 Polygon/MultiPolygon。")
        self.roi_polygon = shape(geom)  # shapely
        self.roi_ee = geemap.geopandas_to_ee(gdf)  # ee FeatureCollection
        # print("AOI 读取完成。")

    def _gee_ic_available(self, ic_id: str) -> bool:
        """判断 GEE 中某 ImageCollection 是否存在。"""
        try:
            _ = ee.ImageCollection(ic_id).limit(1).size().getInfo()
            return True
        except Exception:
            return False

    def _gee_ic_has_data(self, ic_id: str) -> int:
        """统计该 IC 在 AOI + 时间范围内的影像数量。"""
        try:
            ic = ee.ImageCollection(ic_id).filterBounds(self.roi_ee.geometry()).filterDate(self.start_date, self.end_date)
            return int(ic.size().getInfo())
        except Exception:
            return 0

    def _choose_first_available_ic(self, candidates: List[str]) -> Dict[str, Any]:
        """从候选列表中选择第一个存在且在 AOI+时间内有数据的 IC。"""
        for ic_id in candidates:
            if self._gee_ic_available(ic_id):
                n = self._gee_ic_has_data(ic_id)
                if n > 0:
                    return {"dataset_id": ic_id, "has_data": True, "image_count": n}
        return {"dataset_id": None, "has_data": False, "image_count": 0}

    def _check_gee_availability(self):
        """探测 GEE 的 IMERG / ERA5-Land / MODIS NDVI 可用性。"""
        self.availability = {}
        for key, ids in self._CANDIDATES.items():
            self.availability[key] = self._choose_first_available_ic(ids)
            # print(f"[GEE] {key} -> {self.availability[key]}")

    # -------------- 内部步骤：本地 CYGNSS --------------
    def _guess_var_name(self, ds: "xr.Dataset", candidates: List[str]) -> Optional[str]:
        for name in candidates:
            if name in ds.variables or name in ds.coords:
                return name
        return None

    def _subset_dataset_bbox(self, ds: "xr.Dataset", latn: str, lonn: str) -> "xr.Dataset":
        """基于 AOI 外接矩形做快速裁剪（减少内存）。"""
        minx, miny, maxx, maxy = self.roi_polygon.bounds
        # 处理升序/降序坐标
        def _slice_dim(coord, vmin, vmax):
            arr = ds[coord]
            if arr[0] <= arr[-1]:
                return slice(vmin, vmax)
            else:
                return slice(vmax, vmin)

        return ds.sel({latn: _slice_dim(latn, miny, maxy), lonn: _slice_dim(lonn, minx, maxx)})

    def _read_local_cygnss_to_df(self) -> pd.DataFrame:
        """
        读取本地 CYGNSS（NetCDF/HDF）为 DataFrame: [time, lat, lon]。
        """
        if xr is None:
            raise RuntimeError("xarray 未安装，无法读取本地 CYGNSS。请安装：pip install xarray netCDF4 h5netcdf")

        paths = self.local_cygnss_files if isinstance(self.local_cygnss_files, (list, tuple)) else [self.local_cygnss_files]
        ds = xr.open_mfdataset(paths, combine="by_coords", parallel=False)

        tname = self._guess_var_name(ds, ["time", "Time"])
        latn  = self._guess_var_name(ds, ["lat", "latitude", "ddm_sp_lat", "sp_lat", "specular_lat", "ddm_sp_latitude"])
        lonn  = self._guess_var_name(ds, ["lon", "longitude", "ddm_sp_lon", "sp_lon", "specular_lon", "ddm_sp_longitude"])
        if tname is None or latn is None or lonn is None:
            raise KeyError("CYGNSS 文件内未找到 time/lat/lon 变量，请检查变量名。")

        # 外接矩形裁剪
        ds = self._subset_dataset_bbox(ds, latn, lonn)

        # 转 DataFrame（注意：大数据集可能较慢，建议预先分块）
        df = ds[[latn, lonn]].to_dataframe().reset_index()

        # 标准化列名与时间
        if tname not in df.columns and tname in ds.coords:
            # 展开 coords 到列
            df[tname] = np.repeat(ds.coords[tname].values, len(df) // len(ds.coords[tname].values))
        df = df.rename(columns={tname: "time", latn: "lat", lonn: "lon"})
        df = df.dropna(subset=["time", "lat", "lon"])
        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
        df = df.dropna(subset=["time"])
        return df

    def _spatial_filter_df_by_aoi(self, df: pd.DataFrame) -> pd.DataFrame:
        """精筛：点在 AOI 多边形内。"""
        if df.empty:
            return df.copy()
        # 先 bbox 粗筛（已经做过），这里直接 polygon contains 精筛
        mask = df.apply(lambda r: self.roi_polygon.contains(Point(float(r["lon"]), float(r["lat"]))), axis=1)
        return df[mask].copy()

    def _daily_coverage(self, df: pd.DataFrame, threshold: int) -> pd.Series:
        """按日统计点数并与阈值比较，返回 bool 序列。"""
        if df.empty:
            return pd.Series(dtype=bool)
        counts = df.groupby(df["time"].dt.floor("D")).size()
        return (counts >= threshold)

    def _read_local_cygnss_and_coverage(self):
        """读取本地 CYGNSS 点，AOI 精筛，并生成覆盖 Series。"""
        self.cygnss_points_df = self._read_local_cygnss_to_df()
        self.cygnss_points_df = self._spatial_filter_df_by_aoi(self.cygnss_points_df)
        self.coverage_series = self._daily_coverage(self.cygnss_points_df, self.min_hits_per_day)

    # -------------- 内部步骤：计划表 + EnKF配置 + LHS --------------
    def _build_daily_plan(self):
        """构建每日运行计划表（标记 has_cygnss / gee_ok / local_fallback / ready）。"""
        plan = pd.DataFrame({"date": self.dates})
        plan["has_cygnss"] = plan["date"].dt.floor("D").map(lambda d: bool(self.coverage_series.get(d, False)))

        plan["gee_imerg_ok"] = bool(self.availability.get("imerg", {}).get("has_data", False))
        plan["gee_era5_ok"] = bool(self.availability.get("era5_land", {}).get("has_data", False))
        plan["gee_ndvi_ok"] = bool(self.availability.get("modis_ndvi", {}).get("has_data", False))

        plan["local_imerg"] = False
        plan["local_era5"] = False
        plan["local_ndvi"] = False

        self.daily_plan = plan
        self._update_ready_flag()

    def _update_ready_flag(self):
        """根据 gee/local 标志更新 ready_for_assim。"""
        p = self.daily_plan
        self.daily_plan["ready_for_assim"] = (
            p["has_cygnss"] &
            (p["gee_imerg_ok"] | p["local_imerg"]) &
            (p["gee_era5_ok"]  | p["local_era5"]) &
            (p["gee_ndvi_ok"]  | p["local_ndvi"])
        )

    def _build_enkf_config(self):
        """在主程序中配置 EnKF 参数（初始、Q/R、观测模型）。"""
        self.enkf_config = {
            "state_init_mean": [0.25, 1.00],   # [SM0, VWC0]
            "state_init_std":  [0.02, 0.40],   # 初值标准差
            "Q_std":           [0.015, 0.15],  # 过程噪声标准差
            "R_std":           [0.02],         # 观测（反射率）标准差
            "obs_params": {
                "inc_angle_deg": 40.0,
                "surf_rms_height_m": 0.01,
                "veg_b": 0.12,
                "soil_temp_K": 295.0
            },
            "ensemble_size": 50
        }

    def _build_lhs_samples(self):
        """构建 LHS 参数样本集合（仅生成，不执行同化）。"""
        if LatinHypercube is None:
            self.lhs_params = pd.DataFrame(columns=[
                "SM0", "VWC0", "Q_SM", "Q_VWC", "R_refl", "inc_angle", "rms_h", "veg_b"
            ])
            return

        np.random.seed(self.random_seed)
        param_ranges = {
            "SM0": (0.10, 0.35),
            "VWC0": (0.50, 3.00),
            "Q_SM": (0.005, 0.030),
            "Q_VWC": (0.050, 0.300),
            "R_refl": (0.010, 0.050),
            "inc_angle": (30.0, 55.0),
            "rms_h": (0.005, 0.030),
            "veg_b": (0.080, 0.200)
        }
        names = list(param_ranges.keys())
        bounds = np.array([param_ranges[n] for n in names], dtype=float)  # (k, 2)
        sampler = LatinHypercube(d=len(names), seed=self.random_seed)
        unit = sampler.random(n=self.lhs_samples)
        samples = bounds[:, 0] + unit * (bounds[:, 1] - bounds[:, 0])
        self.lhs_params = pd.DataFrame(samples, columns=names)
