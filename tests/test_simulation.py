import numpy as np
from src.simulation import run_simulation, SimulationInputs, SimulationResults
from src.config import CloakConfig, CampaignConfig, FeeStructure


def test_simulation_output_shape():
    inputs = SimulationInputs(
        email_list=500,
        ig_followers=100,
        fb_followers=50,
        daily_ad_budget=50.0,
        pr_hits=1,
        monthly_site_visitors=200,
    )
    results = run_simulation(inputs, n_runs=100, seed=42)
    assert isinstance(results, SimulationResults)
    assert len(results.total_raised) == 100
    assert len(results.total_backers) == 100
    assert len(results.funded) == 100
    assert results.daily_trajectories.shape == (100, 30)


def test_simulation_funded_is_boolean():
    inputs = SimulationInputs(email_list=500)
    results = run_simulation(inputs, n_runs=50, seed=42)
    assert results.funded.dtype == bool


def test_simulation_probability_between_0_and_1():
    inputs = SimulationInputs(email_list=500)
    results = run_simulation(inputs, n_runs=100, seed=42)
    prob = results.probability_of_funding()
    assert 0.0 <= prob <= 1.0


def test_simulation_percentiles():
    inputs = SimulationInputs(email_list=1000, daily_ad_budget=100.0)
    results = run_simulation(inputs, n_runs=200, seed=42)
    p10, p50, p90 = results.percentiles([10, 50, 90])
    assert p10 <= p50 <= p90


def test_simulation_zero_inputs_low_funding():
    inputs = SimulationInputs()
    results = run_simulation(inputs, n_runs=100, seed=42)
    assert np.median(results.total_raised) < 5000


def test_simulation_trajectories_monotonic():
    inputs = SimulationInputs(email_list=500)
    results = run_simulation(inputs, n_runs=50, seed=42)
    for traj in results.daily_trajectories:
        diffs = np.diff(traj)
        assert np.all(diffs >= 0)
