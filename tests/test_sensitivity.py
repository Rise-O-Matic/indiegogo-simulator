from src.sensitivity import tornado_analysis
from src.simulation import SimulationInputs


def test_tornado_returns_all_channels():
    inputs = SimulationInputs(email_list=500, ig_followers=200, daily_ad_budget=50.0)
    result = tornado_analysis(inputs, n_runs=100, seed=42)
    assert "email_list" in result
    assert "ig_followers" in result
    assert "daily_ad_budget" in result


def test_tornado_has_low_high_impact():
    inputs = SimulationInputs(email_list=500)
    result = tornado_analysis(inputs, n_runs=100, seed=42)
    for channel, data in result.items():
        assert "low_revenue" in data
        assert "high_revenue" in data
        assert "impact" in data
        assert data["impact"] >= 0


def test_tornado_sorted_by_impact():
    inputs = SimulationInputs(email_list=500, daily_ad_budget=100.0)
    result = tornado_analysis(inputs, n_runs=100, seed=42)
    impacts = [v["impact"] for v in result.values()]
    assert impacts == sorted(impacts, reverse=True)
