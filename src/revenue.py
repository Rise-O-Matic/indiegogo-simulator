"""Revenue calculations for IndieGoGo campaigns.

Handles early bird / standard perk allocation, fee deduction, COGS, and shipping.
Confidence tier: Tier 1 (fee structure is documented by IndieGoGo).
"""

import numpy as np
from src.config import CloakConfig, FeeStructure


def calculate_revenue(
    daily_backers: np.ndarray,
    cloak: CloakConfig,
    fees: FeeStructure,
    max_fulfillment_days: int = 90,
) -> dict:
    """Calculate revenue from a sequence of daily backer counts.

    Early bird perks are allocated chronologically: first N backers get
    early_bird_price, remainder pay standard_price. If total backers
    exceed production capacity within max_fulfillment_days, excess
    backers are capped (campaign would close or stop accepting orders).

    Args:
        daily_backers: Array of backer counts per day.
        cloak: Product config with prices, costs, and units_per_day.
        fees: Fee structure for the platform.
        max_fulfillment_days: Max acceptable days to fulfill all orders.

    Returns:
        Dict with: total_backers, early_bird_backers, standard_backers,
        gross_revenue, total_fees, net_revenue, daily_cumulative_revenue,
        fulfillment_days, capped.
    """
    max_units = cloak.units_per_day * max_fulfillment_days
    raw_backers = int(np.sum(daily_backers))
    capped = raw_backers > max_units
    total_backers = min(raw_backers, max_units)

    if total_backers == 0:
        return {
            "total_backers": 0,
            "early_bird_backers": 0,
            "standard_backers": 0,
            "gross_revenue": 0.0,
            "total_fees": 0.0,
            "net_revenue": 0.0,
            "daily_cumulative_revenue": np.zeros(len(daily_backers)),
            "fulfillment_days": 0,
            "capped": False,
        }

    early_bird_backers = min(total_backers, cloak.early_bird_quantity)
    standard_backers = total_backers - early_bird_backers

    gross_revenue = (
        early_bird_backers * cloak.early_bird_price
        + standard_backers * cloak.standard_price
    )

    total_fees = fees.calculate_fees(gross_revenue, total_backers)
    cogs = total_backers * cloak.cogs_per_unit
    shipping = total_backers * cloak.shipping_per_unit
    net_revenue = gross_revenue - total_fees - cogs - shipping

    # Build daily cumulative revenue
    cumulative_backers = np.cumsum(daily_backers)
    daily_revenue = np.zeros(len(daily_backers))
    for i, day_backers in enumerate(daily_backers):
        if day_backers == 0:
            continue
        cum_before = int(cumulative_backers[i] - day_backers)
        cum_after = int(cumulative_backers[i])
        eb_in_day = max(0, min(cum_after, cloak.early_bird_quantity) - max(cum_before, 0))
        eb_in_day = min(eb_in_day, int(day_backers))
        std_in_day = int(day_backers) - eb_in_day
        daily_revenue[i] = eb_in_day * cloak.early_bird_price + std_in_day * cloak.standard_price

    fulfillment_days = (
        int(np.ceil(total_backers / cloak.units_per_day))
        if cloak.units_per_day > 0 else 0
    )

    return {
        "total_backers": total_backers,
        "early_bird_backers": early_bird_backers,
        "standard_backers": standard_backers,
        "gross_revenue": gross_revenue,
        "total_fees": total_fees,
        "net_revenue": net_revenue,
        "daily_cumulative_revenue": np.cumsum(daily_revenue),
        "fulfillment_days": fulfillment_days,
        "capped": capped,
    }
