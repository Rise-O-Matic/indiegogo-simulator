# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Monte Carlo crowdfunding campaign simulator for the CLOAK electronic safe keypad shield, targeting an IndieGoGo launch. It models a marketing funnel (audience sources -> page views -> backers -> revenue) with stochastic conversion rates sampled from probability distributions, run 10,000 times to produce confidence intervals on campaign outcomes.

The primary deliverable is `notebooks/cloak-campaign-simulator.ipynb`. The `src/` modules are the engine; the notebook orchestrates them.

## Commands

```bash
# Activate venv (required before all commands)
source .venv/Scripts/activate

# Run all tests
python -m pytest

# Run a single test file
python -m pytest tests/test_simulation.py

# Run a single test
python -m pytest tests/test_simulation.py::test_simulation_output_shape -v

# Install dependencies
pip install -r requirements.txt

# Launch the notebook
jupyter notebook notebooks/cloak-campaign-simulator.ipynb

# Run CMA-ES calibration (requires Kickstarter CSV in data/kickstarter/)
python -m src.calibrate

# Apply saved calibration results to distributions.py
python -m src.calibrate --apply data/calibrated-params.json
```

## Architecture

### Data flow

```
SimulationInputs (audience sizes, budgets)
  -> funnel.py: per-source daily backer counts (Poisson-sampled, U-curve weighted)
  -> revenue.py: early bird allocation, gross/net revenue, daily cumulative trajectory
  -> simulation.py: 10K Monte Carlo runs -> SimulationResults (percentiles, P(funded))
  -> gap.py / sensitivity.py: bisection search and tornado analysis over the simulation
  -> viz.py: matplotlib charts, pandas tables, text scorecards

Kickstarter CSV (data/kickstarter/)
  -> data_loader.py: filter to comparable campaigns
  -> calibrate.py: CMA-ES optimization of 20-dim parameter vector
  -> data/calibrated-params.json -> apply_params() rewrites distributions.py
```

### Module responsibilities

- **config.py** -- Product constants (`CloakConfig`), campaign params (`CampaignConfig`), IndieGoGo fee math (`FeeStructure`)
- **distributions.py** -- All conversion rate distributions as `DistParam` objects (Beta for rates, LogNormal for counts). Each is tagged with a confidence tier (1=research-backed, 2=comparable-inferred, 3=assumed) and source citation
- **ucurve.py** -- Generates daily traffic weights following the U-shaped crowdfunding curve (launch burst + deadline surge)
- **funnel.py** -- Seven independent audience source models (email, IG, FB, paid ads, PR, website, IGG organic) plus word-of-mouth. Each samples conversion rates from distributions and returns Poisson-sampled daily backer counts. `total_daily_backers()` combines all sources
- **revenue.py** -- Converts daily backer arrays into revenue dicts. Early bird perks consumed chronologically
- **simulation.py** -- `run_simulation()` is the Monte Carlo loop. `SimulationInputs` holds all user-configurable params. `SimulationResults` holds all output arrays with helper methods for percentiles and P(funded)
- **gap.py** -- Bisection search: for each audience channel, finds the input value needed to hit a target funding probability
- **sensitivity.py** -- Tornado analysis: varies each input low/high, holds others constant, measures revenue impact
- **market.py** -- Addressable market sizing and saturation feasibility checks
- **demand.py** -- Demand signal scoring (direct/indirect/category) with a validation playbook
- **data_loader.py** -- Loads Kickstarter CSV (gitignored, large) and IGG comparables JSON
- **calibrate.py** -- CMA-ES joint calibration of the 20-dimensional distribution parameter vector (16 Beta means + 4 LogNormal scales) against Kickstarter historical output distributions. Uses logit encoding for Beta means and log encoding for LogNormal scales. Run as `python -m src.calibrate`; apply results with `--apply`.
- **viz.py** -- All visualization: fan charts, tornado charts, gap tables, scorecards, scenario comparisons

### Key design decisions

- All randomness flows through `numpy.random.Generator` (no global state). Seed is passed to `run_simulation()`.
- Conversion rates use scipy.stats distributions (Beta/LogNormal), sampled once per simulation run (not per day).
- Word-of-mouth is the only feedback loop: it reads cumulative backers from other sources and adds referral-driven backers on a one-day lag.
- Gap analysis runs many smaller simulations (n_runs=300-500) via bisection, so it's the slowest operation.
- Calibration (`calibrate.py`) monkey-patches `distributions` module in-place during the optimization loop; `apply_params()` rewrites the `.py` source file with a regex and backs up the original as `distributions.py.bak`.
- The calibrate module docstring says "23-dimensional" but the actual `PARAM_REGISTRY` has 20 entries (16 Beta + 4 LogNormal). The test `test_param_count` asserts `NDIM == 20`.

## Data

- `data/facebook/`, `data/instagram/` -- Raw Meta Business Suite CSVs (first-party social metrics)
- `data/meta-insights-2026-04-07.md` -- Summarized Meta insights for simulator calibration
- `data/kickstarter/` -- Gitignored. Expects `ks-projects-201801.csv` from Kaggle
- `data/igg-comparables.json` -- Manually researched IndieGoGo comparable campaigns (may not exist yet)
- `data/calibrated-params.json` -- Output of `calibrate.py`; best parameter vector + decoded params + loss history
- `data/calibration-history.json` -- Per-eval loss history from CMA-ES run

## Confidence Tier System

Every parameter in `distributions.py` is tagged with a tier:
- **Tier 1:** Research-backed (Kickstarter dataset, Mailchimp benchmarks, academic studies)
- **Tier 2:** Comparable-inferred (IGG comparables, Meta first-party data)
- **Tier 3:** Assumed/estimated (CLOAK-specific, wide uncertainty bands)

When modifying distributions, always preserve the tier tag and source citation.
