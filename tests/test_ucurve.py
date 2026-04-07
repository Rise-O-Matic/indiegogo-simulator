import numpy as np
from src.ucurve import generate_ucurve_weights


def test_weights_sum_to_one():
    weights = generate_ucurve_weights(30)
    assert abs(np.sum(weights) - 1.0) < 1e-6


def test_weights_length_matches_duration():
    for d in [20, 30, 40, 60]:
        weights = generate_ucurve_weights(d)
        assert len(weights) == d


def test_first_two_days_are_highest():
    weights = generate_ucurve_weights(30)
    mid_avg = np.mean(weights[5:25])
    first_two_avg = np.mean(weights[0:2])
    assert first_two_avg > mid_avg * 2


def test_last_two_days_higher_than_middle():
    weights = generate_ucurve_weights(30)
    mid_avg = np.mean(weights[10:20])
    last_two_avg = np.mean(weights[-2:])
    assert last_two_avg > mid_avg


def test_u_shape_thirds():
    """First 48h, middle, and last 48h should each be roughly 1/3."""
    weights = generate_ucurve_weights(30)
    first_two = np.sum(weights[0:2])
    last_two = np.sum(weights[-2:])
    middle = np.sum(weights[2:-2])
    assert first_two > 0.20
    assert last_two > 0.15
    assert middle > 0.25
