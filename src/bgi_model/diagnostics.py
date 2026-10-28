"""Tables and checks for calibration results."""

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

from .model import PARAMETER_NAMES


def parameter_table(parameters, kge):
    """Return every calibration run as a table, best run first."""
    table = pd.DataFrame(parameters, columns=PARAMETER_NAMES)
    table.insert(0, "KGE", kge)
    table.insert(0, "rank", np.arange(1, len(kge) + 1))
    return table


def parameter_correlation(parameters):
    """Pearson correlation between calibrated parameters."""
    return pd.DataFrame(parameters, columns=PARAMETER_NAMES).corr()


def variance_inflation(parameters):
    """Variance inflation factor for each parameter, to flag collinearity."""
    X = add_constant(pd.DataFrame(parameters, columns=PARAMETER_NAMES))
    return pd.DataFrame(
        {
            "Feature": X.columns,
            "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
        }
    )


def water_balance_error(precipitation, result):
    """Return rainfall minus all outputs and storage changes, summed over the period.

    The value should be close to zero. The model clamps soil and drainage
    storage at zero, so small non-zero values are expected.
    """
    outflows = np.sum(result.qsurf) + np.sum(result.qsim) + np.sum(result.et)
    storage = result.ssoil[-1] + result.ssto[-1]
    return float(np.sum(precipitation) - outflows - storage)
