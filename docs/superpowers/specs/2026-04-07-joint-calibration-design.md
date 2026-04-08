# Joint Distribution Calibration via CMA-ES

## Problem

The simulator's 23 distribution parameters (conversion rates, reach rates, etc.) were
hand-tuned against Kickstarter historical data. Hand-tuning is epistatic: changing one
rate shifts the optimal value of every other rate. We need to fit all parameters jointly
against the historical output distribution.

## Approach

Port the CMA-ES black-box optimization pattern from `github/duniverse/tools/nn/cmaes_optimize.py`.
CMA-ES is ideal because the simulator is stochastic and non-differentiable.

## Parameter Vector (21D)

18 Beta distribution means (logit-encoded) + 5 LogNormal scales (log-encoded) = 23D.

Beta concentrations (`a+b`) and LogNormal spreads (`s`) are held fixed -- they encode
uncertainty width, which is a separate concern from central tendency.

### Encoding

| Type | Raw domain | Encoding | Decode |
|------|-----------|----------|--------|
| Beta mean | (0, 1) | logit: `log(p/(1-p))` | sigmoid: `1/(1+exp(-x))` |
| LogNormal scale | (0, inf) | log: `log(scale)` | exp: `exp(x)` |

### Parameter list

| Index | Name | Type | Current mean | Tier |
|-------|------|------|-------------|------|
| 0 | EMAIL_OPEN_RATE | Beta mean | 0.25 | 1 |
| 1 | EMAIL_CTR | Beta mean | 0.10 | 1 |
| 2 | EMAIL_PAGE_TO_BACKER | Beta mean | 0.20 | 1 |
| 3 | IG_REACH_RATE | Beta mean | 0.07 | 2 |
| 4 | IG_CTR | Beta mean | 0.03 | 2 |
| 5 | IG_PAGE_TO_BACKER | Beta mean | 0.05 | 2 |
| 6 | FB_REACH_RATE | Beta mean | 0.05 | 2 |
| 7 | FB_CTR | Beta mean | 0.02 | 2 |
| 8 | FB_PAGE_TO_BACKER | Beta mean | 0.05 | 2 |
| 9 | AD_CTR | Beta mean | 0.015 | 1 |
| 10 | AD_PAGE_TO_BACKER | Beta mean | 0.02 | 2 |
| 11 | PR_CTR | Beta mean | 0.01 | 3 |
| 12 | PR_PAGE_TO_BACKER | Beta mean | 0.03 | 3 |
| 13 | SITE_TO_IGG_CTR | Beta mean | 0.08 | 3 |
| 14 | SITE_PAGE_TO_BACKER | Beta mean | 0.05 | 3 |
| 15 | IGG_PAGE_TO_BACKER | Beta mean | 0.03 | 2 |
| 16 | WOM_VISIT_RATE | Beta mean | 0.15 | 3 |
| 17 | WOM_PAGE_TO_BACKER | Beta mean | 0.05 | 3 |
| 18 | AD_CPM (scale) | LogNorm scale | 12.0 | 1 |
| 19 | PR_REACH_PER_HIT (scale) | LogNorm scale | 8000 | 3 |
| 20 | SITE_CAMPAIGN_MULTIPLIER (scale) | LogNorm scale | 2.0 | 3 |
| 21 | IGG_DAILY_VISITORS (scale) | LogNorm scale | 120 | 2 |
| 22 | WOM_TELLS (scale) | LogNorm scale | 3.0 | 3 |

## Input Presets

Three campaign profiles that the optimizer must satisfy simultaneously:

| Preset | Email | IG | FB | Ads/day | PR | Site/mo | Goal |
|--------|------:|---:|---:|--------:|---:|--------:|-----:|
| Small (bootstrapper) | 200 | 50 | 30 | $0 | 0 | 100 | $15K |
| Medium (typical niche HW) | 1000 | 500 | 200 | $15 | 3 | 500 | $15K |
| CLOAK (actual) | 500 | 124 | 69 | $10 | 2 | 300 | $15K |

## Calibration Targets

Extracted from Kickstarter dataset (Technology/Design, $10-25K goal, $100-250 avg pledge,
N~2414 campaigns):

| Metric | P10 | P25 | P50 | P75 | P90 | Weight |
|--------|-----|-----|-----|-----|-----|--------|
| Backers | -- | -- | -- | -- | -- | 1.0 each |
| Revenue ($) | -- | -- | -- | -- | -- | 1.0 each |
| Success rate | -- | -- | 52% | -- | -- | 3.0 |

Exact percentile values to be extracted from the CSV at calibration time by
`extract_targets()`.

## Loss Function

```
loss = 0
for preset in [small, medium, cloak]:
    results = run_simulation(preset, n_runs=500)
    for metric in [backers, revenue]:
        for pct in [10, 25, 50, 75, 90]:
            sim_val = percentile(results.metric, pct)
            target = targets[metric][pct]
            loss += weight * ((sim_val - target) / target) ** 2
    sim_success = mean(results.funded)
    loss += 3.0 * ((sim_success - target_success) / target_success) ** 2

# Average over 3 presets
loss /= 3

# Average over 3 stochastic trials
total_loss = mean([loss_trial_1, loss_trial_2, loss_trial_3])
```

Relative squared error normalizes backer counts (~100s) and revenue (~$10Ks) onto the
same scale.

## CMA-ES Configuration

- **Initial sigma:** 0.3 (in encoded space)
- **Warm start:** Current hand-tuned values from distributions.py
- **Max evaluations:** 2000
- **Population size:** Default (CMA-ES auto-selects ~14 for 23D)
- **Parallelism:** Not needed at ~2s/eval; sequential is fine
- **Termination:** Loss < 0.01, or max evals, or CMA-ES internal convergence

## Evaluation Cost

- 500 MC runs x 3 presets x 3 trials = 4,500 sim runs per evaluation
- ~0.5ms per sim run = ~2.3s per evaluation
- 2000 evals x 2.3s = ~77 minutes worst case
- Typical convergence at 500-1000 evals = 20-40 minutes

## Output

1. **Console progress:** Eval count, current loss, best loss, best success rate per preset
2. **Best parameters:** Written to `data/calibrated-params.json`
3. **Loss history:** Written to `data/calibration-history.json`
4. **Apply command:** `python -m src.calibrate --apply` rewrites distributions.py
   with optimized values (backs up original first)

## Module: `src/calibrate.py`

### Public API

```python
def extract_targets(ks_csv_path: str) -> dict:
    """Load KS data, filter comparables, compute target percentiles."""

def pack_params() -> np.ndarray:
    """Read current distributions.py values, encode to 23D vector."""

def unpack_params(x: np.ndarray) -> dict:
    """Decode 23D vector to {param_name: (a, b)} or {param_name: (s, scale)}."""

def patch_distributions(params: dict):
    """Monkey-patch distributions module with new DistParam values."""

def objective(x: np.ndarray, targets: dict, n_runs: int, n_trials: int) -> float:
    """Single CMA-ES evaluation: unpack, simulate, compute loss."""

def run_calibration(
    ks_csv_path: str,
    n_runs: int = 500,
    n_trials: int = 3,
    max_evals: int = 2000,
    sigma0: float = 0.3,
) -> tuple[np.ndarray, float]:
    """Main entry: extract targets, warm-start CMA-ES, optimize, save results."""
```

### CLI

```bash
# Run calibration
python -m src.calibrate data/kickstarter/ks-projects-201801.csv

# Apply best params to distributions.py
python -m src.calibrate --apply data/calibrated-params.json
```

## What This Does NOT Do

- Does not optimize Beta concentrations or LogNormal spreads (those encode uncertainty)
- Does not use gradient-based optimization (sim is not differentiable)
- Does not require GPU
- Does not change the simulation engine, funnel logic, or revenue model
- Does not replace the web app or notebook -- just calibrates the underlying parameters
