# gnssr_module1.py
# -*- coding: utf-8 -*-
"""
模块一（面向对象版）— 主控制脚本
--------------------------------
功能：
1) 读取 AOI(GeoJSON) -> (ee.Geometry, shapely Polygon)
2) 探测 GEE 可用性（IMERG / ERA5-Land / MODIS NDVI）
3) 从“本地目录”递归读取 CYGNSS Level-1 v3.2（NetCDF/HDF），抽取：
   - time（UTC）
   - ddm_sp_lat / ddm_sp_lon（或同义字段）
   - incidence_angle（或同义字段）
   - 反射率：优先取 DDM NBRCS（峰值），dB→线性（如需）
4) 生成每日 CYGNSS 覆盖（是否达到阈值）与每日 ROI 平均观测（反射率/入射角）
5) 在主程序内配置 EnKF 初值、Q/R、观测模型参数
6) 生成 LHS 敏感性分析参数表
7) 导出制品：availability_report.json, daily_run_plan.csv, enkf_config.json, lhs_params.csv,
              cygnss_daily_obs.csv（ROI日均观测）

依赖：
    pip install geemap earthengine-api geopandas shapely
    pip install xarray netCDF4 h5netcdf
    pip install scipy pandas numpy
"""

from __future__ import annotations
import os
import re
import json
import glob
import warnings
from typing import List, Dict, Any, Optional, Tuple

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

# GEE / geospatial
import ee
import geemap
import geopandas as gpd
from shapely.geometry import shape, Point

# local CYGNSS
try:
    import xarray as xr
except Exception:
    xr = None

# LHS
try:
    from scipy.stats.qmc import LatinHypercube
except Exception:
    LatinHypercube = None


class GNSSREnKFModule1:
    """
    模块一主类：AOI加载、GEE可用性探测、本地CYGNSS(L1 v3.2)读取与覆盖统计、
                EnKF参数配置、LHS采样与制品导出。
    """

    _CANDIDATES = {
        "imerg": ["NASA/GPM_L3/IMERG_V07", "NASA/GPM_L3/IMERG_V06"],
        "era5_land": ["ECMWF/ERA5_LAND/DAILY_AGGR", "ECMWF/ERA5_LAND/HOURLY"],
        "modis_ndvi": ["MODIS/061/MOD13Q1", "MODIS/006/MOD13Q1", "MODIS/061/MYD13Q1"]
    }

    def __init__(
        self,
        aoi_geojson_path: str,
        local_cygnss_dir: str,                # <--- 本地目录
        start_date: str,
        end_date: str,
        output_dir: str = "./out_module1",
        min_hits_per_day: int = 10,
        lhs_samples: int = 50,
        random_seed: int = 42,
        cygnss_required_substrings: Tuple[str, ...] = ("L1", "3.2"),  # 只匹配包含这些关键字的文件
        cygnss_glob_pattern: str = "**/*.nc",   # 可改为 "**/*.nc4" 或 "**/*.h5" 等
    ):
        self.aoi_geojson_path = aoi_geojson_path
        self.local_cygnss_dir = local_cygnss_dir
        self.start_date = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        self.end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")
        self.output_dir = output_dir
        self.min_hits_per_day = int(min_hits_per_day)
        self.lhs_samples = int(lhs_samples)
        self.random_seed = int(random_seed)
        self.cygnss_required_substrings = tuple(cygnss_required_substrings)
        self.cygnss_glob_pattern = cygnss_glob_pattern

        os.makedirs(self.output_dir, exist_ok=True)

        # runtime fields
        self.roi_ee = None
        self.roi_polygon = None
        self.dates = pd.date_range(self.start_date, self.end_date, freq="D", tz="UTC")

        self.availability: Dict[str, Dict[str, Any]] = {}
        self.cygnss_points_df: Optional[pd.DataFrame] = None
        self.cygnss_daily_obs_df: Optional[pd.DataFrame] = None
        self.coverage_series: Optional[pd.Series] = None
        self.daily_plan: Optional[pd.DataFrame] = None
        self.enkf_config: Dict[str, Any] = {}
        self.lhs_params: Optional[pd.DataFrame] = None

    # ---------------------- 外部主流程 ----------------------
    def run(self) -> Dict[str, Any]:
        self._init_gee()
        self._read_aoi()
        self._check_gee_availability()
        self._read_local_cygnss_l1_v32()
        self._build_daily_plan()
        self._build_enkf_config()
        self._build_lhs_samples()
        self._export_artifacts()
        return {
            "aoi_ee": self.roi_ee,
            "aoi_polygon": self.roi_polygon,
            "availability": self.availability,
            "daily_plan": self.daily_plan,
            "enkf_config": self.enkf_config,
            "lhs_params": self.lhs_params,
            "cygnss_points": self.cygnss_points_df,
            "cygnss_daily_obs": self.cygnss_daily_obs_df
        }

    def set_local_fallback(self, *, imerg: Optional[bool] = None, era5: Optional[bool] = None, ndvi: Optional[bool] = None):
        """设置本地回退标志位，并更新 ready_for_assim。"""
        if self.daily_plan is None:
            raise RuntimeError("daily_plan 尚未生成。")
        if imerg is not None: self.daily_plan["local_imerg"] = bool(imerg)
        if era5 is not None:  self.daily_plan["local_era5"] = bool(era5)
        if ndvi is not None:  self.daily_plan["local_ndvi"] = bool(ndvi)
        self._update_ready_flag()

    # ---------------------- 内部：GEE & AOI ----------------------
    def _init_gee(self):
        """初始化 Google Earth Engine。"""
        try:
            ee.Initialize(project="solid-terra-465503-p1")
        except Exception:
            ee.Authenticate()
            ee.Initialize(project="solid-terra-465503-p1")

    def _read_aoi(self):
        gdf = gpd.read_file(self.aoi_geojson_path)
        if len(gdf) > 1:
            gdf = gdf.dissolve().reset_index(drop=True)
        geom = gdf.geometry.iloc[0]
        if geom.geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError("AOI 几何必须为 Polygon/MultiPolygon。")
        self.roi_polygon = shape(geom)
        self.roi_ee = geemap.geopandas_to_ee(gdf)

    def _gee_ic_available(self, ic_id: str) -> bool:
        try:
            _ = ee.ImageCollection(ic_id).limit(1).size().getInfo()
            return True
        except Exception:
            return False

    def _gee_ic_has_data(self, ic_id: str) -> int:
        try:
            ic = ee.ImageCollection(ic_id).filterBounds(self.roi_ee.geometry()).filterDate(self.start_date, self.end_date)
            return int(ic.size().getInfo())
        except Exception:
            return 0

    def _choose_first_available_ic(self, candidates: List[str]) -> Dict[str, Any]:
        for ic_id in candidates:
            if self._gee_ic_available(ic_id):
                n = self._gee_ic_has_data(ic_id)
                if n > 0:
                    return {"dataset_id": ic_id, "has_data": True, "image_count": n}
        return {"dataset_id": None, "has_data": False, "image_count": 0}

    def _check_gee_availability(self):
        self.availability.clear()
        for key, ids in self._CANDIDATES.items():
            self.availability[key] = self._choose_first_available_ic(ids)

    # ---------------------- 内部：本地 CYGNSS L1 v3.2 ----------------------
    def _discover_cygnss_files(self) -> List[str]:
        """在本地目录递归查找 CYGNSS L1 v3.2 文件（按关键字过滤）。"""
        pattern = os.path.join(self.local_cygnss_dir, self.cygnss_glob_pattern)
        files = glob.glob(pattern, recursive=True)
        # 仅保留包含必须子串的文件（如 "L1", "3.2"）
        def match_required(path: str) -> bool:
            name = os.path.basename(path)
            return all(s.lower() in name.lower() for s in self.cygnss_required_substrings)
        filtered = [f for f in files if match_required(f)]
        if not filtered:
            # 若严格筛选后为空，回退到全部匹配
            filtered = files
        filtered = sorted(filtered)
        return filtered

    @staticmethod
    def _pick_var(ds: "xr.Dataset", candidates: List[str]) -> Optional[str]:
        for name in candidates:
            if name in ds.variables or name in ds.data_vars or name in ds.coords:
                return name
        return None

    @staticmethod
    def _to_datetime64(series) -> np.ndarray:
        """让时间坐标尽量变成 np.datetime64[ns] 数组。"""
        vals = series.values if hasattr(series, "values") else series
        # xarray 通常已decode_cf，直接 to_datetime 即可
        try:
            return pd.to_datetime(vals).to_numpy()
        except Exception:
            # 退化处理：若是秒 since epoch
            return pd.to_datetime(vals, unit="s", origin="unix").to_numpy()

    @staticmethod
    def _maybe_db_to_linear(arr: np.ndarray, units: Optional[str]) -> np.ndarray:
        """若 units 包含 dB，或值域显著为dB，尝试 dB→线性。"""
        if units is not None and isinstance(units, str) and "db" in units.lower():
            return np.power(10.0, arr / 10.0)
        # 值域启发式（大量负值）
        if np.nanmedian(arr) < -5 and np.nanmax(arr) < 20:
            return np.power(10.0, arr / 10.0)
        return arr

    def _combine_reflectivity_arrays(self, ds: "xr.Dataset", shape: Tuple[int, int]) -> np.ndarray:
        """优先使用 reflectivity_peak, 其次 nbrcs 系列，保持线性单位。"""
        arr = np.full(shape, np.nan, dtype=np.float32)
        candidates = (
            "reflectivity_peak",
            "ddm_nbrcs",
            "ddm_nbrcs_center",
            "ddm_nbrcs_peak",
        )
        for name in candidates:
            if name not in ds:
                continue
            data = np.asarray(ds[name].values, dtype=np.float32)
            if name == "ddm_nbrcs" and "ddm_nbrcs_scale_factor" in ds:
                scale = np.asarray(ds["ddm_nbrcs_scale_factor"].values, dtype=np.float32)
                if scale.shape == data.shape:
                    data = data * scale
            arr = np.where(np.isfinite(arr), arr, data)

        if np.isnan(arr).all():
            try:
                arr = self._extract_specular_from_brcs(ds)
            except Exception:
                pass
        return arr

    def _extract_specular_from_brcs(self, ds: "xr.Dataset") -> np.ndarray:
        """兜底：根据 specular bin 索引从 4D BRCS 提取标量。"""
        needed = {"brcs", "brcs_ddm_sp_bin_delay_row", "brcs_ddm_sp_bin_dopp_col"}
        if not needed.issubset(set(ds.data_vars)):
            n_sample = int(ds.dims.get("sample", 0) or 0)
            n_ddm = int(ds.dims.get("ddm", 0) or 0)
            return np.full((n_sample, n_ddm), np.nan, dtype=np.float32)
        brcs = np.asarray(ds["brcs"].values, dtype=np.float32)
        delay_idx = np.rint(np.asarray(ds["brcs_ddm_sp_bin_delay_row"].values)).astype(int)
        doppler_idx = np.rint(np.asarray(ds["brcs_ddm_sp_bin_dopp_col"].values)).astype(int)
        n_sample, n_ddm, n_delay, n_dopp = brcs.shape
        delay_idx = np.clip(delay_idx, 0, n_delay - 1)
        doppler_idx = np.clip(doppler_idx, 0, n_dopp - 1)
        sample_idx = np.arange(n_sample)[:, None]
        ddm_idx = np.arange(n_ddm)[None, :]
        values = brcs[sample_idx, ddm_idx, delay_idx, doppler_idx]
        return values.astype(np.float32)

    def _extract_power_brcs_specular_points(self, ds: "xr.Dataset", path: str) -> Optional[pd.DataFrame]:
        """针对 CYGNSS L1 v3.2 power-brcs 文件提取 specular 点。"""
        required = {"ddm_timestamp_utc", "sp_lat", "sp_lon"}
        if not required.issubset(set(ds.variables) | set(ds.coords)):
            return None

        n_sample = ds.dims.get("sample")
        n_ddm = ds.dims.get("ddm")
        if not n_sample or not n_ddm:
            return None

        time_idx = pd.to_datetime(ds["ddm_timestamp_utc"].values, utc=True, errors="coerce")
        lat = np.asarray(ds["sp_lat"].values, dtype=np.float32)
        lon = np.asarray(ds["sp_lon"].values, dtype=np.float32)
        inc = (
            np.asarray(ds["sp_inc_angle"].values, dtype=np.float32)
            if "sp_inc_angle" in ds
            else np.full_like(lat, np.nan, dtype=np.float32)
        )

        reflect = self._combine_reflectivity_arrays(ds, lat.shape)
        ddm_ant = (
            np.asarray(ds["ddm_ant"].values, dtype=np.float32)
            if "ddm_ant" in ds
            else np.full(lat.shape, np.nan, dtype=np.float32)
        )
        quality = (
            np.asarray(ds["quality_flags_2"].values, dtype=np.float32)
            if "quality_flags_2" in ds
            else None
        )
        track_id = (
            np.asarray(ds["track_id"].values, dtype=np.float32)
            if "track_id" in ds
            else None
        )
        spacecraft = (
            int(ds["spacecraft_num"].values)
            if "spacecraft_num" in ds
            else None
        )

        minx, miny, maxx, maxy = self.roi_polygon.bounds
        bbox_mask = (
            np.isfinite(lat)
            & np.isfinite(lon)
            & (lon >= minx)
            & (lon <= maxx)
            & (lat >= miny)
            & (lat <= maxy)
        )
        ant_mask = np.isfinite(ddm_ant) & np.isin(ddm_ant, (2, 3))
        mask = bbox_mask & ant_mask

        if not np.any(mask):
            return pd.DataFrame(columns=["time", "lat", "lon", "incidence_angle", "reflectivity"])

        flat_mask = mask.reshape(-1)
        time_flat = np.repeat(time_idx.to_numpy(), n_ddm)[flat_mask]
        lat_flat = lat.reshape(-1)[flat_mask]
        lon_flat = lon.reshape(-1)[flat_mask]
        inc_flat = inc.reshape(-1)[flat_mask]
        refl_flat = reflect.reshape(-1)[flat_mask]
        ant_flat = ddm_ant.reshape(-1)[flat_mask].astype(np.int16)
        ddm_index = np.tile(np.arange(n_ddm, dtype=np.int16), int(n_sample))[flat_mask]

        df = pd.DataFrame(
            {
                "time": pd.to_datetime(time_flat, utc=True, errors="coerce"),
                "lat": lat_flat,
                "lon": lon_flat,
                "incidence_angle": inc_flat,
                "reflectivity": refl_flat,
                "ddm_index": ddm_index,
                "ddm_ant": ant_flat,
                "src_file": os.path.basename(path),
            }
        )

        if quality is not None:
            df["quality_flags_2"] = quality.reshape(-1)[flat_mask]
        if track_id is not None:
            df["track_id"] = track_id.reshape(-1)[flat_mask]
        if spacecraft is not None:
            df["spacecraft"] = spacecraft

        df = df.dropna(subset=["time", "lat", "lon", "reflectivity"])
        return df

    def _extract_obs_inc_from_ds(self, ds: "xr.Dataset") -> Tuple[np.ndarray, np.ndarray]:
        """
        从一个 L1 文件中抽取：
          - 反射率/BRCS/NBRCS：优先 DDM（sample, delay, doppler）取 max(delay,doppler)，得到 per-sample 标量
          - 入射角 incidence_angle per-sample
        返回 (reflectivity_linear, incidence_angle_deg)，均为 1D np.array，长度与 sample/time 对齐。
        """
        # 候选变量名（尽量覆盖 v3.2 常见命名）
        ddm_candidates = [
            "ddm_nbrcs", "ddm_sp_nbrcs", "nbrcs", "ddm_brcs", "sp_brcs",
            "calibrated_ddm_nbrcs", "calibrated_ddm_brcs",
            "calibrated_bistatic_radar_cross_section", "bistatic_radar_cross_section"
        ]
        one_d_candidates = [
            "reflectivity", "sp_reflectivity", "ddm_sp_reflectivity",
            "sp_nbrcs", "nbrcs_sp", "sp_brcs", "brcs", "nbrcs"
        ]
        inc_candidates = [
            "ddm_sp_incidence_angle", "sp_incidence_angle", "incidence_angle",
            "ddm_sp_inc_angle", "sp_inc_angle", "inc_angle"
        ]

        # 1) incidence
        inc_name = self._pick_var(ds, inc_candidates)
        if inc_name is None:
            # 兜底：自动搜寻含 "inc" 关键词的一维变量
            for name in ds.data_vars:
                if "inc" in name.lower():
                    inc_name = name
                    break
        inc = ds[inc_name].values if inc_name else None

        # 2) reflectivity-like
        # 2.1 尝试 DDM 3D
        ddm_name = self._pick_var(ds, ddm_candidates)
        refl_lin = None
        if ddm_name is None:
            # 兜底：查找带 delay+doppler 维度的变量
            for name, da in ds.data_vars.items():
                dims_lower = [d.lower() for d in da.dims]
                if any("delay" in d for d in dims_lower) and any("doppler" in d for d in dims_lower):
                    if any(keyword in name.lower() for keyword in ("nbrcs", "brcs", "reflect", "power")):
                        ddm_name = name
                        break

        if ddm_name is not None:
            da = ds[ddm_name]
            # 自动识别 delay/doppler 维度名（长度一般十几）
            delay_dim = next((d for d in da.dims if re.search("delay", d, re.I)), None)
            doppler_dim = next((d for d in da.dims if re.search("doppler", d, re.I)), None)
            sample_dim = next((d for d in da.dims if d not in (delay_dim, doppler_dim)), None)
            if delay_dim and doppler_dim and sample_dim:
                # 峰值 NBRCS（对 delay/doppler 取最大）
                ddm_peak = da.max(dim=(delay_dim, doppler_dim), skipna=True).values
                units = da.attrs.get("units", None)
                refl_lin = self._maybe_db_to_linear(ddm_peak, units)
        # 2.2 尝试 1D reflectivity/nbrcs
        if refl_lin is None:
            one = self._pick_var(ds, one_d_candidates)
            if one is None:
                # 再兜底：扫描所有变量名含 brcs/nbrcs/reflect/power 的一维量
                for name, da in ds.data_vars.items():
                    if da.ndim == 1 and any(keyword in name.lower() for keyword in ("nbrcs", "brcs", "reflect", "power")):
                        one = name
                        break
            if one is not None:
                da = ds[one]
                units = da.attrs.get("units", None)
                refl_lin = self._maybe_db_to_linear(da.values, units)

        if refl_lin is None:
            available = ", ".join(sorted(ds.data_vars)) or "<无数据变量>"
            raise KeyError(
                (
                    "未找到可用的 CYGNSS 反射率/NBRCS 变量（DDM 或 1D）。"
                    "已尝试关键字：nbrcs/brcs/reflect/power。"
                    f" 可用变量：{available}"
                )
            )

        # incidence 可能缺失，填 NaN
        if inc is None:
            inc = np.full_like(refl_lin, np.nan, dtype=float)

        # 尽量压成 1D（与样本维度同长）
        refl_lin = np.asarray(refl_lin).reshape(-1)
        inc = np.asarray(inc).reshape(-1)
        return refl_lin, inc

    def _read_one_cygnss_file_to_df(self, path: str) -> pd.DataFrame:
        """读取单个 L1 文件 -> DataFrame: [time, lat, lon, incidence_angle, reflectivity]."""
        if xr is None:
            raise RuntimeError("需要 xarray，请安装：pip install xarray netCDF4 h5netcdf")
        with xr.open_dataset(path) as ds:
            specialized = self._extract_power_brcs_specular_points(ds, path)
            if specialized is not None:
                return specialized

            # time/lat/lon 候选（通用兜底）
            tname = self._pick_var(ds, ["time", "sp_time", "ddm_time_utc", "ddm_timestamp_utc", "ddm_time"])
            latn = self._pick_var(ds, ["ddm_sp_lat", "sp_lat", "lat", "latitude", "ddm_sp_latitude"])
            lonn = self._pick_var(ds, ["ddm_sp_lon", "sp_lon", "lon", "longitude", "ddm_sp_longitude"])
            if tname is None or latn is None or lonn is None:
                raise KeyError(f"{os.path.basename(path)} 未找到 time/lat/lon 变量。")

            time_vals = self._to_datetime64(ds[tname])
            lat_vals = ds[latn].values
            lon_vals = ds[lonn].values

            refl_lin, inc_deg = self._extract_obs_inc_from_ds(ds)

            n = min(len(time_vals), len(lat_vals), len(lon_vals), len(refl_lin), len(inc_deg))
            df = pd.DataFrame(
                {
                    "time": pd.to_datetime(time_vals[:n]).tz_localize(
                        "UTC", nonexistent="shift_forward", ambiguous="NaT", errors="coerce"
                    ),
                    "lat": lat_vals[:n],
                    "lon": lon_vals[:n],
                    "incidence_angle": inc_deg[:n],
                    "reflectivity": refl_lin[:n],
                    "src_file": os.path.basename(path),
                }
            )
            df = df.dropna(subset=["time", "lat", "lon"])
            return df

    def _spatial_filter_df_by_aoi(self, df: pd.DataFrame) -> pd.DataFrame:
        """点在 AOI 多边形内。预期 df 已经通过 bbox 粗裁剪。"""
        if df.empty:
            return df
        minx, miny, maxx, maxy = self.roi_polygon.bounds
        df = df[(df["lon"] >= minx) & (df["lon"] <= maxx) & (df["lat"] >= miny) & (df["lat"] <= maxy)]
        if df.empty:
            return df
        mask = df.apply(lambda r: self.roi_polygon.contains(Point(float(r["lon"]), float(r["lat"]))), axis=1)
        return df[mask].copy()

    def _read_local_cygnss_l1_v32(self):
        """
        主入口：从本地目录读取 CYGNSS L1 v3.2，抽取 per-sample 点位与观测，
        过滤到 AOI，计算每日覆盖与每日 ROI 平均观测。
        """
        files = self._discover_cygnss_files()
        if not files:
            raise FileNotFoundError(f"在目录 {self.local_cygnss_dir} 下未找到CYGNSS文件（pattern={self.cygnss_glob_pattern}）。")

        dfs = []
        for fp in files:
            try:
                df_one = self._read_one_cygnss_file_to_df(fp)
                dfs.append(df_one)
            except Exception as e:
                # 某些文件可能字段差异，跳过并打印提示
                print(f"[WARN] 解析失败（跳过）：{os.path.basename(fp)} -> {e}")

        if not dfs:
            raise RuntimeError("未能从任何 L1 文件成功抽取观测。请检查变量名候选或文件内容。")

        df_all = pd.concat(dfs, ignore_index=True)
        # 时间范围过滤
        df_all = df_all[(df_all["time"] >= self.dates.min()) & (df_all["time"] <= self.dates.max() + pd.Timedelta(days=1))]

        # AOI 精筛
        df_all = self._spatial_filter_df_by_aoi(df_all)

        # 保存 sample 级点（供可视化或调试）
        self.cygnss_points_df = df_all.copy()

        # 每日覆盖（达到阈值 min_hits_per_day）
        day_counts = df_all.groupby(df_all["time"].dt.floor("D")).size()
        self.coverage_series = (day_counts >= self.min_hits_per_day)

        # 每日 ROI 平均观测（线性 reflectivity 与 incidence_angle）
        daily = df_all.groupby(df_all["time"].dt.floor("D")).agg(
            reflectivity=("reflectivity", "mean"),
            incidence_angle=("incidence_angle", "mean"),
            n_points=("reflectivity", "size")
        )
        # 索引已经继承了 UTC 时区信息，无需再次 tz_localize
        self.cygnss_daily_obs_df = daily.sort_index()

    # ---------------------- 计划表 + EnKF + LHS ----------------------
    def _build_daily_plan(self):
        plan = pd.DataFrame({"date": self.dates})
        plan["has_cygnss"] = plan["date"].dt.floor("D").map(lambda d: bool(self.coverage_series.get(d, False)))

        plan["gee_imerg_ok"] = bool(self.availability.get("imerg", {}).get("has_data", False))
        plan["gee_era5_ok"]  = bool(self.availability.get("era5_land", {}).get("has_data", False))
        plan["gee_ndvi_ok"]  = bool(self.availability.get("modis_ndvi", {}).get("has_data", False))

        plan["local_imerg"] = False
        plan["local_era5"]  = False
        plan["local_ndvi"]  = False

        self.daily_plan = plan
        self._update_ready_flag()

    def _update_ready_flag(self):
        p = self.daily_plan
        self.daily_plan["ready_for_assim"] = (
            p["has_cygnss"] &
            (p["gee_imerg_ok"] | p["local_imerg"]) &
            (p["gee_era5_ok"]  | p["local_era5"]) &
            (p["gee_ndvi_ok"]  | p["local_ndvi"])
        )

    def _build_enkf_config(self):
        self.enkf_config = {
            "state_init_mean": [0.25, 1.00],   # [SM0, VWC0]
            "state_init_std":  [0.02, 0.40],
            "Q_std":           [0.015, 0.15],
            "R_std":           [0.02],
            "obs_params": {
                "inc_angle_deg": 40.0,        # 若当天有观测，则以实际入射角为准
                "surf_rms_height_m": 0.01,
                "veg_b": 0.12,
                "soil_temp_K": 295.0
            },
            "ensemble_size": 50
        }

    def _build_lhs_samples(self):
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
        bounds = np.array([param_ranges[n] for n in names], dtype=float)
        sampler = LatinHypercube(d=len(names), seed=self.random_seed)
        unit = sampler.random(n=self.lhs_samples)
        samples = bounds[:, 0] + unit * (bounds[:, 1] - bounds[:, 0])
        self.lhs_params = pd.DataFrame(samples, columns=names)

    # ---------------------- 制品导出 ----------------------
    def _export_artifacts(self):
        # availability
        with open(os.path.join(self.output_dir, "availability_report.json"), "w", encoding="utf-8") as f:
            json.dump(self.availability, f, ensure_ascii=False, indent=2)

        # daily plan
        if self.daily_plan is not None:
            self.daily_plan.to_csv(os.path.join(self.output_dir, "daily_run_plan.csv"), index=False)

        # enkf config
        with open(os.path.join(self.output_dir, "enkf_config.json"), "w", encoding="utf-8") as f:
            json.dump(self.enkf_config, f, ensure_ascii=False, indent=2)

        # lhs params
        if self.lhs_params is not None:
            self.lhs_params.to_csv(os.path.join(self.output_dir, "lhs_params.csv"), index=False)

        # cygnss daily obs
        if self.cygnss_daily_obs_df is not None:
            self.cygnss_daily_obs_df.to_csv(os.path.join(self.output_dir, "cygnss_daily_obs.csv"))
