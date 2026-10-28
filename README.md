# bgi_model

A conceptual storage model for runoff from blue-green infrastructure (BGI). The model has a soil store and a drainage store. It is calibrated to the underdrain flow at Oslo by maximising the Kling-Gupta efficiency (KGE) with SLSQP from several random starting points.

## Installation

You need Python 3.10 or later.

```bash
git clone https://github.com/prabhatjoshi007/bgi_model.git
cd bgi_model
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

## Data

The data files are not in this repository. See [`data/README.md`](data/README.md) for the file names, the columns used and where to get them. Place the two files in `data/`, or pass another folder with `--data-dir`.

## Usage

Calibrate the model and check it on the validation period:

```bash
python scripts/run_calibration.py --runs 20 --seed 42
```

| Option | Default | Meaning |
|---|---|---|
| `--runs` | 10 | Number of SLSQP runs from different starting points |
| `--seed` | 42 | Seed for the starting points. The same seed gives the same results. |
| `--data-dir` | `data/` | Folder with the Oslo data files |
| `--output-dir` | `outputs/` | Folder for tables and figures |
| `--cal-length` | 100000 | Calibration length in 5-minute samples |
| `--show-plots` | off | Show figures on screen as well as saving them |

The model is a pure Python loop, so each calibration run takes about a minute at the default calibration length. Use `--cal-length` for quick tests.

### Outputs

| File | Contents |
|---|---|
| `calibration_runs.csv` | Every run with its parameters and KGE, best first |
| `best_run_metrics.csv` | KGE, NSE and RMSE for the best run in the calibration and validation periods |
| `parameter_correlation.csv`, `variance_inflation.csv` | Collinearity checks between the calibrated parameters. The VIF table needs more than 8 runs. |
| `calibration_*.png`, `validation_*.png` | Hydrographs, cumulative volumes, fluxes and water balance |
| `parameter_values.png`, `parameter_correlation.png` | Parameter spread across runs, and the correlation heatmap |

## Model

Parameters are in the order used throughout the code:

| Name | Bounds | Meaning |
|---|---|---|
| `Smax` | 0.01 to 30 | Soil storage capacity |
| `fr` | 0.001 to 0.010 | Fraction of rainfall that becomes surface runoff when the soil is full |
| `k1`, `n1` | 0 to 1, 1 to 3 | Coefficient and exponent for percolation from the soil store to the drainage store |
| `k2`, `n2` | 0 to 1, 1 to 3 | Coefficient and exponent for underdrain outflow |
| `Dmax` | 0 to 25 | Drainage-store threshold above which underdrain outflow occurs |

### Input alignment

Rainfall and underdrain flow are smoothed with a 10-sample moving average. The smoothed value is centred about 4.5 samples (about 22 minutes) later than the raw record. PET is shifted by 5 samples to match. This leaves a residual offset of half a sample. Change `PET_SHIFT` in `src/bgi_model/data.py` if you prefer another alignment.

### Calibration and validation periods

- Calibration: 100,000 samples starting at sample 2000.
- Validation: 20,000 samples, starting 2,000 samples after the end of calibration.

Both periods use the same parameter set, the best calibration run.

### Known limitations

- The model clamps soil and drainage storage at zero, so the water balance does not close exactly. The calibration output reports the residual.
- The optimiser works from random starting points. More runs give more confidence in the best parameter set but take longer.
- Parameter bounds were chosen for the Oslo catchment. Check them before applying the model elsewhere.

## Repository layout

```
bgi_model/
├── src/bgi_model/     # the importable package
│   ├── model.py       # storage model, GR_sim and GR_opt
│   ├── calibration.py # multi-start SLSQP calibration
│   ├── data.py        # loading and aligning the input series
│   ├── kge.py         # Kling-Gupta efficiency
│   ├── diagnostics.py # parameter tables, correlation, VIF, water balance
│   └── plots.py       # figures
├── scripts/
│   └── run_calibration.py
├── data/              # see data/README.md; data files are not tracked
├── pyproject.toml
├── requirements.txt
└── CITATION.cff
```

## Citation

If you use this code, please cite it using [`CITATION.cff`](CITATION.cff). Citation details for the associated paper: TBD.

## Licence

TBD

## Contact

Prabhat Joshi, Prabhat.joshi@protonmail.com
