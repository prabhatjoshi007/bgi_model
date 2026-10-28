"""Loading and aligning the Oslo rainfall, underdrain flow and PET series."""

from pathlib import Path

import numpy as np

OSLO_FILE = "OsloData_5min.txt"
PET_FILE = "Oslo_PET_5min.txt"

# Rainfall and underdrain flow are smoothed with a 10-sample moving average
# ('valid' mode), which shifts their centre about 4.5 samples later than the
# raw record. PET is shifted by the same amount so each PET value lines up
# with the centre of its rainfall window.
MOVING_AVERAGE_WINDOW = 10
PET_SHIFT = 5

# Column indices in the raw files (the first column is the timestamp).
OSLO_PRECIPITATION_COLUMN = 1
OSLO_UNDERDRAIN_COLUMN = 3
PET_COLUMN = 1


def moving_average(data, window_size):
    """Return the moving average of ``data`` over ``window_size`` samples."""
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


def load_oslo_data(data_dir):
    """Load rainfall, PET and underdrain flow for the Oslo catchment.

    Returns
    -------
    precipitation, pet, qobs : 1-D arrays of equal length
        Smoothed rainfall, aligned PET, and smoothed underdrain flow (observed).
    """
    data_dir = Path(data_dir)

    precipitation_raw, qobs_raw = np.genfromtxt(
        data_dir / OSLO_FILE,
        delimiter=",",
        skip_header=1,
        usecols=(OSLO_PRECIPITATION_COLUMN, OSLO_UNDERDRAIN_COLUMN),
        unpack=True,
    )
    pet_raw = np.genfromtxt(
        data_dir / PET_FILE,
        delimiter=",",
        skip_header=1,
        usecols=PET_COLUMN,
    )

    precipitation = moving_average(precipitation_raw, MOVING_AVERAGE_WINDOW)
    qobs = moving_average(qobs_raw, MOVING_AVERAGE_WINDOW)
    n = len(precipitation)
    pet = pet_raw[PET_SHIFT:PET_SHIFT + n]

    if len(pet) != n:
        raise ValueError(
            f"PET file is too short: needs {PET_SHIFT + n} rows, has {len(pet_raw)}."
        )
    for name, series in (("precipitation", precipitation), ("PET", pet), ("underdrain flow", qobs)):
        if np.isnan(series).any():
            raise ValueError(f"The {name} series contains missing values.")

    return precipitation, pet, qobs
