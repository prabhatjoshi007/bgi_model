"""Figures for calibration and validation results."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .model import PARAMETER_NAMES

TIME_LABEL = "Time [5 min]"


def _finish(fig, output_dir, filename, show):
    """Save the figure if an output folder is given, then show or close it."""
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / filename, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_period(period, precipitation, pet, qobs, result, output_dir=None, show=False):
    """Plot hydrographs, cumulative volumes, fluxes and the water balance.

    ``pet`` must be the same window the model was run on, so the flux plot
    shows the PET that went into the simulation.
    """
    slug = period.lower()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax1.plot(precipitation, "k-", label="Rain")
    ax1.set(ylabel="Rainfall [mm]", title=period)
    ax1.legend()
    ax2.plot(qobs, "r-", label="Obs")
    ax2.plot(result.qsim, "b--", label="Sim", linewidth=1)
    ax2.set(xlabel=TIME_LABEL, ylabel="Underdrain flow [mm]")
    ax2.legend()
    fig.tight_layout()
    _finish(fig, output_dir, f"{slug}_hydrograph.png", show)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(np.cumsum(precipitation), "k-", label="Rain")
    ax.plot(np.cumsum(qobs), "r-", label="Obs")
    ax.plot(np.cumsum(result.qsim), "b--", label="Sim")
    ax.set(title=period, ylabel="Cumulative [mm]", xlabel=TIME_LABEL)
    ax.legend()
    fig.tight_layout()
    _finish(fig, output_dir, f"{slug}_cumulative.png", show)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(precipitation, "k-", label="Rain")
    ax.plot(result.qsurf, "g-", label="Surface runoff")
    ax.plot(result.et, "y-", label="ET")
    ax.plot(pet, "b--", label="PET")
    ax.set(title=period, ylabel="[mm]", xlabel=TIME_LABEL)
    ax.legend()
    fig.tight_layout()
    _finish(fig, output_dir, f"{slug}_fluxes.png", show)

    fig, ax = plt.subplots(figsize=(8, 6))
    outflows = np.cumsum(result.qsurf) + np.cumsum(result.qsim) + np.cumsum(result.et)
    ax.plot(np.cumsum(precipitation), "k-", label="Rain")
    ax.plot(outflows + result.ssoil + result.ssto, "g--", label="Outflows and storage")
    ax.set(title=f"{period}: water balance", ylabel="[mm]", xlabel=TIME_LABEL)
    ax.legend()
    fig.tight_layout()
    _finish(fig, output_dir, f"{slug}_water_balance.png", show)


def plot_parameter_values(parameters, lower, upper, output_dir=None, show=False, ncols=2):
    """Plot each calibrated parameter against its rank (best run first)."""
    nrows = int(np.ceil(len(PARAMETER_NAMES) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(8, 2.5 * nrows))
    axes = np.ravel(axes)

    for i, name in enumerate(PARAMETER_NAMES):
        ax = axes[i]
        ax.plot(parameters[:, i], ".", color="#91003f", markersize=0.5)
        pad = 0.05 * (upper[i] - lower[i])
        ax.set_ylim(lower[i] - pad, upper[i] + pad)
        ax.grid(True)
        ax.set(xlabel=f"{name} (rank)", ylabel="Parameter value")

    for ax in axes[len(PARAMETER_NAMES):]:
        ax.set_visible(False)

    fig.tight_layout()
    _finish(fig, output_dir, "parameter_values.png", show)


def plot_correlation_heatmap(correlation, output_dir=None, show=False):
    """Heatmap of the correlation between calibrated parameters."""
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation, annot=True, cmap="coolwarm", linewidths=0.5, ax=ax)
    ax.set_title("Correlation between calibrated parameters")
    fig.tight_layout()
    _finish(fig, output_dir, "parameter_correlation.png", show)
