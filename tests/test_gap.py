from src.gap import find_required_value, gap_analysis
from src.simulation import SimulationInputs


def test_find_required_email_list():
    base_inputs = SimulationInputs(ig_followers=100, fb_followers=50, daily_ad_budget=50.0)
    required, reached = find_required_value(
        base_inputs=base_inputs,
        param_name="email_list",
        target_probability=0.5,
        search_range=(0, 20_000),
        n_runs=200,
        seed=42,
    )
    assert isinstance(required, int)
    assert 0 <= required <= 20_000
    assert isinstance(reached, bool)


def test_gap_analysis_returns_all_channels():
    inputs = SimulationInputs()
    result = gap_analysis(inputs, target_probability=0.5, n_runs=100, seed=42)
    assert "email_list" in result
    assert "ig_followers" in result
    assert "daily_ad_budget" in result
    for channel, data in result.items():
        assert "you_have" in data
        assert "you_need" in data
        assert "delta" in data
