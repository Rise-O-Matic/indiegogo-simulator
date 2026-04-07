"""Conversion rate distributions for each traffic source.

Each distribution is tagged with a confidence tier:
- Tier 1: Research-backed (Kickstarter data, academic studies)
- Tier 2: Comparable-inferred (IGG comparables, Meta first-party data)
- Tier 3: Assumed/estimated (CLOAK-specific, wide bands)

All rates use Beta distributions (bounded 0-1).
All counts use LogNormal distributions (positive, right-skewed).
"""

from dataclasses import dataclass
from scipy import stats


@dataclass
class DistParam:
    """A distribution parameter with its confidence tier."""
    dist: stats.rv_continuous
    tier: int
    source: str


# --- Email funnel ---
EMAIL_OPEN_RATE = DistParam(stats.beta(a=20, b=80), tier=1, source="Mailchimp benchmarks ~20%")
EMAIL_CTR = DistParam(stats.beta(a=3, b=97), tier=1, source="Mailchimp benchmarks ~3%")
EMAIL_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=47), tier=3, source="Estimated ~6% of page visitors back")

# --- Social (Instagram) ---
IG_REACH_RATE = DistParam(stats.beta(a=5, b=95), tier=2, source="Meta data: ~5% organic reach per post")
IG_CTR = DistParam(stats.beta(a=2, b=98), tier=2, source="Meta data: ~2% CTR estimate")
IG_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% social visitor backs")

# --- Social (Facebook) ---
FB_REACH_RATE = DistParam(stats.beta(a=3, b=97), tier=2, source="Meta data: ~3% organic reach")
FB_CTR = DistParam(stats.beta(a=1, b=99), tier=2, source="Meta data: ~1% link click rate")
FB_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% social visitor backs")

# --- Paid ads ---
AD_CPM = DistParam(stats.lognorm(s=0.4, scale=12.0), tier=1, source="Meta Ads ~$12 CPM physical products")
AD_CTR = DistParam(stats.beta(a=1.5, b=98.5), tier=1, source="Meta Ads ~1.5% CTR physical products")
AD_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% ad visitor backs")

# --- PR / media ---
PR_REACH_PER_HIT = DistParam(stats.lognorm(s=1.0, scale=5000), tier=3, source="Estimated 5K median reach per article")
PR_CTR = DistParam(stats.beta(a=0.5, b=99.5), tier=3, source="Estimated ~0.5% CTR from press")
PR_PAGE_TO_BACKER = DistParam(stats.beta(a=2, b=98), tier=3, source="Estimated ~2% press visitor backs (warm)")

# --- Website traffic ---
SITE_CAMPAIGN_MULTIPLIER = DistParam(stats.lognorm(s=0.3, scale=1.5), tier=3, source="Estimated 1.5x traffic during campaign")
SITE_TO_IGG_CTR = DistParam(stats.beta(a=5, b=95), tier=3, source="Estimated ~5% site-to-IGG click-through")
SITE_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=97), tier=3, source="Estimated ~3% warm visitor backs")

# --- IGG organic ---
IGG_DAILY_CATEGORY_VISITORS = DistParam(
    stats.lognorm(s=0.5, scale=50), tier=2,
    source="IGG ~5M monthly, Technology ~1%, niche fraction"
)
IGG_PAGE_TO_BACKER = DistParam(stats.beta(a=2, b=98), tier=2, source="IGG organic visitor ~2% conversion")

# --- Word of mouth ---
WOM_TELLS = DistParam(stats.lognorm(s=0.5, scale=2.0), tier=3, source="Each backer tells ~2 people")
WOM_VISIT_RATE = DistParam(stats.beta(a=10, b=90), tier=3, source="~10% of told people visit")
WOM_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=97), tier=3, source="~3% WOM visitor backs (warm referral)")
