"""Addressable market sizing for CLOAK."""
from dataclasses import dataclass

@dataclass
class MarketEstimate:
    value: int | float
    unit: str
    source: str
    tier: int
    notes: str = ""

US_GUN_OWNERS = MarketEstimate(82_000_000, "people", "Pew Research / ATF estimates, 2024", 1, "~32% of US adults")
SAFE_OWNERSHIP_RATE = MarketEstimate(0.45, "ratio", "AFSA industry estimates", 2, "~45% of gun owners have a safe")
ELECTRONIC_KEYPAD_RATE = MarketEstimate(0.65, "ratio", "Industry trend data, major brands", 2, "~65% of new safes use electronic locks")
ANNUAL_NEW_SAFE_SALES = MarketEstimate(2_500_000, "units/year", "AFSA, firearms industry reports", 2)
ADDRESSABLE_SAFE_OWNERS = MarketEstimate(int(82_000_000 * 0.45 * 0.65), "people", "Derived: gun owners * safe rate * electronic keypad rate", 2, "~24M electronic keypad safe owners in US")
META_TARGETABLE_AUDIENCE = MarketEstimate(5_000_000, "people", "Estimated from Facebook Ads Manager interest targeting", 3, "Needs validation with Ads Manager")
MONTHLY_SEARCH_VOLUME = MarketEstimate(500, "searches/month", "Estimated; needs validation via Google Keyword Planner", 3)

def saturation_check(required_audience: int, channel: str) -> dict:
    addressable = META_TARGETABLE_AUDIENCE.value
    capture_rate = required_audience / addressable if addressable > 0 else float("inf")
    if capture_rate < 0.01: feasibility = "Easy"
    elif capture_rate < 0.05: feasibility = "Achievable"
    elif capture_rate < 0.15: feasibility = "Ambitious"
    elif capture_rate < 0.30: feasibility = "Very ambitious"
    else: feasibility = "Unrealistic"
    return {"addressable": addressable, "required": required_audience, "capture_rate": capture_rate, "feasibility": feasibility}
