"""Calibrate the storage model on the Oslo calibration period and check it on the validation period.

Examples
--------
    python scripts/run_calibration.py --runs 20 --seed 42
    python scripts/run_calibration.py --data-dir path/to/data --output-dir results
"""

import argparse
import logging
from pathlib import Path

import pandas as pd

from bgi_model.calibration import LOWER_BOUNDS, UPPER_BOUNDS, calibrate
from bgi_model.data import load_oslo_data
from bgi_model.diagnostics import (
    parameter_correlation,
    parameter_table,
    variance_inflation,
    water_balance_error,
)
from bgi_model.model import GR_sim, PARAMETER_NAMES
from bgi_model.plots import plot_correlation_heatmap, plot_parameter_values, plot_period

REPO_ROOT = Path(__file__).resolve().parents[1]

CAL_START = 2000
CAL_LENGTH = 100_000
VAL_GAP = 2000  # samples between the end of calibration and the start of validation
VAL_LENGTH = 20_000


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=int, default=10, help="number of calibration runs (default: 10)")
    parser.add_argument("--seed", type=int, default=42, help="random seed for starting points (default: 42)")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data", help="folder with the Oslo data files")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "outputs", help="folder for tables and figures")
    parser.add_argument("--cal-length", type=int, default=CAL_LENGTH, help="calibration length in samples")
    parser.add_argument("--show-plots", action="store_true", help="show figures on screen as well as saving them")
    return parser.parse_args(argv)


def metrics_row(period, sim):
    return {"period": period, "KGE": sim.kge, "NSE": sim.nse, "RMSE": sim.rmse}


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    precipitation, pet, qobs = load_oslo_data(args.data_dir)

    cal = slice(CAL_START, CAL_START + args.cal_length)
    val_start = CAL_START + args.cal_length + VAL_GAP
    val = slice(val_start, val_start + VAL_LENGTH)

    result = calibrate(precipitation[cal], pet[cal], qobs[cal], args.runs, args.seed)
    parameter_table(result.parameters, result.kge).to_csv(out / "calibration_runs.csv", index=False)

    cal_sim = GR_sim(result.best, precipitation[cal], pet[cal], qobs[cal])
    val_sim = GR_sim(result.best, precipitation[val], pet[val], qobs[val])

    metrics = pd.DataFrame(
        [metrics_row("Calibration", cal_sim), metrics_row("Validation", val_sim)]
    )
    metrics.to_csv(out / "best_run_metrics.csv", index=False)
    logging.info("\n%s", metrics.to_string(index=False))
    logging.info("Calibration water balance error: %.3f mm", water_balance_error(precipitation[cal], cal_sim))

    correlation = parameter_correlation(result.parameters)
    correlation.to_csv(out / "parameter_correlation.csv")
    # VIF regresses each parameter on the others, so it needs more runs than parameters.
    if len(result.kge) > len(PARAMETER_NAMES) + 1:
        variance_inflation(result.parameters).to_csv(out / "variance_inflation.csv", index=False)
    else:
        logging.info("Skipping variance inflation: needs more than %d runs.", len(PARAMETER_NAMES) + 1)

    plot_period("Calibration", precipitation[cal], pet[cal], qobs[cal], cal_sim, out, args.show_plots)
    plot_period("Validation", precipitation[val], pet[val], qobs[val], val_sim, out, args.show_plots)
    plot_parameter_values(result.parameters, LOWER_BOUNDS, UPPER_BOUNDS, out, args.show_plots)
    plot_correlation_heatmap(correlation, out, args.show_plots)

    logging.info("Results saved to %s", out.resolve())


if __name__ == "__main__":
    main()
