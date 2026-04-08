"""Joint calibration of all distribution parameters via CMA-ES.

Fits the 23-dimensional parameter vector (18 Beta means + 5 LogNormal scales)
against Kickstarter historical output distributions. Uses logit encoding for
Beta means and log encoding for LogNormal scales, following the duniverse
optimization pattern.

Usage:
    # Run calibration
    python -m src.calibrate

    # Apply saved results to distributions.py
    python -m src.calibrate --apply data/calibrated-params.json
"""

import json
import math
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import cma
import numpy as np
from scipy import stats

from src import distributions as D
from src.config import CloakConfig, CampaignConfig, FeeStructure
from src.data_loader import load_kickstarter, filter_kickstarter_comparables
from src.simulation import SimulationInputs, run_simulation


# ---------------------------------------------------------------------------
# Parameter registry: maps each DistParam to its encoding and position
# ---------------------------------------------------------------------------

@dataclass
class ParamSpec:
    """Describes one optimizable parameter."""
    name: str
    attr: str          # attribute name in distributions module
    encoding: str      # 'logit' for Beta means, 'log' for LogNormal scales
    concentration: float = 0.0  # fixed a+b for Beta params


def _beta_mean(dist_param):
    """Extract mean from a frozen Beta distribution."""
    a = dist_param.dist.kwds.get('a', dist_param.dist.args[0] if dist_param.dist.args else None)
    b = dist_param.dist.kwds.get('b', dist_param.dist.args[1] if len(dist_param.dist.args) > 1 else None)
    return a / (a + b)


def _beta_concentration(dist_param):
    """Extract concentration (a+b) from a frozen Beta distribution."""
    a = dist_param.dist.kwds.get('a', dist_param.dist.args[0] if dist_param.dist.args else None)
    b = dist_param.dist.kwds.get('b', dist_param.dist.args[1] if len(dist_param.dist.args) > 1 else None)
    return a + b


def _lognorm_scale(dist_param):
    """Extract scale from a frozen LogNormal distribution."""
    return dist_param.dist.kwds.get('scale', 1.0)


def _lognorm_s(dist_param):
    """Extract s (shape) from a frozen LogNormal distribution."""
    return dist_param.dist.kwds.get('s', dist_param.dist.args[0] if dist_param.dist.args else None)


# Build the registry from current distributions.py
PARAM_REGISTRY = [
    # Beta means (18)
    ParamSpec("EMAIL_OPEN_RATE", "EMAIL_OPEN_RATE", "logit"),
    ParamSpec("EMAIL_CTR", "EMAIL_CTR", "logit"),
    ParamSpec("EMAIL_PAGE_TO_BACKER", "EMAIL_PAGE_TO_BACKER", "logit"),
    ParamSpec("IG_REACH_RATE", "IG_REACH_RATE", "logit"),
    ParamSpec("IG_CTR", "IG_CTR", "logit"),
    ParamSpec("IG_PAGE_TO_BACKER", "IG_PAGE_TO_BACKER", "logit"),
    ParamSpec("FB_REACH_RATE", "FB_REACH_RATE", "logit"),
    ParamSpec("FB_CTR", "FB_CTR", "logit"),
    ParamSpec("FB_PAGE_TO_BACKER", "FB_PAGE_TO_BACKER", "logit"),
    ParamSpec("AD_CTR", "AD_CTR", "logit"),
    ParamSpec("AD_PAGE_TO_BACKER", "AD_PAGE_TO_BACKER", "logit"),
    ParamSpec("PR_CTR", "PR_CTR", "logit"),
    ParamSpec("PR_PAGE_TO_BACKER", "PR_PAGE_TO_BACKER", "logit"),
    ParamSpec("IGG_PAGE_TO_BACKER", "IGG_PAGE_TO_BACKER", "logit"),
    ParamSpec("WOM_VISIT_RATE", "WOM_VISIT_RATE", "logit"),
    ParamSpec("WOM_PAGE_TO_BACKER", "WOM_PAGE_TO_BACKER", "logit"),
    # LogNormal scales (5)
    ParamSpec("AD_CPM", "AD_CPM", "log"),
    ParamSpec("PR_REACH_PER_HIT", "PR_REACH_PER_HIT", "log"),
    ParamSpec("IGG_DAILY_CATEGORY_VISITORS", "IGG_DAILY_CATEGORY_VISITORS", "log"),
    ParamSpec("WOM_TELLS", "WOM_TELLS", "log"),
]

NDIM = len(PARAM_REGISTRY)  # 23


# ---------------------------------------------------------------------------
# Encoding / decoding (logit space for [0,1], log space for R+)
# ---------------------------------------------------------------------------

def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return math.log(p / (1 - p))


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-np.clip(x, -20, 20)))


def pack_params() -> np.ndarray:
    """Read current distributions.py values, encode to 23D vector."""
    x = np.zeros(NDIM)
    for i, spec in enumerate(PARAM_REGISTRY):
        dp = getattr(D, spec.attr)
        if spec.encoding == "logit":
            mean = _beta_mean(dp)
            spec.concentration = _beta_concentration(dp)
            x[i] = _logit(mean)
        elif spec.encoding == "log":
            scale = _lognorm_scale(dp)
            x[i] = math.log(max(scale, 1e-6))
    return x


def unpack_params(x: np.ndarray) -> dict:
    """Decode 23D vector to {attr_name: frozen_distribution}."""
    params = {}
    for i, spec in enumerate(PARAM_REGISTRY):
        dp = getattr(D, spec.attr)
        if spec.encoding == "logit":
            mean = _sigmoid(x[i])
            conc = _beta_concentration(dp)
            a = mean * conc
            b = (1 - mean) * conc
            a = max(a, 0.01)
            b = max(b, 0.01)
            params[spec.attr] = {
                "type": "beta",
                "a": a,
                "b": b,
                "tier": dp.tier,
                "source": dp.source,
            }
        elif spec.encoding == "log":
            scale = math.exp(x[i])
            s = _lognorm_s(dp)
            params[spec.attr] = {
                "type": "lognorm",
                "s": s,
                "scale": scale,
                "tier": dp.tier,
                "source": dp.source,
            }
    return params


def patch_distributions(params: dict):
    """Monkey-patch the distributions module with new parameter values."""
    for attr_name, p in params.items():
        old = getattr(D, attr_name)
        if p["type"] == "beta":
            new_dist = stats.beta(a=p["a"], b=p["b"])
        else:
            new_dist = stats.lognorm(s=p["s"], scale=p["scale"])
        setattr(D, attr_name, D.DistParam(new_dist, tier=p["tier"], source=p["source"]))


# ---------------------------------------------------------------------------
# Calibration targets from Kickstarter data
# ---------------------------------------------------------------------------

def extract_targets(ks_csv_path: str = None) -> dict:
    """Load KS data, filter comparables, compute target percentiles."""
    df = load_kickstarter(ks_csv_path) if ks_csv_path else load_kickstarter()
    comp = filter_kickstarter_comparables(df)

    successful = comp[comp["state"] == "successful"]
    all_campaigns = comp

    targets = {
        "success_rate": len(successful) / len(all_campaigns),
        "n_campaigns": len(all_campaigns),
        "n_successful": len(successful),
    }

    # Backer percentiles (successful campaigns only -- failed campaigns
    # with 0-5 backers would skew the distribution in ways the simulator
    # can't match, since the sim always runs with some audience)
    for pct in [10, 25, 50, 75, 90]:
        targets[f"backers_p{pct}"] = float(successful["backers"].quantile(pct / 100))

    # Revenue percentiles (successful campaigns only)
    for pct in [10, 25, 50, 75, 90]:
        targets[f"revenue_p{pct}"] = float(successful["usd pledged"].quantile(pct / 100))

    return targets


# ---------------------------------------------------------------------------
# Input presets
# ---------------------------------------------------------------------------

INPUT_PRESETS = {
    "small": SimulationInputs(
        email_list=200, ig_followers=50, fb_followers=30,
        daily_ad_budget=0.0, pr_hits=0,
    ),
    "medium": SimulationInputs(
        email_list=1000, ig_followers=500, fb_followers=200,
        daily_ad_budget=15.0, pr_hits=3,
    ),
    "cloak": SimulationInputs(
        email_list=50, ig_followers=124, fb_followers=69,
        daily_ad_budget=10.0, pr_hits=2,
    ),
}


# ---------------------------------------------------------------------------
# Loss function
# ---------------------------------------------------------------------------

def compute_loss(x: np.ndarray, targets: dict, n_runs: int = 500,
                 n_trials: int = 3, rng_base_seed: int = 0) -> float:
    """Evaluate candidate parameter vector against KS targets.

    Runs the simulation across all 3 presets, averaged over n_trials
    stochastic repetitions. Returns scalar loss (lower = better).
    """
    params = unpack_params(x)
    patch_distributions(params)

    total_loss = 0.0

    for trial in range(n_trials):
        trial_loss = 0.0

        for preset_name, inputs in INPUT_PRESETS.items():
            seed = rng_base_seed + trial * 1000 + hash(preset_name) % 1000
            results = run_simulation(inputs, n_runs=n_runs, seed=seed % (2**31))

            # Success rate (weight 3.0)
            sim_success = results.probability_of_funding()
            target_success = targets["success_rate"]
            if target_success > 0:
                trial_loss += 3.0 * ((sim_success - target_success) / target_success) ** 2

            # Backer percentiles (weight 1.0 each, successful runs only)
            successful_mask = results.funded
            if successful_mask.sum() > 10:
                sim_backers = results.total_backers[successful_mask]
                for pct in [10, 25, 50, 75, 90]:
                    sim_val = np.percentile(sim_backers, pct)
                    target_val = targets[f"backers_p{pct}"]
                    if target_val > 0:
                        trial_loss += 1.0 * ((sim_val - target_val) / target_val) ** 2

                # Revenue percentiles (weight 1.0 each, successful runs only)
                sim_revenue = results.total_raised[successful_mask]
                for pct in [10, 25, 50, 75, 90]:
                    sim_val = np.percentile(sim_revenue, pct)
                    target_val = targets[f"revenue_p{pct}"]
                    if target_val > 0:
                        trial_loss += 1.0 * ((sim_val - target_val) / target_val) ** 2
            else:
                # Penalty for too few successful runs -- means success rate is way off
                trial_loss += 10.0

        trial_loss /= len(INPUT_PRESETS)
        total_loss += trial_loss

    return total_loss / n_trials


# ---------------------------------------------------------------------------
# CMA-ES calibration loop
# ---------------------------------------------------------------------------

def run_calibration(
    ks_csv_path: str = None,
    n_runs: int = 500,
    n_trials: int = 3,
    max_evals: int = 2000,
    sigma0: float = 0.3,
) -> tuple:
    """Run CMA-ES calibration. Returns (best_x, best_loss, history)."""

    print("Extracting Kickstarter targets...")
    targets = extract_targets(ks_csv_path)
    print(f"  Campaigns: {targets['n_campaigns']} total, {targets['n_successful']} successful")
    print(f"  Success rate: {targets['success_rate']:.1%}")
    print(f"  Median backers (successful): {targets['backers_p50']:.0f}")
    print(f"  Median revenue (successful): ${targets['revenue_p50']:,.0f}")
    print()

    # Warm-start from current hand-tuned parameters
    x0 = pack_params()
    print(f"Parameter vector dimension: {len(x0)}")
    print(f"Initial encoded values (first 5): {x0[:5].round(3)}")
    print()

    # Evaluate initial loss
    print("Evaluating initial parameters...")
    initial_loss = compute_loss(x0, targets, n_runs=n_runs, n_trials=n_trials)
    print(f"Initial loss: {initial_loss:.4f}")
    print()

    # CMA-ES options
    opts = cma.CMAOptions()
    opts["maxfevals"] = max_evals
    opts["tolx"] = 1e-6
    opts["tolfun"] = 1e-4
    opts["verb_disp"] = 1
    opts["verb_log"] = 0

    eval_count = 0
    history = {"evals": [], "loss": [], "best_loss": []}

    def objective(x):
        nonlocal eval_count
        eval_count += 1
        loss = compute_loss(x, targets, n_runs=n_runs, n_trials=n_trials,
                            rng_base_seed=eval_count)
        history["evals"].append(eval_count)
        history["loss"].append(loss)
        history["best_loss"].append(min(history["loss"]))

        if eval_count % 10 == 0:
            best = min(history["loss"])
            print(f"  [eval {eval_count:4d}] loss={loss:.4f}  best={best:.4f}")

        return loss

    print(f"Starting CMA-ES (sigma0={sigma0}, max_evals={max_evals})...")
    print(f"Estimated time: {max_evals * n_runs * len(INPUT_PRESETS) * n_trials * 0.0005 / 60:.0f} min worst case")
    print()

    es = cma.CMAEvolutionStrategy(x0, sigma0, opts)
    es.optimize(objective)

    best_x = es.result.xbest
    best_loss = es.result.fbest

    print()
    print(f"Calibration complete after {eval_count} evaluations")
    print(f"Best loss: {best_loss:.4f} (started at {initial_loss:.4f})")

    # Decode and display best parameters
    best_params = unpack_params(best_x)
    print()
    print("Optimized parameters:")
    print(f"{'Name':<35} {'Type':<8} {'Old Mean':>10} {'New Mean':>10} {'Change':>10}")
    print("-" * 78)

    x_initial = pack_params()  # won't be accurate since we patched, but show final
    for i, spec in enumerate(PARAM_REGISTRY):
        p = best_params[spec.attr]
        if p["type"] == "beta":
            new_mean = p["a"] / (p["a"] + p["b"])
            # Get old mean from initial vector
            old_mean = _sigmoid(x0[i])
            change = (new_mean - old_mean) / old_mean * 100
            print(f"  {spec.name:<33} beta    {old_mean:>10.4f} {new_mean:>10.4f} {change:>+9.1f}%")
        else:
            new_scale = p["scale"]
            old_scale = math.exp(x0[i])
            change = (new_scale - old_scale) / old_scale * 100
            print(f"  {spec.name:<33} lognorm {old_scale:>10.2f} {new_scale:>10.2f} {change:>+9.1f}%")

    # Save results
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Save best parameter vector + decoded params
    result = {
        "best_x": best_x.tolist(),
        "best_loss": best_loss,
        "initial_loss": initial_loss,
        "total_evals": eval_count,
        "targets": {k: v for k, v in targets.items() if not k.startswith("n_")},
        "params": {},
    }
    for attr_name, p in best_params.items():
        if p["type"] == "beta":
            result["params"][attr_name] = {"a": p["a"], "b": p["b"]}
        else:
            result["params"][attr_name] = {"s": p["s"], "scale": p["scale"]}

    params_path = data_dir / "calibrated-params.json"
    with open(params_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved best params to {params_path}")

    # Save loss history
    history_path = data_dir / "calibration-history.json"
    with open(history_path, "w") as f:
        json.dump(history, f)
    print(f"Saved loss history to {history_path}")

    return best_x, best_loss, history


# ---------------------------------------------------------------------------
# Apply calibrated params to distributions.py
# ---------------------------------------------------------------------------

def apply_params(json_path: str):
    """Rewrite distributions.py with optimized parameter values."""
    with open(json_path) as f:
        result = json.load(f)

    dist_path = Path(__file__).parent / "distributions.py"

    # Read current file
    content = dist_path.read_text()

    # Back up original
    backup_path = dist_path.with_suffix(".py.bak")
    backup_path.write_text(content)
    print(f"Backed up original to {backup_path}")

    # Replace each parameter
    import re
    for attr_name, p in result["params"].items():
        spec = next(s for s in PARAM_REGISTRY if s.attr == attr_name)

        if "a" in p:
            # Beta distribution -- find and replace the stats.beta(a=..., b=...) call
            old_pattern = re.compile(
                rf'({re.escape(attr_name)}\s*=\s*DistParam\(stats\.beta\()a=[^)]+(\))'
            )
            new_args = f"a={p['a']:.4f}, b={p['b']:.4f}"
            content = old_pattern.sub(rf'\g<1>{new_args}\2', content)
        else:
            # LogNormal distribution
            old_pattern = re.compile(
                rf'({re.escape(attr_name)}\s*=\s*DistParam\(\s*stats\.lognorm\()s=[^)]+(\))'
            )
            new_args = f"s={p['s']:.4f}, scale={p['scale']:.4f}"
            content = old_pattern.sub(rf'\g<1>{new_args}\2', content)

    dist_path.write_text(content)
    print(f"Updated {dist_path}")
    print(f"Loss: {result['initial_loss']:.4f} -> {result['best_loss']:.4f}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--apply" in sys.argv:
        idx = sys.argv.index("--apply")
        json_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "data/calibrated-params.json"
        apply_params(json_path)
    else:
        ks_path = sys.argv[1] if len(sys.argv) > 1 else None
        run_calibration(ks_csv_path=ks_path)
