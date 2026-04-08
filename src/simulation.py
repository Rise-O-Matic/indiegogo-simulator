"""Monte Carlo simulation engine for crowdfunding campaigns."""

from dataclasses import dataclass, field
import numpy as np
from src.config import CloakConfig, CampaignConfig, FeeStructure
from src.ucurve import generate_ucurve_weights
from src.funnel import total_daily_backers
from src.revenue import calculate_revenue


@dataclass
class SimulationInputs:
    """User-configurable audience inputs."""
    email_list: int = 0
    ig_followers: int = 0
    fb_followers: int = 0
    daily_ad_budget: float = 0.0
    pr_hits: int = 0
    cloak: CloakConfig = field(default_factory=CloakConfig)
    campaign: CampaignConfig = field(default_factory=CampaignConfig)
    fees: FeeStructure = field(default_factory=FeeStructure)


@dataclass
class SimulationResults:
    """Aggregated results from N simulation runs."""
    total_raised: np.ndarray
    total_backers: np.ndarray
    net_revenue: np.ndarray
    funded: np.ndarray
    daily_trajectories: np.ndarray
    goal: float

    def probability_of_funding(self) -> float:
        return float(np.mean(self.funded))

    def percentiles(self, pcts: list[int]) -> np.ndarray:
        return np.percentile(self.total_raised, pcts)

    def trajectory_percentiles(self, pcts: list[int]) -> np.ndarray:
        return np.percentile(self.daily_trajectories, pcts, axis=0)


def run_simulation(inputs: SimulationInputs, n_runs: int = 10_000, seed: int = 42) -> SimulationResults:
    rng = np.random.default_rng(seed)
    duration = inputs.campaign.duration_days
    weights = generate_ucurve_weights(duration)

    all_raised = np.zeros(n_runs)
    all_backers = np.zeros(n_runs, dtype=int)
    all_net = np.zeros(n_runs)
    all_funded = np.zeros(n_runs, dtype=bool)
    all_trajectories = np.zeros((n_runs, duration))

    for i in range(n_runs):
        daily_backers = total_daily_backers(
            email_list=inputs.email_list,
            ig_followers=inputs.ig_followers,
            fb_followers=inputs.fb_followers,
            daily_ad_budget=inputs.daily_ad_budget,
            pr_hits=inputs.pr_hits,
            duration_days=duration,
            weights=weights,
            rng=rng,
        )
        rev = calculate_revenue(daily_backers, inputs.cloak, inputs.fees,
                                max_fulfillment_days=inputs.campaign.max_fulfillment_days)
        all_raised[i] = rev["gross_revenue"]
        all_backers[i] = rev["total_backers"]
        all_net[i] = rev["net_revenue"]
        all_funded[i] = rev["gross_revenue"] >= inputs.campaign.goal
        all_trajectories[i] = rev["daily_cumulative_revenue"]

    return SimulationResults(
        total_raised=all_raised,
        total_backers=all_backers,
        net_revenue=all_net,
        funded=all_funded,
        daily_trajectories=all_trajectories,
        goal=inputs.campaign.goal,
    )
