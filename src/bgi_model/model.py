"""Storage model used for calibration and simulation.

The model has one soil store and one drainage store. Water enters as rainfall,
leaves as evapotranspiration (ET), surface runoff and underdrain flow.
"""

from dataclasses import dataclass

import numpy as np

from .kge import kling_gupta_efficiency

PARAMETER_NAMES = ("Smax", "fr", "k1", "n1", "k2", "n2", "Dmax")

# Returned as the KGE when a parameter set produces a constant or undefined
# simulation. It is far below any realistic KGE, so the optimiser avoids it.
PENALTY_KGE = -10.0


@dataclass(frozen=True)
class SimulationResult:
    """Model output and goodness-of-fit metrics for one simulation."""

    qsurf: np.ndarray  # surface runoff
    qsim: np.ndarray   # underdrain flow (drainage-store outflow)
    et: np.ndarray     # evapotranspiration
    ssoil: np.ndarray  # soil-store state
    ssto: np.ndarray   # drainage-store state
    rmse: float
    nse: float
    kge: float


def run_model(params, precipitation, pet):
    """Run the storage model over one time series.

    Parameters
    ----------
    params : sequence of 7 floats
        ``(Smax, fr, k1, n1, k2, n2, Dmax)``, in the order of PARAMETER_NAMES.
        Smax is the soil storage capacity, fr the fraction of rainfall that
        becomes surface runoff when the soil is full, k1 and n1 control
        percolation to the drainage store, k2 and n2 control underdrain outflow,
        and Dmax is the drainage-store threshold above which outflow occurs.
    precipitation, pet : 1-D arrays
        Rainfall and potential evapotranspiration, same length and time step.

    Returns
    -------
    tuple of 5 arrays
        ``(qsurf, qsim, et, ssoil, ssto)``.
    """
    Smax, fr, k1, n1, k2, n2, Dmax = params
    n = len(precipitation)

    ssoil = np.zeros(n)
    qsurf = np.zeros(n)
    ssto = np.zeros(n)
    qsim = np.zeros(n)
    per_sto = np.zeros(n)
    et = np.zeros(n)

    for i in range(1, n):
        rain = precipitation[i]

        # Evapotranspiration, limited by soil moisture and never negative
        et[i] = max(min(ssoil[i - 1] / Smax, 1) * pet[i], 0)

        # Soil moisture update, never negative
        ssoil[i] = max(ssoil[i - 1] + rain - et[i], 0)

        # Surface runoff when the soil is full
        if ssoil[i] > Smax:
            qsurf[i] = max(rain * fr, 0)
            ssoil[i] -= qsurf[i]
        else:
            qsurf[i] = 0

        # Percolation from the soil store to the drainage store
        if ssoil[i] > Smax:
            excess_soil = ssoil[i] - Smax
            per_sto[i] = k1 * excess_soil ** n1
            ssoil[i] -= per_sto[i]
        else:
            per_sto[i] = 0

        # Underdrain outflow from the drainage store
        excess_storage = max(ssto[i - 1] - Dmax, 0)
        qsim[i] = k2 * excess_storage ** n2

        # Drainage-store update, never negative
        ssto[i] = ssto[i - 1] + per_sto[i] - qsim[i]
        if ssto[i] < 0:
            qsim[i] = 0
            ssto[i] = 0

    return qsurf, qsim, et, ssoil, ssto


def GR_sim(params, precipitation, pet, qobs):
    """Simulate one period and report RMSE, NSE and KGE against ``qobs``."""
    qsurf, qsim, et, ssoil, ssto = run_model(params, precipitation, pet)

    residual = qsim - qobs
    rmse = np.sqrt(np.mean(residual ** 2))
    nse = 1 - np.sum(residual ** 2) / np.sum((qobs - np.mean(qobs)) ** 2)
    kge = kling_gupta_efficiency(qsim, qobs)

    return SimulationResult(qsurf, qsim, et, ssoil, ssto, rmse, nse, kge)


def GR_opt(params, precipitation, pet, qobs):
    """Return the KGE of a parameter set, for use as an optimisation objective.

    Returns PENALTY_KGE when the simulation is constant or the KGE is not
    finite, so the optimiser treats the parameter set as very poor.
    """
    _, qsim, _, _, _ = run_model(params, precipitation, pet)

    if np.std(qsim) == 0:
        return PENALTY_KGE

    kge = kling_gupta_efficiency(qsim, qobs)
    if not np.isfinite(kge):
        return PENALTY_KGE
    return kge
