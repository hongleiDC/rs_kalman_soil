# -*- coding: utf-8 -*-
"""土壤湿度-植被耦合过程模型。

该模块实现陆面过程模型, 负责在数据同化循环中提供预测步骤: 根据最新的土壤湿度 SM
和植被含水量 VWC, 配合气象强迫字段, 计算下一时刻的状态。公式来源于
``knowledge/2.状态方程设计.md``。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass
class ForcingInputs:
    """单步过程模型所需的气象强迫。"""

    precipitation: float  # 每步降水量 (mm)
    pet: float  # 每步潜在蒸散发量 (mm)
    temperature: float  # 日平均气温 (°C)
    doy: float  # 年积日 (1-366)


class ProcessModel:
    """非线性的水量平衡与植被物候模型。"""

    def __init__(
        self,
        *,
        delta_t_days: float = 1.0,
        root_zone_depth_m: float = 0.3,
        sm_wilt: float = 0.1,
        sm_field: float = 0.35,
        sm_sat: float = 0.45,
        runoff_exponent: float = 3.0,
        r_max: float = 0.25,
        vwc_max: float = 2.5,
        k_sen: float = 0.015,
        t_base: float = 5.0,
        t_opt: float = 30.0,
        season_peak_doy: float = 200.0,
        season_width: float = 60.0,
    ) -> None:
        # 基础参数: 时间步长、根系层厚度、关键土壤阈值等
        self.delta_t = delta_t_days
        self.root_zone_depth = root_zone_depth_m
        self.sm_wilt = sm_wilt
        self.sm_field = sm_field
        self.sm_sat = sm_sat

        # 径流与植被生长控制参数
        self.runoff_exponent = runoff_exponent
        self.r_max = r_max
        self.vwc_max = vwc_max
        self.k_sen = k_sen

        # 温度与季节调节参数
        self.t_base = t_base
        self.t_opt = t_opt
        self.season_peak = season_peak_doy
        self.season_width = season_width

    # ------------------------------------------------------------------ 辅助函数
    def _soil_moisture_stress(self, sm: np.ndarray) -> np.ndarray:
        """土壤湿度归一化函数: 将 SM 映射到 [0,1] 的水分胁迫因子。"""

        stress = (sm - self.sm_wilt) / (self.sm_field - self.sm_wilt)
        return np.clip(stress, 0.0, 1.0)

    def _runoff(self, sm: np.ndarray, precipitation: float) -> np.ndarray:
        """使用幂律形式计算饱和超渗径流。"""

        saturation = self._soil_moisture_stress(sm)
        return np.clip(precipitation * saturation**self.runoff_exponent, 0.0, precipitation)

    def _evapotranspiration(self, sm: np.ndarray, pet: float) -> np.ndarray:
        """将潜在蒸散发乘以水分胁迫系数得到实际蒸散发。"""

        beta = self._soil_moisture_stress(sm)
        return np.clip(beta * pet, 0.0, pet)

    def _temperature_limiter(self, temperature: float) -> float:
        """温度限制因子: 低于基线时生长为零, 高于最佳温度后保持 1。"""

        if temperature <= self.t_base:
            return 0.0
        scale = (temperature - self.t_base) / max(self.t_opt - self.t_base, 1e-6)
        return float(np.clip(scale, 0.0, 1.0))

    def _season_limiter(self, doy: float) -> float:
        """季节限制因子: 以高斯曲线近似光周期/物候效应。"""

        relative = (doy - self.season_peak) / self.season_width
        return float(np.exp(-relative**2))

    # ------------------------------------------------------------------ 核心接口
    def run(self, state: np.ndarray, forcings: ForcingInputs | Mapping[str, float]) -> np.ndarray:
        """给定气象强迫, 将状态向量推进一个时间步。"""

        if isinstance(forcings, Mapping):
            inputs = ForcingInputs(**forcings)  # type: ignore[arg-type]
        else:
            inputs = forcings

        state = np.asarray(state, dtype=float)
        was_one_dimensional = state.ndim == 1
        ensemble = state.reshape(1, -1) if was_one_dimensional else state.copy()

        sm = ensemble[:, 0]
        vwc = ensemble[:, 1]

        runoff = self._runoff(sm, inputs.precipitation)
        et = self._evapotranspiration(sm, inputs.pet)

        # 由水量平衡得到的 SM 变化, 分母 1000 将 mm 转换为 m
        sm_increment = (
            self.delta_t / (self.root_zone_depth * 1000.0)
            * (inputs.precipitation - runoff - et)
        )
        sm_new = np.clip(sm + sm_increment, 0.0, self.sm_sat)

        # 植被生长受温度、季节与土壤水分三重限制, 再乘逻辑斯蒂项避免爆发式增长
        growth_limiters = (
            self._temperature_limiter(inputs.temperature)
            * self._season_limiter(inputs.doy)
            * self._soil_moisture_stress(sm)
        )
        growth = self.r_max * growth_limiters * (1.0 - vwc / self.vwc_max)
        senescence = self.k_sen * vwc
        vwc_new = np.clip(vwc + self.delta_t * (growth - senescence), 0.0, self.vwc_max)

        updated_state = np.column_stack((sm_new, vwc_new))
        return updated_state[0] if was_one_dimensional else updated_state
