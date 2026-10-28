"""Kling-Gupta efficiency (KGE)."""

import numpy as np


def kling_gupta_efficiency(simulated, observed):
    """Return the Kling-Gupta efficiency of ``simulated`` against ``observed``.

    KGE = 1 - sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2), where r is the
    Pearson correlation, alpha the ratio of standard deviations and beta the
    ratio of means. A value of 1 means a perfect match.

    If ``simulated`` is constant, its standard deviation is zero and the
    correlation is undefined, so the result is NaN. Callers that optimise over
    the result should check for this.

    Raises
    ------
    ValueError
        If an input contains NaN or infinity, or if the mean or standard
        deviation of ``observed`` is zero.
    """
    simulated = np.asarray(simulated, dtype=float)
    observed = np.asarray(observed, dtype=float)

    if np.any(np.isnan(simulated)) or np.any(np.isnan(observed)):
        raise ValueError("Input data contains NaN values.")
    if np.any(np.isinf(simulated)) or np.any(np.isinf(observed)):
        raise ValueError("Input data contains infinite values.")

    mean_observed = np.mean(observed)
    mean_simulated = np.mean(simulated)
    std_observed = np.std(observed)
    std_simulated = np.std(simulated)

    if std_observed == 0 or mean_observed == 0:
        raise ValueError(
            "Standard deviation or mean of observed data is zero, "
            "so KGE is undefined."
        )

    r = np.corrcoef(simulated, observed)[0, 1]
    alpha = std_simulated / std_observed
    beta = mean_simulated / mean_observed

    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
