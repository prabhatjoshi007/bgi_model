"""Multi-start calibration of the storage model with SLSQP."""

import logging
from dataclasses import dataclass

import numpy as np
import scipy.optimize as optimize

from .model import GR_opt, PARAMETER_NAMES

logger = logging.getLogger(__name__)

LOWER_BOUNDS = np.array([0.01, 0.001, 0.0, 1.0, 0.0, 1.0, 0.0])
UPPER_BOUNDS = np.array([30.0, 0.010, 1.0, 3.0, 1.0, 3.0, 25.0])

SLSQP_OPTIONS = {"maxiter": 1000, "ftol": 1e-4, "disp": False}


@dataclass(frozen=True)
class CalibrationResult:
    """Calibrated parameter sets, ranked by calibration KGE (best first)."""

    parameters: np.ndarray  # shape (n_runs, n_parameters)
    kge: np.ndarray         # shape (n_runs,)

    @property
    def best(self):
        """Parameter set with the highest calibration KGE."""
        return self.parameters[0]


def calibrate(precipitation, pet, qobs, n_runs, seed=42):
    """Maximise KGE from ``n_runs`` random starting points.

    The random starting points come from a generator seeded with ``seed``, so
    the same seed gives the same results on any machine.
    """
    if n_runs < 1:
        raise ValueError("n_runs must be at least 1.")

    rng = np.random.default_rng(seed)
    starts = rng.uniform(LOWER_BOUNDS, UPPER_BOUNDS, size=(n_runs, len(PARAMETER_NAMES)))
    bounds = list(zip(LOWER_BOUNDS, UPPER_BOUNDS))

    def negative_kge(params):
        return -GR_opt(params, precipitation, pet, qobs)

    parameters = np.empty_like(starts)
    kge = np.empty(n_runs)
    for run, x0 in enumerate(starts):
        logger.info("Calibration run %d of %d", run + 1, n_runs)
        result = optimize.minimize(
            negative_kge, x0, method="SLSQP", bounds=bounds, options=SLSQP_OPTIONS
        )
        parameters[run] = result.x
        kge[run] = -result.fun

    order = np.argsort(kge)[::-1]
    return CalibrationResult(parameters=parameters[order], kge=kge[order])
