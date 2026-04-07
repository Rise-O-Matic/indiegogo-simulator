"""U-shaped crowdfunding funding curve.

Research shows campaigns follow a U-shape: ~33% of traffic in first 48 hours,
~33% in the middle (gradual decay), ~33% in the final 48 hours (deadline urgency).
Sources: Multiple academic studies on Kickstarter/IndieGoGo funding dynamics.
Confidence tier: Tier 1 (research-backed, large-N studies).
"""

import numpy as np


def generate_ucurve_weights(duration_days: int) -> np.ndarray:
    """Generate daily traffic weights that follow the U-shaped funding curve.

    Args:
        duration_days: Total campaign duration in days.

    Returns:
        Array of length duration_days, summing to 1.0. Higher values at
        the beginning and end, lower in the middle.
    """
    days = np.arange(duration_days, dtype=float)

    # Launch burst: exponential decay from day 0
    launch_burst = np.exp(-days / 2.0)

    # Deadline surge: exponential growth toward final day
    days_remaining = duration_days - 1 - days
    deadline_surge = np.exp(-days_remaining / 2.0)

    # Baseline: constant low-level activity throughout
    baseline = np.ones(duration_days) * 0.1

    # Combine
    raw = launch_burst + deadline_surge + baseline

    # Normalize to sum to 1.0
    weights = raw / np.sum(raw)

    return weights
