"""CLOAK campaign configuration and IndieGoGo fee structure."""

from dataclasses import dataclass, field


@dataclass
class CloakConfig:
    """CLOAK product constants."""
    standard_price: float = 200.00
    early_bird_price: float = 149.99
    early_bird_quantity: int = 50
    cogs_per_unit: float = 45.0
    shipping_per_unit: float = 12.0


@dataclass
class CampaignConfig:
    """IndieGoGo campaign parameters."""
    goal: float = 15_000.0
    duration_days: int = 30
    category: str = "Technology"


@dataclass
class FeeStructure:
    """IndieGoGo fee structure (post-Gamefound, Oct 2025)."""
    platform_rate: float = 0.05
    processing_rate: float = 0.03
    per_txn_fee: float = 0.20

    def calculate_fees(self, gross_revenue: float, num_backers: int) -> float:
        """Total fees deducted by IndieGoGo + payment processor."""
        return (
            gross_revenue * self.platform_rate
            + gross_revenue * self.processing_rate
            + num_backers * self.per_txn_fee
        )

    def net_revenue(
        self,
        gross_revenue: float,
        num_backers: int,
        cogs_per_unit: float,
        shipping_per_unit: float,
    ) -> float:
        """Net revenue after fees, COGS, and shipping."""
        fees = self.calculate_fees(gross_revenue, num_backers)
        cogs = num_backers * cogs_per_unit
        shipping = num_backers * shipping_per_unit
        return gross_revenue - fees - cogs - shipping
