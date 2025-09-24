# -*- coding: utf-8 -*-
"""GNSS-R 土壤湿度 EnKF 原型: 命令行模拟入口。"""

from __future__ import annotations

import math
from dataclasses import asdict

import numpy as np

from ProcessModel import ForcingInputs, ProcessModel
from ObservationModel import ObservationModel, ObservationParams
from EnsembleKalmanFilter import EnsembleKalmanFilter


def generate_forcings(num_steps: int, seed: int = 7) -> list[ForcingInputs]:
    """构造具有季节周期的气象强迫序列。"""

    rng = np.random.default_rng(seed)
    forcings: list[ForcingInputs] = []
    doy0 = 120
    for k in range(num_steps):
        doy = (doy0 + k) % 365 + 1
        seasonal = math.sin(2.0 * math.pi * (doy - 80) / 365.0)
        precipitation = max(0.0, 2.0 + 4.0 * seasonal + rng.normal(0.0, 1.5))
        pet = max(0.5, 3.5 + 1.0 * seasonal + rng.normal(0.0, 0.3))
        temperature = 18.0 + 10.0 * seasonal + rng.normal(0.0, 1.5)
        forcings.append(
            ForcingInputs(
                precipitation=precipitation,
                pet=pet,
                temperature=temperature,
                doy=doy,
            )
        )
    return forcings


def create_truth(
    process_model: ProcessModel,
    observation_model: ObservationModel,
    forcings: list[ForcingInputs],
    process_noise_std: np.ndarray,
    obs_params: ObservationParams,
    seed: int = 42,
):
    """生成“真实”土壤湿度/植被状态及对应的反射率观测。"""

    rng = np.random.default_rng(seed)
    num_steps = len(forcings)
    truth_states = np.zeros((num_steps, 2))
    reflectivity = np.zeros(num_steps)

    state = np.array([0.25, 1.2])
    for idx, forcing in enumerate(forcings):
        state = process_model.run(state, forcing)
        state += rng.normal(0.0, process_noise_std)
        state[0] = np.clip(state[0], 0.0, process_model.sm_sat)
        state[1] = np.clip(state[1], 0.0, process_model.vwc_max)
        truth_states[idx] = state
        reflectivity[idx] = observation_model.run(state, obs_params)

    return truth_states, reflectivity


def main() -> None:
    """执行模拟并打印关键统计量。"""

    np.set_printoptions(precision=3, suppress=True)

    process_model = ProcessModel()
    observation_model = ObservationModel(sand_fraction=0.45, clay_fraction=0.25)

    forcings = generate_forcings(num_steps=120)
    obs_params = ObservationParams(
        incidence_angle_deg=40.0,
        surface_rms_height_m=0.015,
        vegetation_b=0.12,
        temperature_kelvin=295.0,
    )

    truth_states, truth_reflectivity = create_truth(
        process_model,
        observation_model,
        forcings,
        process_noise_std=np.array([0.01, 0.1]),
        obs_params=obs_params,
    )

    observation_noise_std = 0.01
    observations = truth_reflectivity + np.random.normal(0.0, observation_noise_std, size=len(truth_reflectivity))

    enkf = EnsembleKalmanFilter(process_model, observation_model, ensemble_size=80)
    enkf.initialize(initial_mean=[0.20, 0.8], initial_cov=np.diag([0.02**2, 0.4**2]))

    q = np.diag([0.015**2, 0.15**2])
    r = np.array([[observation_noise_std**2]])

    analysis = np.zeros_like(truth_states)
    forecast = np.zeros_like(truth_states)

    for idx, forcing in enumerate(forcings):
        enkf.forecast(asdict(forcing), q)
        forecast[idx] = enkf.state_estimate
        enkf.analysis(observations[idx], r, asdict(obs_params))
        analysis[idx] = enkf.state_estimate

    print("Final truth state          :", truth_states[-1])
    print("Final EnKF analysis state  :", analysis[-1])
    print("Final EnKF forecast state  :", forecast[-1])
    print("Mean absolute SM error (m3/m3):", np.mean(np.abs(analysis[:, 0] - truth_states[:, 0])))
    print("Mean absolute VWC error (kg/m2):", np.mean(np.abs(analysis[:, 1] - truth_states[:, 1])))


if __name__ == "__main__":
    main()
