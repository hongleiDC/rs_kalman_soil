# -*- coding: utf-8 -*-
"""基于物理的 GNSS-R 观测算子, 将状态向量映射到反射率。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


def _debye_permittivity(frequency_hz: float, temperature_kelvin: float) -> complex:
    """使用单极 Debye 模型计算液态水的复介电常数。"""

    t_c = temperature_kelvin - 273.15
    epsilon_static = 87.9 - 0.404 * t_c + 9.33e-4 * t_c**2
    epsilon_infinity = 4.9
    relaxation_time = (
        1.1109e-10 - 3.824e-12 * t_c + 6.938e-14 * t_c**2 - 5.096e-16 * t_c**3
    )
    omega = 2.0 * np.pi * frequency_hz
    return epsilon_infinity + (epsilon_static - epsilon_infinity) / (1.0 + 1j * omega * relaxation_time)


@dataclass
class ObservationParams:
    """观测模型所需的辅助参数。"""

    incidence_angle_deg: float  # 入射角 (deg)
    surface_rms_height_m: float  # 地表均方根高度 (m)
    vegetation_b: float  # VWC 到 VOD 的线性系数
    temperature_kelvin: float  # 土壤温度 (K)


class ObservationModel:
    """将 ``[SM, VWC]`` 状态映射成 GNSS-R 反射率。"""

    def __init__(
        self,
        *,
        sand_fraction: float,
        clay_fraction: float,
        bulk_density: float = 1.3,
        particle_density: float = 2.65,
        frequency_hz: float = 1.57542e9,
        default_incidence_angle_deg: float = 40.0,
        vegetation_b: float = 0.12,
        surface_rms_height_m: float = 0.01,
        bound_water_factor: float = 0.3,
    ) -> None:
        # 土壤质地与物理常数
        self.sand_fraction = sand_fraction
        self.clay_fraction = clay_fraction
        self.bulk_density = bulk_density
        self.particle_density = particle_density
        self.frequency_hz = frequency_hz

        # 默认观测几何与地表/植被参数
        self.default_incidence_angle = default_incidence_angle_deg
        self.default_vegetation_b = vegetation_b
        self.default_surface_rms_height = surface_rms_height_m
        self.bound_water_factor = bound_water_factor

        # 土壤孔隙度, 用于划分束缚水与自由水
        self.porosity = 1.0 - bulk_density / particle_density

    # ------------------------------------------------------- 介电常数与反射率
    def _mironov_dielectric(self, sm: np.ndarray, temperature_kelvin: float) -> np.ndarray:
        """Mironov(2009) 模型: 由 SM 推导复介电常数。"""

        sm = np.clip(sm, 1e-6, self.porosity - 1e-6)
        epsilon_soil_solid = 4.7 - 0.62j * self.clay_fraction
        epsilon_free = _debye_permittivity(self.frequency_hz, temperature_kelvin)
        epsilon_bound = 7.0 - 0.8j

        theta_bound = np.minimum(self.bound_water_factor * self.clay_fraction * self.porosity, sm)
        theta_free = np.maximum(sm - theta_bound, 0.0)

        g = 0.65
        phi = max(self.porosity, 1e-6)
        bound_ratio = np.clip(theta_bound / phi, 0.0, 1.0)
        free_ratio = np.clip(theta_free / phi, 0.0, 1.0)

        sqrt_eps_solid = np.sqrt(epsilon_soil_solid)
        sqrt_eps_bound = np.sqrt(epsilon_bound)
        sqrt_eps_free = np.sqrt(epsilon_free)

        mix = (
            1.0
            + (1.0 - phi) ** g * (sqrt_eps_solid - 1.0)
            + bound_ratio**g * (sqrt_eps_bound - 1.0)
            + free_ratio**g * (sqrt_eps_free - 1.0)
        )
        return mix**2

    def _fresnel_cross_pol(self, epsilon: np.ndarray, incidence_angle_rad: float) -> np.ndarray:
        """根据菲涅尔方程计算交叉极化反射率。"""

        cos_theta = np.cos(incidence_angle_rad)
        sin_theta_sq = np.sin(incidence_angle_rad) ** 2
        sqrt_term = np.sqrt(epsilon - sin_theta_sq)

        r_hh = (cos_theta - sqrt_term) / (cos_theta + sqrt_term)
        r_vv = (epsilon * cos_theta - sqrt_term) / (epsilon * cos_theta + sqrt_term)
        return 0.5 * np.abs(r_vv - r_hh) ** 2

    # ------------------------------------------------------------ 对外接口
    def run(
        self,
        state: np.ndarray,
        params: ObservationParams | Mapping[str, float] | None = None,
    ) -> np.ndarray:
        """将状态向量映射到观测空间。支持单个状态与集合。"""

        if params is None:
            observation_params = ObservationParams(
                incidence_angle_deg=self.default_incidence_angle,
                surface_rms_height_m=self.default_surface_rms_height,
                vegetation_b=self.default_vegetation_b,
                temperature_kelvin=295.0,
            )
        elif isinstance(params, Mapping):
            observation_params = ObservationParams(**params)  # type: ignore[arg-type]
        else:
            observation_params = params

        state = np.asarray(state, dtype=float)
        was_one_dimensional = state.ndim == 1
        ensemble = state.reshape(1, -1) if was_one_dimensional else state

        sm = ensemble[:, 0]
        vwc = ensemble[:, 1]

        epsilon = self._mironov_dielectric(sm, observation_params.temperature_kelvin)
        theta_rad = np.deg2rad(observation_params.incidence_angle_deg)
        gamma_smooth = self._fresnel_cross_pol(epsilon, theta_rad)

        wavelength = 299792458.0 / self.frequency_hz
        k = 2.0 * np.pi / wavelength
        h = (2.0 * k * observation_params.surface_rms_height_m) ** 2 * np.cos(theta_rad) ** 2
        roughness_factor = np.exp(-h)

        tau = observation_params.vegetation_b * vwc
        vegetation_factor = np.exp(-2.0 * tau / np.cos(theta_rad))

        reflectivity = gamma_smooth * roughness_factor * vegetation_factor
        return reflectivity[0] if was_one_dimensional else reflectivity
