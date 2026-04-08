"""Gap analysis: 'You have' vs 'You need' via bisection search."""

from dataclasses import replace
from src.simulation import SimulationInputs, run_simulation


CHANNEL_CONFIGS = {
    "email_list": {"range": (0, 50_000), "difficulty": "Medium", "type": int},
    "ig_followers": {"range": (0, 50_000), "difficulty": "Hard", "type": int},
    "fb_followers": {"range": (0, 50_000), "difficulty": "Hard", "type": int},
    "daily_ad_budget": {"range": (0, 5_000), "difficulty": "Medium ($$)", "type": float},
    "pr_hits": {"range": (0, 20), "difficulty": "Hard", "type": int},
}


def find_required_value(base_inputs, param_name, target_probability, search_range, n_runs=500, seed=42, max_iterations=15):
    lo, hi = search_range
    param_type = type(getattr(base_inputs, param_name))
    best_prob = 0.0

    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        if param_type == int:
            mid = int(mid)
        test_inputs = replace(base_inputs, **{param_name: mid})
        results = run_simulation(test_inputs, n_runs=n_runs, seed=seed)
        prob = results.probability_of_funding()
        best_prob = max(best_prob, prob)
        if prob < target_probability:
            lo = mid
        else:
            hi = mid
        if abs(hi - lo) < 2:
            break

    final_value = param_type(hi)
    # Check if we actually reached the target at the upper bound
    reached = best_prob >= target_probability * 0.9  # within 90% of target
    return final_value, reached


def gap_analysis(inputs, target_probability=0.7, n_runs=300, seed=42):
    results = {}
    for channel, config in CHANNEL_CONFIGS.items():
        current_value = getattr(inputs, channel)
        required, reached = find_required_value(
            base_inputs=inputs,
            param_name=channel,
            target_probability=target_probability,
            search_range=config["range"],
            n_runs=n_runs,
            seed=seed,
        )
        delta = required - current_value if isinstance(current_value, (int, float)) else required
        results[channel] = {
            "you_have": current_value,
            "you_need": required,
            "delta": delta,
            "difficulty": config["difficulty"],
            "reachable": reached,
        }
    return results
