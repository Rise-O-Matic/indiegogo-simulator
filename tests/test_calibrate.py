"""Tests for the calibration module (pack/unpack roundtrip, loss computation)."""

import math
import numpy as np
import pytest
from src.calibrate import (
    pack_params, unpack_params, patch_distributions, compute_loss,
    extract_targets, PARAM_REGISTRY, NDIM, _logit, _sigmoid,
    _beta_mean, _beta_concentration, INPUT_PRESETS,
)
from src import distributions as D


def test_param_count():
    assert NDIM == 20


def test_pack_unpack_roundtrip():
    x = pack_params()
    assert x.shape == (NDIM,)
    params = unpack_params(x)
    # Verify roundtrip preserves means
    for i, spec in enumerate(PARAM_REGISTRY):
        p = params[spec.attr]
        if p["type"] == "beta":
            original_mean = _beta_mean(getattr(D, spec.attr))
            recovered_mean = p["a"] / (p["a"] + p["b"])
            assert abs(original_mean - recovered_mean) < 1e-6, f"{spec.name} mean mismatch"
        else:
            original_scale = getattr(D, spec.attr).dist.kwds.get("scale", 1.0)
            assert abs(original_scale - p["scale"]) < 1e-4, f"{spec.name} scale mismatch"


def test_logit_sigmoid_inverse():
    for p in [0.01, 0.1, 0.25, 0.5, 0.75, 0.99]:
        assert abs(_sigmoid(_logit(p)) - p) < 1e-6


def test_patch_distributions_changes_values():
    original_mean = _beta_mean(D.EMAIL_OPEN_RATE)
    x = pack_params()
    # Perturb first param (EMAIL_OPEN_RATE)
    x[0] += 0.5
    params = unpack_params(x)
    patch_distributions(params)
    new_mean = _beta_mean(D.EMAIL_OPEN_RATE)
    assert new_mean != original_mean
    # Restore
    x[0] -= 0.5
    params = unpack_params(x)
    patch_distributions(params)
    restored_mean = _beta_mean(D.EMAIL_OPEN_RATE)
    assert abs(restored_mean - original_mean) < 1e-6


def test_extract_targets_structure():
    targets = extract_targets()
    assert "success_rate" in targets
    assert 0 < targets["success_rate"] < 1
    for pct in [10, 25, 50, 75, 90]:
        assert f"backers_p{pct}" in targets
        assert f"revenue_p{pct}" in targets
        assert targets[f"backers_p{pct}"] > 0
        assert targets[f"revenue_p{pct}"] > 0
    # Percentiles should be monotonically increasing
    for metric in ["backers", "revenue"]:
        vals = [targets[f"{metric}_p{p}"] for p in [10, 25, 50, 75, 90]]
        assert vals == sorted(vals)


def test_loss_is_finite():
    targets = extract_targets()
    x = pack_params()
    loss = compute_loss(x, targets, n_runs=100, n_trials=1)
    assert np.isfinite(loss)
    assert loss > 0


def test_input_presets_valid():
    assert len(INPUT_PRESETS) == 3
    for name, inputs in INPUT_PRESETS.items():
        assert inputs.campaign.goal == 15000.0
        assert inputs.campaign.duration_days == 30
