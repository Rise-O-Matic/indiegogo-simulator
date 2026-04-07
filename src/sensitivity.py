"""Sensitivity analysis for tornado charts."""

from dataclasses import replace
from collections import OrderedDict
import numpy as np
from src.simulation import SimulationInputs, run_simulation

SENSITIVITY_RANGES = {
    "email_list": (0, 5000),
    "ig_followers": (0, 5000),
    "fb_followers": (0, 2000),
    "daily_ad_budget": (0.0, 500.0),
    "pr_hits": (0, 5),
    "monthly_site_visitors": (0, 5000),
}


def tornado_analysis(inputs, n_runs=500, seed=42):
    results = {}
    for channel, (lo, hi) in SENSITIVITY_RANGES.items():
        low_inputs = replace(inputs, **{channel: lo})
        low_results = run_simulation(low_inputs, n_runs=n_runs, seed=seed)
        low_revenue = float(np.median(low_results.total_raised))

        high_inputs = replace(inputs, **{channel: hi})
        high_results = run_simulation(high_inputs, n_runs=n_runs, seed=seed)
        high_revenue = float(np.median(high_results.total_raised))

        results[channel] = {
            "low_value": lo,
            "high_value": hi,
            "low_revenue": low_revenue,
            "high_revenue": high_revenue,
            "impact": abs(high_revenue - low_revenue),
        }

    return OrderedDict(sorted(results.items(), key=lambda x: x[1]["impact"], reverse=True))
