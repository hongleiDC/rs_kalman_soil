# -*- coding: utf-8 -*-
"""集合卡尔曼滤波器 (EnKF) 实现。

该模块根据 Evensen (2003) 的随机 EnKF 思路, 支持向量状态、任意过程模型与观测算子。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass
class EnsembleStatistics:
    """记录集合均值与距平, 便于计算协方差。"""

    mean: np.ndarray
    anomalies: np.ndarray


class EnsembleKalmanFilter:
    """随机集合卡尔曼滤波器。"""

    def __init__(self, process_model, observation_model, ensemble_size: int = 50) -> None:
        self.process_model = process_model
        self.observation_model = observation_model
        self.N = ensemble_size

        self.ensemble: np.ndarray | None = None
        self.state_dim: int | None = None
        self.state_estimate: np.ndarray | None = None

    # ------------------------------------------------------------ 内部工具
    def _ensure_initialized(self) -> np.ndarray:
        if self.ensemble is None:
            raise RuntimeError("EnKF 尚未通过 initialize() 初始化集合。")
        return self.ensemble

    @staticmethod
    def _stats(matrix: np.ndarray) -> EnsembleStatistics:
        mean = np.mean(matrix, axis=0)
        anomalies = matrix - mean
        return EnsembleStatistics(mean=mean, anomalies=anomalies)

    def _apply_physical_bounds(self) -> None:
        """根据过程模型提供的极值限制集合成员。"""

        if self.ensemble is None or self.state_dim is None:
            return
        if self.state_dim >= 1 and hasattr(self.process_model, "sm_sat"):
            self.ensemble[:, 0] = np.clip(self.ensemble[:, 0], 0.0, self.process_model.sm_sat)
        if self.state_dim >= 2 and hasattr(self.process_model, "vwc_max"):
            self.ensemble[:, 1] = np.clip(self.ensemble[:, 1], 0.0, self.process_model.vwc_max)

    # ------------------------------------------------------------- 公共接口
    def initialize(self, initial_mean: Sequence[float], initial_cov: np.ndarray) -> None:
        """根据初值均值/协方差生成集合。"""

        mean = np.asarray(initial_mean, dtype=float)
        cov = np.asarray(initial_cov, dtype=float)
        if cov.ndim == 1:
            cov = np.diag(cov)

        self.state_dim = mean.shape[0]
        self.ensemble = np.random.multivariate_normal(mean, cov, size=self.N)
        self._apply_physical_bounds()
        self.state_estimate = np.mean(self.ensemble, axis=0)

    def forecast(
        self,
        forcings: Mapping[str, float] | Sequence[float] | None,
        process_noise_cov: np.ndarray,
    ) -> None:
        """利用过程模型推进集合, 并注入过程噪声。"""

        ensemble = self._ensure_initialized()
        propagated = self.process_model.run(ensemble, forcings if forcings is not None else {})

        q = np.asarray(process_noise_cov, dtype=float)
        if q.ndim == 1:
            q = np.diag(q)
        process_noise = np.random.multivariate_normal(np.zeros(q.shape[0]), q, size=self.N)

        self.ensemble = propagated + process_noise
        self._apply_physical_bounds()
        self.state_estimate = np.mean(self.ensemble, axis=0)

    def analysis(
        self,
        observation: Sequence[float] | float,
        observation_cov: np.ndarray,
        obs_params: Mapping[str, float] | None = None,
    ) -> None:
        """结合观测更新集合成员。"""

        ensemble = self._ensure_initialized()
        predicted_obs = self.observation_model.run(ensemble, obs_params)
        predicted_obs = np.atleast_2d(predicted_obs).reshape(self.N, -1)

        state_stats = self._stats(ensemble)
        obs_stats = self._stats(predicted_obs)

        cov_xz = state_stats.anomalies.T @ obs_stats.anomalies / (self.N - 1)

        r = np.asarray(observation_cov, dtype=float)
        if r.ndim == 1:
            r = np.diag(r)
        cov_zz = obs_stats.anomalies.T @ obs_stats.anomalies / (self.N - 1) + r

        kalman_gain = cov_xz @ np.linalg.inv(cov_zz)

        obs_vector = np.asarray(observation, dtype=float)
        obs_vector = np.atleast_1d(obs_vector)
        perturbations = np.random.multivariate_normal(np.zeros(r.shape[0]), r, size=self.N)
        perturbed_obs = obs_vector + perturbations

        innovation = perturbed_obs - predicted_obs
        self.ensemble = ensemble + innovation @ kalman_gain.T
        self._apply_physical_bounds()
        self.state_estimate = np.mean(self.ensemble, axis=0)
