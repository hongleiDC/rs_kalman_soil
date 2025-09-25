# -*- coding: utf-8 -*-
"""GNSS-R 土壤湿度 EnKF (2021 年 7 月郑州) 实例脚本。

本脚本假设用户提供真实数据集的文件路径, 包括:
1. GPM IMERG 累积降水 (30 分钟或小时级)
2. ERA5-Land 再分析 (变量: t2m, pev)
3. CYGNSS Level 1/2 反射率产品 (含反射率与入射角)
4. 土壤质地静态数据 (如 SoilGrids sand/clay 分数)

当用户提供对应时间范围 (2021-07-01 至 2021-07-31) 的文件地址后, 填写
DATA_CATALOG 中的路径列表即可执行端到端的同化实验。
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import earthaccess
import pandas as pd
import xarray as xr

from ProcessModel import ForcingInputs, ProcessModel
from ObservationModel import ObservationModel, ObservationParams
from EnsembleKalmanFilter import EnsembleKalmanFilter


# ---------------------------------------------------------------------------
# 数据目录与区域定义
# ---------------------------------------------------------------------------

@dataclass
class DataCatalog:
    """记录不同数据源的本地文件路径 (可为 NetCDF/HDF 多个文件)。"""

    imerge_precip: Sequence[Path]
    era5_land: Sequence[Path]
    cygnss_l1: Sequence[Path]
    soil_texture: Path


@dataclass
class Region:
    """简单的经纬度包络框描述, 便于裁剪数据。"""

    name: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


ZHENGZHOU_REGION = Region(
    name="郑州",
    lat_min=34.2,
    lat_max=35.0,
    lon_min=112.8,
    lon_max=114.0,
)

START = pd.Timestamp("2021-07-01", tz="UTC")
END = pd.Timestamp("2021-07-31 23:59:59", tz="UTC")


# ---------------------------------------------------------------------------
# 通用帮助函数
# ---------------------------------------------------------------------------

def _guess_coord_name(ds: xr.Dataset, candidates: Iterable[str]) -> str:
    for name in candidates:
        if name in ds.coords:
            return name
    raise KeyError(f"无法在数据集中找到坐标 {candidates}")


def _subset_bbox(ds: xr.Dataset, region: Region) -> xr.Dataset:
    lat_name = _guess_coord_name(ds, ["lat", "latitude", "Latitude"])
    lon_name = _guess_coord_name(ds, ["lon", "longitude", "Longitude"])

    lat_vals = ds[lat_name]
    lon_vals = ds[lon_name]

    lat_slice = slice(region.lat_max, region.lat_min)
    if lat_vals[0] < lat_vals[-1]:
        lat_slice = slice(region.lat_min, region.lat_max)

    lon_slice = slice(region.lon_min, region.lon_max)
    if lon_vals[0] > lon_vals[-1]:
        lon_slice = slice(region.lon_max, region.lon_min)

    return ds.sel({lat_name: lat_slice, lon_name: lon_slice})


# ---------------------------------------------------------------------------
# 数据读取
# ---------------------------------------------------------------------------

def load_imerge_precip(paths: Sequence[Path], region: Region, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """读取 IMERG 降水并聚合为日尺度 (mm/day)。"""

    ds = xr.open_mfdataset(paths, combine="by_coords")
    ds = _subset_bbox(ds.sel(time=slice(start, end)), region)
    var_name = "precipitationCal" if "precipitationCal" in ds.data_vars else list(ds.data_vars)[0]
    precip = ds[var_name]
    daily = precip.resample(time="1D").sum(dim="time")
    series = daily.mean(dim=[coord for coord in precip.dims if coord != "time"]).to_series()
    series.index = series.index.tz_localize("UTC")
    return series


def load_era5_land(paths: Sequence[Path], region: Region, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """读取 ERA5-Land, 提取 t2m (°C) 与潜在蒸散发 (mm/day)。"""

    ds = xr.open_mfdataset(paths, combine="by_coords")
    ds = _subset_bbox(ds.sel(time=slice(start, end)), region)

    t2m_name = _guess_coord_name(ds, ["t2m", "T2M"]) if "t2m" not in ds.data_vars else "t2m"
    pev_name = "pev"

    temp = ds[t2m_name] - 273.15
    pet = -ds[pev_name] * 1000.0  # era5 中的潜在蒸发为负值, 单位 m

    temp_daily = temp.resample(time="1D").mean()
    pet_daily = pet.resample(time="1D").sum()

    temp_series = temp_daily.mean(dim=[coord for coord in temp_daily.dims if coord != "time"]).to_series()
    pet_series = pet_daily.mean(dim=[coord for coord in pet_daily.dims if coord != "time"]).to_series()

    df = pd.DataFrame({
        "temperature": temp_series,
        "pet": pet_series,
    })
    df.index = df.index.tz_localize("UTC")
    return df


def load_cygnss_reflectivity(paths: Sequence[Path], region: Region, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """读取 CYGNSS Level 1/2 反射率, 输出日平均观测。"""

    ds = xr.open_mfdataset(paths, combine="nested", concat_dim="file", engine="h5netcdf")
    ds = ds.sel(time=slice(start, end))
    ds = _subset_bbox(ds, region)

    candidates = [
        "sp_reflectivity",
        "reflectivity",
        "ddm_sp_reflectivity",
        "ddm_reflectivity",
    ]
    for name in candidates:
        if name in ds.data_vars:
            refl_name = name
            break
    else:
        raise KeyError("在 CYGNSS 数据中未找到反射率变量, 请检查变量名。")

    inc_name = "incidence_angle" if "incidence_angle" in ds.data_vars else "incidence_angle_mean"

    df = ds[[refl_name, inc_name]].to_dataframe().reset_index()
    df = df.groupby(pd.Grouper(key="time", freq="1D")).agg({refl_name: "mean", inc_name: "mean"})
    df.index = df.index.tz_localize("UTC")
    df.rename(columns={refl_name: "reflectivity", inc_name: "incidence_angle"}, inplace=True)
    return df


def load_soil_texture(path: Path, region: Region) -> Mapping[str, float]:
    """读取土壤质地 (沙/粘) 平均值, 供观测/过程模型参数使用。"""

    ds = xr.open_dataset(path)
    ds = _subset_bbox(ds, region)

    sand_var = "sand" if "sand" in ds.data_vars else "sand_fraction"
    clay_var = "clay" if "clay" in ds.data_vars else "clay_fraction"

    sand = float(ds[sand_var].mean().values)
    clay = float(ds[clay_var].mean().values)
    return {"sand_fraction": sand, "clay_fraction": clay}


# ---------------------------------------------------------------------------
# 数据下载 (earthaccess)
# ---------------------------------------------------------------------------

def login_earthdata() -> None:
    """通过 earthaccess 登录 NASA Earthdata (首次运行需输入凭据)。"""

    earthaccess.login()


def _earthaccess_bbox(region: Region) -> tuple[float, float, float, float]:
    return (region.lon_min, region.lat_min, region.lon_max, region.lat_max)


def download_imerge(
    collection_short_name: str,
    region: Region,
    start: pd.Timestamp,
    end: pd.Timestamp,
    out_dir: Path,
) -> list[Path]:
    """使用 earthaccess 下载 GPM IMERG 数据。"""

    temporal = (
        start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        end.strftime('%Y-%m-%dT%H:%M:%SZ'),
    )
    results = earthaccess.search_data(
        short_name=collection_short_name,
        temporal=temporal,
        bounding_box=_earthaccess_bbox(region),
    )
    if not results:
        raise RuntimeError('未检索到 GPM IMERG 数据, 请检查 short_name 和时间范围。')
    out_dir.mkdir(parents=True, exist_ok=True)
    return [Path(p) for p in earthaccess.download(results, path=out_dir)]


def download_cygnss(
    collection_short_name: str,
    region: Region,
    start: pd.Timestamp,
    end: pd.Timestamp,
    out_dir: Path,
) -> list[Path]:
    """使用 earthaccess 下载 CYGNSS Level 1/2 数据。"""

    temporal = (
        start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        end.strftime('%Y-%m-%dT%H:%M:%SZ'),
    )
    results = earthaccess.search_data(
        short_name=collection_short_name,
        temporal=temporal,
        bounding_box=_earthaccess_bbox(region),
    )
    if not results:
        raise RuntimeError('未检索到 CYGNSS 数据, 请检查 short_name 和时间范围。')
    out_dir.mkdir(parents=True, exist_ok=True)
    return [Path(p) for p in earthaccess.download(results, path=out_dir)]


# ---------------------------------------------------------------------------
# 数据准备
# ---------------------------------------------------------------------------

def prepare_forcings(precip: pd.Series, met: pd.DataFrame) -> pd.DataFrame:
    """合并降水、PET、温度信息, 生成同化所需的逐日强迫。"""

    df = met.copy()
    df["precipitation"] = precip
    df["precipitation"].fillna(0.0, inplace=True)
    df = df.dropna(subset=["temperature", "pet"])
    df["doy"] = df.index.dayofyear
    return df


def prepare_observations(obs_df: pd.DataFrame) -> pd.DataFrame:
    """清洗观测, 去除缺失值。"""

    df = obs_df.dropna(subset=["reflectivity"]).copy()
    df["incidence_angle"].fillna(df["incidence_angle"].median(), inplace=True)
    return df


# ---------------------------------------------------------------------------
# 同化执行
# ---------------------------------------------------------------------------

def run_assimilation(
    forcings: pd.DataFrame,
    observations: pd.DataFrame,
    soil_params: Mapping[str, float],
    observation_std: float = 0.02,
) -> pd.DataFrame:
    """使用真实数据执行 EnKF, 返回结果时间序列。"""

    process_model = ProcessModel()
    observation_model = ObservationModel(**soil_params)
    enkf = EnsembleKalmanFilter(process_model, observation_model, ensemble_size=80)

    enkf.initialize(initial_mean=[0.25, 1.2], initial_cov=np.diag([0.02**2, 0.4**2]))
    q = np.diag([0.015**2, 0.15**2])
    r = np.array([[observation_std**2]])

    results = []
    for time, forcing_row in forcings.sort_index().iterrows():
        forcing = ForcingInputs(
            precipitation=float(forcing_row["precipitation"]),
            pet=float(forcing_row["pet"]),
            temperature=float(forcing_row["temperature"]),
            doy=float(forcing_row["doy"]),
        )
        enkf.forecast(forcing.__dict__, q)

        if time in observations.index:
            obs_row = observations.loc[time]
            params = ObservationParams(
                incidence_angle_deg=float(obs_row["incidence_angle"]),
                surface_rms_height_m=0.015,
                vegetation_b=0.12,
                temperature_kelvin=298.0,
            )
            observation_value = float(obs_row["reflectivity"])
            enkf.analysis(observation_value, r, params.__dict__)

        results.append({
            "time": time,
            "sm_forecast": enkf.state_estimate[0],
            "vwc_forecast": enkf.state_estimate[1],
        })

    return pd.DataFrame(results).set_index("time")


# ---------------------------------------------------------------------------
# 主函数 (示例调用)
# ---------------------------------------------------------------------------

def main() -> None:
    """示例入口: 需用户填写真实数据的文件路径。"""

    catalog = DataCatalog(
        imerge_precip=[
            # TODO: 将 GPM IMERG 文件路径填入此列表, 支持多个 NetCDF 文件
        ],
        era5_land=[
            # TODO: ERA5-Land NetCDF 文件路径
        ],
        cygnss_l1=[
            # TODO: CYGNSS L1/L2 文件路径
        ],
        soil_texture=Path("/path/to/soil_texture.nc"),  # TODO: SoilGrids 或其他土壤质地产品
    )

    precip_series = load_imerge_precip(catalog.imerge_precip, ZHENGZHOU_REGION, START, END)
    met_df = load_era5_land(catalog.era5_land, ZHENGZHOU_REGION, START, END)
    forcing_df = prepare_forcings(precip_series, met_df)

    obs_df = load_cygnss_reflectivity(catalog.cygnss_l1, ZHENGZHOU_REGION, START, END)
    obs_df = prepare_observations(obs_df)

    soil_params = load_soil_texture(catalog.soil_texture, ZHENGZHOU_REGION)

    results = run_assimilation(forcing_df, obs_df, soil_params)

    results.to_csv("enkf_results_zhengzhou_202107.csv")
    print(results.tail())


if __name__ == "__main__":
    main()
