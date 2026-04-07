import numpy as np
from src.revenue import calculate_revenue
from src.config import CloakConfig, FeeStructure


def test_all_early_bird():
    """When backers < early_bird_quantity, all get early bird price."""
    cloak = CloakConfig(early_bird_quantity=50)
    result = calculate_revenue(
        daily_backers=np.array([10, 5, 3]),
        cloak=cloak,
        fees=FeeStructure(),
    )
    assert result["total_backers"] == 18
    assert result["gross_revenue"] == 18 * 149.99


def test_mixed_early_bird_and_standard():
    """When backers exceed early_bird_quantity, overflow pays standard."""
    cloak = CloakConfig(early_bird_quantity=10)
    result = calculate_revenue(
        daily_backers=np.array([8, 5, 7]),
        cloak=cloak,
        fees=FeeStructure(),
    )
    assert result["total_backers"] == 20
    expected_gross = 10 * 149.99 + 10 * 179.99
    assert abs(result["gross_revenue"] - expected_gross) < 0.01


def test_net_revenue_deducts_all_costs():
    cloak = CloakConfig(early_bird_quantity=100, cogs_per_unit=40, shipping_per_unit=10)
    fees = FeeStructure()
    result = calculate_revenue(
        daily_backers=np.array([50]),
        cloak=cloak,
        fees=fees,
    )
    gross = result["gross_revenue"]
    expected_fees = fees.calculate_fees(gross, 50)
    expected_net = gross - expected_fees - (50 * 40) - (50 * 10)
    assert abs(result["net_revenue"] - expected_net) < 0.01


def test_zero_backers():
    result = calculate_revenue(
        daily_backers=np.array([0, 0, 0]),
        cloak=CloakConfig(),
        fees=FeeStructure(),
    )
    assert result["total_backers"] == 0
    assert result["gross_revenue"] == 0.0
    assert result["net_revenue"] == 0.0
