import numpy as np
from src.funnel import (
    email_traffic,
    social_traffic,
    paid_ads_traffic,
    pr_traffic,
    website_traffic,
    igg_organic_traffic,
    word_of_mouth_traffic,
    total_daily_backers,
)
from src.ucurve import generate_ucurve_weights


def test_email_traffic_shape():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    backers = email_traffic(list_size=1000, duration_days=30, weights=weights, rng=rng)
    assert len(backers) == 30
    assert np.all(backers >= 0)
    assert np.sum(backers) > 0


def test_email_zero_list():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    backers = email_traffic(list_size=0, duration_days=30, weights=weights, rng=rng)
    assert np.sum(backers) == 0


def test_social_traffic_shape():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    backers = social_traffic(
        ig_followers=124, fb_followers=69, duration_days=30, weights=weights, rng=rng
    )
    assert len(backers) == 30
    assert np.all(backers >= 0)


def test_paid_ads_traffic_shape():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    backers = paid_ads_traffic(
        daily_budget=50.0, duration_days=30, weights=weights, rng=rng
    )
    assert len(backers) == 30
    assert np.all(backers >= 0)


def test_paid_ads_zero_budget():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    backers = paid_ads_traffic(
        daily_budget=0.0, duration_days=30, weights=weights, rng=rng
    )
    assert np.sum(backers) == 0


def test_total_daily_backers_combines_sources():
    rng = np.random.default_rng(42)
    weights = generate_ucurve_weights(30)
    result = total_daily_backers(
        email_list=1000,
        ig_followers=500,
        fb_followers=200,
        daily_ad_budget=100.0,
        pr_hits=2,
        monthly_site_visitors=500,
        duration_days=30,
        weights=weights,
        rng=rng,
    )
    assert len(result) == 30
    assert np.all(result >= 0)
    assert np.sum(result) > 0
