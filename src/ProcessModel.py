# -*- coding: utf-8 -*-
"""Coupled soil moisture and vegetation process model for the EnKF framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass
class ForcingInputs:
    """Meteorological inputs required by the process model for a single step."""

    precipitation: float  # mm per time step
    pet: float  # mm per time step
    temperature: float  # degrees Celsius
    doy: float  # day of year (1-366)


class ProcessModel:
    """Non-linear water balance and vegetation phenology model.

    The state vector is ``[SM, VWC]`` where ``SM`` is volumetric soil moisture and
    ``VWC`` is vegetation water content. Formulations follow the design notes in
    ``knowledge/2.状态方程设计.md``.
    """

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
        self.delta_t = delta_t_days
        self.root_zone_depth = root_zone_depth_m
        self.sm_wilt = sm_wilt
        self.sm_field = sm_field
        self.sm_sat = sm_sat
        self.runoff_exponent = runoff_exponent
        self.r_max = r_max
        self.vwc_max = vwc_max
        self.k_sen = k_sen
        self.t_base = t_base
        self.t_opt = t_opt
        self.season_peak = season_peak_doy
        self.season_width = season_width

    # --- helper formulations -------------------------------------------------
    def _soil_moisture_stress(self, sm: np.ndarray) -> np.ndarray:
        stress = (sm - self.sm_wilt) / (self.sm_field - self.sm_wilt)
        return np.clip(stress, 0.0, 1.0)

    def _runoff(self, sm: np.ndarray, precipitation: float) -> np.ndarray:
        saturation = self._soil_moisture_stress(sm)
        return np.clip(precipitation * saturation**self.runoff_exponent, 0.0, precipitation)

    def _evapotranspiration(self, sm: np.ndarray, pet: float) -> np.ndarray:
        beta = self._soil_moisture_stress(sm)
        return np.clip(beta * pet, 0.0, pet)

    def _temperature_limiter(self, temperature: float) -> float:
        if temperature <= self.t_base:
            return 0.0
        scale = (temperature - self.t_base) / max(self.t_opt - self.t_base, 1e-6)
        return float(np.clip(scale, 0.0, 1.0))

    def _season_limiter(self, doy: float) -> float:
        relative = (doy - self.season_peak) / self.season_width
        return float(np.exp(-relative**2))

    # --- core API ------------------------------------------------------------
    def run(self, state: np.ndarray, forcings: ForcingInputs | Mapping[str, float]) -> np.ndarray:
        """Propagate the state by one time step given meteorological forcings."""

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

        sm_increment = (
            self.delta_t
            / (self.root_zone_depth * 1000.0)
            * (inputs.precipitation - runoff - et)
        )
        sm_new = np.clip(sm + sm_increment, 0.0, self.sm_sat)

        growth_limiters = (
            self._temperature_limiter(inputs.temperature)
            * self._season_limiter(inputs.doy)
            * self._soil_moisture_stress(sm)
        )
        growth = self.r_max * growth_limiters * (1.0 - vwc / self.vwc_max)
        senescence = self.k_sen * vwc
        vwc_new = np.clip(vwc + self.delta_t * (growth - senescence), 0.0, self.vwc_max)

        updated_state = np.column_stack((sm_new, vwc_new))
        if was_one_dimensional:
            return updated_state[0]
        return updated_state
