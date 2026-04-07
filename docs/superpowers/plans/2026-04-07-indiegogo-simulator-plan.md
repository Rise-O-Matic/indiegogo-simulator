# CLOAK IndieGoGo Campaign Simulator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Jupyter Notebook that uses Monte Carlo simulation over a marketing funnel to project IndieGoGo campaign outcomes for the CLOAK electronic safe keypad shield, with emphasis on gap analysis and risk assessment.

**Architecture:** A set of focused Python modules (`src/`) implement the simulation engine, data loading, revenue model, and analysis functions. A Jupyter notebook (`notebooks/cloak-campaign-simulator.ipynb`) orchestrates these modules across 11 cells: setup, data foundations, market sizing, demand signals, audience inputs, simulation engine, primary outputs, gap analysis, sensitivity analysis, scenario comparison, and recommendations. Tests live in `tests/` and cover all core computation.

**Tech Stack:** Python 3.13, numpy, pandas, scipy.stats, matplotlib, seaborn, plotly, requests, Jupyter

---

## File Structure

```
indiegogo-simulator/
├── data/
│   ├── meta-insights-2026-04-07.md           # (exists) captured Meta Business Suite data
│   ├── kickstarter/                           # Kickstarter CSV (gitignored, too large)
│   │   └── .gitkeep
│   └── igg-comparables.json                   # Manually researched IGG campaigns
├── docs/                                      # (exists) specs and plans
├── src/
│   ├── __init__.py
│   ├── config.py                              # CLOAK constants, campaign defaults, fee structure
│   ├── data_loader.py                         # Load & filter Kickstarter CSV, load comparables
│   ├── distributions.py                       # Conversion rate distributions with confidence tiers
│   ├── ucurve.py                              # U-shaped funding curve time-weighting function
│   ├── funnel.py                              # Audience source models (email, social, ads, etc.)
│   ├── revenue.py                             # Revenue, fees, COGS, net profit calculations
│   ├── simulation.py                          # Monte Carlo engine (vectorized with numpy)
│   ├── market.py                              # Addressable market sizing & saturation checks
│   ├── demand.py                              # Demand signal scoring
│   ├── gap.py                                 # Gap analysis bisection search
│   ├── sensitivity.py                         # Tornado chart sensitivity analysis
│   └── viz.py                                 # All matplotlib/seaborn/plotly chart functions
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_ucurve.py
│   ├── test_funnel.py
│   ├── test_revenue.py
│   ├── test_simulation.py
│   ├── test_gap.py
│   └── test_sensitivity.py
├── notebooks/
│   └── cloak-campaign-simulator.ipynb         # The main deliverable
├── requirements.txt
└── .gitignore
```

**Design notes:**
- Each `src/` module has one clear responsibility and is independently testable.
- The notebook imports from `src/` — it orchestrates and visualizes, it doesn't contain computation logic.
- `data/kickstarter/` is gitignored (CSV is ~55MB). A setup step downloads it.
- `igg-comparables.json` is small enough to commit.

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `data/kickstarter/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```
numpy>=1.26
pandas>=2.1
scipy>=1.11
matplotlib>=3.8
seaborn>=0.13
plotly>=5.18
requests>=2.31
jupyter>=1.0
ipykernel>=6.25
```

- [ ] **Step 2: Create .gitignore**

```
# Python
__pycache__/
*.pyc
*.pyo
.ipynb_checkpoints/

# Data (too large for git)
data/kickstarter/*.csv

# Environment
.venv/
venv/
.env

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Create empty __init__.py files**

Create `src/__init__.py` and `tests/__init__.py` as empty files.

Create `data/kickstarter/.gitkeep` as an empty file.

- [ ] **Step 4: Create virtual environment and install dependencies**

Run:
```bash
cd /c/GitHub/indiegogo-simulator
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Expected: All packages install successfully.

- [ ] **Step 5: Verify imports work**

Run:
```bash
python -c "import numpy, pandas, scipy, matplotlib, seaborn, plotly, requests; print('All imports OK')"
```

Expected: `All imports OK`

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore src/__init__.py tests/__init__.py data/kickstarter/.gitkeep
git commit -m "feat: project scaffolding with dependencies and directory structure"
```

---

## Task 2: Config Module — CLOAK Constants & Campaign Defaults

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from src.config import CloakConfig, CampaignConfig, FeeStructure


def test_cloak_defaults():
    c = CloakConfig()
    assert c.standard_price == 179.99
    assert c.early_bird_price == 149.99
    assert c.early_bird_quantity == 50


def test_campaign_defaults():
    c = CampaignConfig()
    assert c.duration_days == 30
    assert c.goal == 15_000


def test_fee_structure():
    f = FeeStructure()
    assert f.platform_rate == 0.05
    assert f.processing_rate == 0.03
    assert f.per_txn_fee == 0.20


def test_fee_calculation():
    f = FeeStructure()
    gross = 10_000
    backers = 50
    total_fees = f.calculate_fees(gross, backers)
    expected = (10_000 * 0.05) + (10_000 * 0.03) + (50 * 0.20)
    assert total_fees == expected


def test_net_revenue():
    f = FeeStructure()
    gross = 10_000
    backers = 50
    cogs_per_unit = 40.0
    shipping_per_unit = 10.0
    net = f.net_revenue(gross, backers, cogs_per_unit, shipping_per_unit)
    fees = (10_000 * 0.05) + (10_000 * 0.03) + (50 * 0.20)
    cogs = 50 * 40.0
    shipping = 50 * 10.0
    assert net == gross - fees - cogs - shipping
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.config'`

- [ ] **Step 3: Write implementation**

```python
# src/config.py
"""CLOAK campaign configuration and IndieGoGo fee structure."""

from dataclasses import dataclass, field


@dataclass
class CloakConfig:
    """CLOAK product constants."""
    standard_price: float = 179.99
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: config module with CLOAK constants, campaign defaults, fee structure"
```

---

## Task 3: U-Curve Function — Time-Weighted Funding Distribution

**Files:**
- Create: `src/ucurve.py`
- Create: `tests/test_ucurve.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ucurve.py
import numpy as np
from src.ucurve import generate_ucurve_weights


def test_weights_sum_to_one():
    weights = generate_ucurve_weights(30)
    assert abs(np.sum(weights) - 1.0) < 1e-6


def test_weights_length_matches_duration():
    for d in [20, 30, 40, 60]:
        weights = generate_ucurve_weights(d)
        assert len(weights) == d


def test_first_two_days_are_highest():
    weights = generate_ucurve_weights(30)
    mid_avg = np.mean(weights[5:25])
    first_two_avg = np.mean(weights[0:2])
    assert first_two_avg > mid_avg * 2


def test_last_two_days_higher_than_middle():
    weights = generate_ucurve_weights(30)
    mid_avg = np.mean(weights[10:20])
    last_two_avg = np.mean(weights[-2:])
    assert last_two_avg > mid_avg


def test_u_shape_thirds():
    """First 48h, middle, and last 48h should each be roughly 1/3."""
    weights = generate_ucurve_weights(30)
    first_two = np.sum(weights[0:2])
    last_two = np.sum(weights[-2:])
    middle = np.sum(weights[2:-2])
    assert first_two > 0.20  # at least 20%
    assert last_two > 0.15   # at least 15%
    assert middle > 0.25     # at least 25%
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ucurve.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/ucurve.py
"""U-shaped crowdfunding funding curve.

Research shows campaigns follow a U-shape: ~33% of traffic in first 48 hours,
~33% in the middle (gradual decay), ~33% in the final 48 hours (deadline urgency).
Sources: Multiple academic studies on Kickstarter/IndieGoGo funding dynamics.
Confidence tier: Tier 1 (research-backed, large-N studies).
"""

import numpy as np


def generate_ucurve_weights(duration_days: int) -> np.ndarray:
    """Generate daily traffic weights that follow the U-shaped funding curve.

    Args:
        duration_days: Total campaign duration in days.

    Returns:
        Array of length duration_days, summing to 1.0. Higher values at
        the beginning and end, lower in the middle.
    """
    days = np.arange(duration_days, dtype=float)

    # Launch burst: exponential decay from day 0
    # Peak at day 0-1, decaying with half-life of ~2 days
    launch_burst = np.exp(-days / 2.0)

    # Deadline surge: exponential growth toward final day
    # Mirrored: grows as we approach the end
    days_remaining = duration_days - 1 - days
    deadline_surge = np.exp(-days_remaining / 2.0)

    # Baseline: constant low-level activity throughout
    baseline = np.ones(duration_days) * 0.1

    # Combine
    raw = launch_burst + deadline_surge + baseline

    # Normalize to sum to 1.0
    weights = raw / np.sum(raw)

    return weights
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ucurve.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/ucurve.py tests/test_ucurve.py
git commit -m "feat: U-shaped funding curve time-weighting function"
```

---

## Task 4: Revenue Model

**Files:**
- Create: `src/revenue.py`
- Create: `tests/test_revenue.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_revenue.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_revenue.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/revenue.py
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
) -> dict:
    """Calculate revenue from a sequence of daily backer counts.

    Early bird perks are allocated chronologically: first N backers get
    early_bird_price, remainder pay standard_price.

    Args:
        daily_backers: Array of backer counts per day.
        cloak: Product config with prices and costs.
        fees: Fee structure for the platform.

    Returns:
        Dict with: total_backers, early_bird_backers, standard_backers,
        gross_revenue, total_fees, net_revenue, daily_cumulative_revenue.
    """
    total_backers = int(np.sum(daily_backers))

    if total_backers == 0:
        return {
            "total_backers": 0,
            "early_bird_backers": 0,
            "standard_backers": 0,
            "gross_revenue": 0.0,
            "total_fees": 0.0,
            "net_revenue": 0.0,
            "daily_cumulative_revenue": np.zeros(len(daily_backers)),
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

    return {
        "total_backers": total_backers,
        "early_bird_backers": early_bird_backers,
        "standard_backers": standard_backers,
        "gross_revenue": gross_revenue,
        "total_fees": total_fees,
        "net_revenue": net_revenue,
        "daily_cumulative_revenue": np.cumsum(daily_revenue),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_revenue.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/revenue.py tests/test_revenue.py
git commit -m "feat: revenue model with early bird allocation and fee calculations"
```

---

## Task 5: Funnel Model — Audience Source Traffic Generation

**Files:**
- Create: `src/distributions.py`
- Create: `src/funnel.py`
- Create: `tests/test_funnel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_funnel.py
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
    assert np.sum(backers) > 0  # 1000 subscribers should produce some backers


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_funnel.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write distributions module**

```python
# src/distributions.py
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
# Tier 1: Mailchimp industry benchmarks, large-N
EMAIL_OPEN_RATE = DistParam(stats.beta(a=20, b=80), tier=1, source="Mailchimp benchmarks ~20%")
EMAIL_CTR = DistParam(stats.beta(a=3, b=97), tier=1, source="Mailchimp benchmarks ~3%")
# Tier 3: No CLOAK-specific data
EMAIL_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=47), tier=3, source="Estimated ~6% of page visitors back")

# --- Social (Instagram) ---
# Tier 2: Meta first-party data (124 followers, 645 views = ~5.2x views/follower over 28 days)
IG_REACH_RATE = DistParam(stats.beta(a=5, b=95), tier=2, source="Meta data: ~5% organic reach per post")
IG_CTR = DistParam(stats.beta(a=2, b=98), tier=2, source="Meta data: ~2% CTR estimate")
IG_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% social visitor backs")

# --- Social (Facebook) ---
# Tier 2: Meta first-party data (69 followers, 101 views, 1 link click)
FB_REACH_RATE = DistParam(stats.beta(a=3, b=97), tier=2, source="Meta data: ~3% organic reach")
FB_CTR = DistParam(stats.beta(a=1, b=99), tier=2, source="Meta data: ~1% link click rate")
FB_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% social visitor backs")

# --- Paid ads ---
# Tier 1: Meta Ads benchmarks for physical products
AD_CPM = DistParam(stats.lognorm(s=0.4, scale=12.0), tier=1, source="Meta Ads ~$12 CPM physical products")
AD_CTR = DistParam(stats.beta(a=1.5, b=98.5), tier=1, source="Meta Ads ~1.5% CTR physical products")
AD_PAGE_TO_BACKER = DistParam(stats.beta(a=1, b=99), tier=3, source="Estimated ~1% ad visitor backs")

# --- PR / media ---
# Tier 3: High variance, no CLOAK data
PR_REACH_PER_HIT = DistParam(stats.lognorm(s=1.0, scale=5000), tier=3, source="Estimated 5K median reach per article")
PR_CTR = DistParam(stats.beta(a=0.5, b=99.5), tier=3, source="Estimated ~0.5% CTR from press")
PR_PAGE_TO_BACKER = DistParam(stats.beta(a=2, b=98), tier=3, source="Estimated ~2% press visitor backs (warm)")

# --- Website traffic ---
# Tier 3: Negligible current traffic
SITE_CAMPAIGN_MULTIPLIER = DistParam(stats.lognorm(s=0.3, scale=1.5), tier=3, source="Estimated 1.5x traffic during campaign")
SITE_TO_IGG_CTR = DistParam(stats.beta(a=5, b=95), tier=3, source="Estimated ~5% site-to-IGG click-through")
SITE_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=97), tier=3, source="Estimated ~3% warm visitor backs")

# --- IGG organic ---
# Tier 1/2: Derived from platform data (~5M monthly visits)
IGG_DAILY_CATEGORY_VISITORS = DistParam(
    stats.lognorm(s=0.5, scale=50), tier=2,
    source="IGG ~5M monthly, Technology ~1%, niche fraction"
)
IGG_PAGE_TO_BACKER = DistParam(stats.beta(a=2, b=98), tier=2, source="IGG organic visitor ~2% conversion")

# --- Word of mouth ---
# Tier 3: Highly uncertain
WOM_TELLS = DistParam(stats.lognorm(s=0.5, scale=2.0), tier=3, source="Each backer tells ~2 people")
WOM_VISIT_RATE = DistParam(stats.beta(a=10, b=90), tier=3, source="~10% of told people visit")
WOM_PAGE_TO_BACKER = DistParam(stats.beta(a=3, b=97), tier=3, source="~3% WOM visitor backs (warm referral)")
```

- [ ] **Step 4: Write funnel module**

```python
# src/funnel.py
"""Audience source traffic models.

Each function takes audience size inputs + U-curve weights + RNG,
samples conversion rates from distributions, and returns daily backer counts.
"""

import numpy as np
from src import distributions as D


def _sample(dist_param, rng) -> float:
    """Sample a single value from a DistParam's distribution."""
    return float(dist_param.dist.rvs(random_state=rng))


def email_traffic(
    list_size: int,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Email list -> daily backers. Bulk arrives in first 48h."""
    if list_size == 0:
        return np.zeros(duration_days)

    open_rate = _sample(D.EMAIL_OPEN_RATE, rng)
    ctr = _sample(D.EMAIL_CTR, rng)
    page_to_backer = _sample(D.EMAIL_PAGE_TO_BACKER, rng)

    total_page_views = list_size * open_rate * ctr
    total_backers_expected = total_page_views * page_to_backer

    # Email is front-loaded: 80% in first 2 days, 20% trickled
    email_weights = np.copy(weights)
    email_weights[0] *= 5.0
    email_weights[1] *= 3.0
    email_weights /= email_weights.sum()

    expected_daily = total_backers_expected * email_weights
    daily_backers = rng.poisson(np.maximum(expected_daily, 0))
    return daily_backers


def social_traffic(
    ig_followers: int,
    fb_followers: int,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Social media followers -> daily backers."""
    total_backers_expected = 0.0

    if ig_followers > 0:
        ig_reach = ig_followers * _sample(D.IG_REACH_RATE, rng)
        ig_clicks = ig_reach * _sample(D.IG_CTR, rng)
        ig_backers = ig_clicks * _sample(D.IG_PAGE_TO_BACKER, rng)
        total_backers_expected += ig_backers * 6  # ~6 posts during campaign

    if fb_followers > 0:
        fb_reach = fb_followers * _sample(D.FB_REACH_RATE, rng)
        fb_clicks = fb_reach * _sample(D.FB_CTR, rng)
        fb_backers = fb_clicks * _sample(D.FB_PAGE_TO_BACKER, rng)
        total_backers_expected += fb_backers * 6

    if total_backers_expected == 0:
        return np.zeros(duration_days)

    expected_daily = total_backers_expected * weights
    return rng.poisson(np.maximum(expected_daily, 0))


def paid_ads_traffic(
    daily_budget: float,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Paid ads budget -> daily backers."""
    if daily_budget <= 0:
        return np.zeros(duration_days)

    cpm = _sample(D.AD_CPM, rng)
    ctr = _sample(D.AD_CTR, rng)
    page_to_backer = _sample(D.AD_PAGE_TO_BACKER, rng)

    daily_impressions = (daily_budget / cpm) * 1000
    daily_clicks = daily_impressions * ctr
    daily_expected_backers = daily_clicks * page_to_backer

    # Ads run every day, but slightly weighted by U-curve for realism
    ad_weights = 0.5 * np.ones(duration_days) / duration_days + 0.5 * weights
    expected_daily = daily_expected_backers * duration_days * ad_weights

    return rng.poisson(np.maximum(expected_daily, 0))


def pr_traffic(
    num_hits: int,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """PR/media hits -> daily backers."""
    if num_hits <= 0:
        return np.zeros(duration_days)

    total_backers_expected = 0.0
    for _ in range(num_hits):
        reach = _sample(D.PR_REACH_PER_HIT, rng)
        clicks = reach * _sample(D.PR_CTR, rng)
        backers = clicks * _sample(D.PR_PAGE_TO_BACKER, rng)
        total_backers_expected += backers

    # PR clustered in first week
    pr_weights = np.copy(weights)
    pr_weights[:7] *= 3.0
    pr_weights /= pr_weights.sum()

    expected_daily = total_backers_expected * pr_weights
    return rng.poisson(np.maximum(expected_daily, 0))


def website_traffic(
    monthly_visitors: int,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Existing website visitors -> daily backers."""
    if monthly_visitors <= 0:
        return np.zeros(duration_days)

    multiplier = _sample(D.SITE_CAMPAIGN_MULTIPLIER, rng)
    campaign_daily_visitors = (monthly_visitors / 30.0) * multiplier
    ctr = _sample(D.SITE_TO_IGG_CTR, rng)
    page_to_backer = _sample(D.SITE_PAGE_TO_BACKER, rng)

    daily_expected = campaign_daily_visitors * ctr * page_to_backer
    expected_daily = daily_expected * duration_days * weights
    return rng.poisson(np.maximum(expected_daily, 0))


def igg_organic_traffic(
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
    trending_boost: float = 1.0,
) -> np.ndarray:
    """IndieGoGo platform organic discovery -> daily backers."""
    daily_visitors = _sample(D.IGG_DAILY_CATEGORY_VISITORS, rng) * trending_boost
    page_to_backer = _sample(D.IGG_PAGE_TO_BACKER, rng)

    daily_expected = daily_visitors * page_to_backer
    # Organic is relatively flat, slight U-curve influence
    organic_weights = 0.7 * np.ones(duration_days) / duration_days + 0.3 * weights
    expected_daily = daily_expected * duration_days * organic_weights

    return rng.poisson(np.maximum(expected_daily, 0))


def word_of_mouth_traffic(
    cumulative_backers: np.ndarray,
    duration_days: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Word-of-mouth from existing backers -> additional daily backers."""
    tells = _sample(D.WOM_TELLS, rng)
    visit_rate = _sample(D.WOM_VISIT_RATE, rng)
    page_to_backer = _sample(D.WOM_PAGE_TO_BACKER, rng)

    wom_backers = np.zeros(duration_days)
    for day in range(1, duration_days):
        new_referrals = cumulative_backers[day - 1] * tells * visit_rate * page_to_backer
        wom_backers[day] = rng.poisson(max(new_referrals, 0))

    return wom_backers


def total_daily_backers(
    email_list: int,
    ig_followers: int,
    fb_followers: int,
    daily_ad_budget: float,
    pr_hits: int,
    monthly_site_visitors: int,
    duration_days: int,
    weights: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Combine all traffic sources into total daily backer counts."""
    backers = np.zeros(duration_days)

    backers += email_traffic(email_list, duration_days, weights, rng)
    backers += social_traffic(ig_followers, fb_followers, duration_days, weights, rng)
    backers += paid_ads_traffic(daily_ad_budget, duration_days, weights, rng)
    backers += pr_traffic(pr_hits, duration_days, weights, rng)
    backers += website_traffic(monthly_site_visitors, duration_days, weights, rng)
    backers += igg_organic_traffic(duration_days, weights, rng)

    # Word-of-mouth is cumulative, based on backers so far
    cumulative = np.cumsum(backers)
    backers += word_of_mouth_traffic(cumulative, duration_days, rng)

    return backers.astype(int)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_funnel.py -v`
Expected: All 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/distributions.py src/funnel.py tests/test_funnel.py
git commit -m "feat: funnel model with all audience source traffic generators"
```

---

## Task 6: Monte Carlo Simulation Engine

**Files:**
- Create: `src/simulation.py`
- Create: `tests/test_simulation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_simulation.py
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
    assert results.daily_trajectories.shape == (100, 30)  # default 30 days


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
    inputs = SimulationInputs()  # all defaults (zeros)
    results = run_simulation(inputs, n_runs=100, seed=42)
    # With zero audience, most runs should raise very little
    assert np.median(results.total_raised) < 5000


def test_simulation_trajectories_monotonic():
    """Cumulative revenue should never decrease."""
    inputs = SimulationInputs(email_list=500)
    results = run_simulation(inputs, n_runs=50, seed=42)
    for traj in results.daily_trajectories:
        diffs = np.diff(traj)
        assert np.all(diffs >= 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_simulation.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/simulation.py
"""Monte Carlo simulation engine for crowdfunding campaigns.

Runs N simulations, each sampling from conversion rate distributions
and generating a day-by-day funding trajectory through the marketing funnel.
"""

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
    monthly_site_visitors: int = 0
    cloak: CloakConfig = field(default_factory=CloakConfig)
    campaign: CampaignConfig = field(default_factory=CampaignConfig)
    fees: FeeStructure = field(default_factory=FeeStructure)


@dataclass
class SimulationResults:
    """Aggregated results from N simulation runs."""
    total_raised: np.ndarray       # shape: (n_runs,)
    total_backers: np.ndarray      # shape: (n_runs,)
    net_revenue: np.ndarray        # shape: (n_runs,)
    funded: np.ndarray             # shape: (n_runs,) dtype=bool
    daily_trajectories: np.ndarray # shape: (n_runs, duration_days)
    goal: float

    def probability_of_funding(self) -> float:
        return float(np.mean(self.funded))

    def percentiles(self, pcts: list[int]) -> np.ndarray:
        return np.percentile(self.total_raised, pcts)

    def trajectory_percentiles(self, pcts: list[int]) -> np.ndarray:
        """Percentile bands for daily trajectories. Shape: (len(pcts), duration_days)."""
        return np.percentile(self.daily_trajectories, pcts, axis=0)


def run_simulation(
    inputs: SimulationInputs,
    n_runs: int = 10_000,
    seed: int = 42,
) -> SimulationResults:
    """Run Monte Carlo simulation of the crowdfunding campaign.

    Args:
        inputs: Audience sizes and campaign configuration.
        n_runs: Number of simulation runs.
        seed: Random seed for reproducibility.

    Returns:
        SimulationResults with per-run outcomes and trajectories.
    """
    rng = np.random.default_rng(seed)
    duration = inputs.campaign.duration_days
    weights = generate_ucurve_weights(duration)

    all_raised = np.zeros(n_runs)
    all_backers = np.zeros(n_runs, dtype=int)
    all_net = np.zeros(n_runs)
    all_funded = np.zeros(n_runs, dtype=bool)
    all_trajectories = np.zeros((n_runs, duration))

    for i in range(n_runs):
        # Each run gets a fresh sample from all distributions
        daily_backers = total_daily_backers(
            email_list=inputs.email_list,
            ig_followers=inputs.ig_followers,
            fb_followers=inputs.fb_followers,
            daily_ad_budget=inputs.daily_ad_budget,
            pr_hits=inputs.pr_hits,
            monthly_site_visitors=inputs.monthly_site_visitors,
            duration_days=duration,
            weights=weights,
            rng=rng,
        )

        rev = calculate_revenue(daily_backers, inputs.cloak, inputs.fees)

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_simulation.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/simulation.py tests/test_simulation.py
git commit -m "feat: Monte Carlo simulation engine with 10K run support"
```

---

## Task 7: Gap Analysis — Bisection Search

**Files:**
- Create: `src/gap.py`
- Create: `tests/test_gap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gap.py
import numpy as np
from src.gap import find_required_value, gap_analysis
from src.simulation import SimulationInputs


def test_find_required_email_list():
    """Bisection should find an email list size that achieves target funding probability."""
    base_inputs = SimulationInputs(
        ig_followers=100,
        fb_followers=50,
        daily_ad_budget=50.0,
    )
    required = find_required_value(
        base_inputs=base_inputs,
        param_name="email_list",
        target_probability=0.5,
        search_range=(0, 20_000),
        n_runs=200,
        seed=42,
    )
    assert isinstance(required, int)
    assert 0 <= required <= 20_000


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_gap.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/gap.py
"""Gap analysis: 'You have' vs 'You need' via bisection search.

For each audience channel, varies that one input while holding others constant,
and finds the value at which the target funding probability is achieved.
"""

from dataclasses import replace
from src.simulation import SimulationInputs, run_simulation


CHANNEL_CONFIGS = {
    "email_list": {"range": (0, 50_000), "difficulty": "Medium", "type": int},
    "ig_followers": {"range": (0, 50_000), "difficulty": "Hard", "type": int},
    "fb_followers": {"range": (0, 50_000), "difficulty": "Hard", "type": int},
    "daily_ad_budget": {"range": (0, 5_000), "difficulty": "Medium ($$)", "type": float},
    "pr_hits": {"range": (0, 20), "difficulty": "Hard", "type": int},
    "monthly_site_visitors": {"range": (0, 50_000), "difficulty": "Medium", "type": int},
}


def find_required_value(
    base_inputs: SimulationInputs,
    param_name: str,
    target_probability: float,
    search_range: tuple[int | float, int | float],
    n_runs: int = 500,
    seed: int = 42,
    max_iterations: int = 15,
) -> int | float:
    """Bisection search to find the input value that achieves target funding probability.

    Args:
        base_inputs: Current simulation inputs (all other params held constant).
        param_name: Which input to vary (e.g., 'email_list').
        target_probability: Target P(funded), e.g. 0.7.
        search_range: (min, max) to search within.
        n_runs: Runs per evaluation (lower = faster, noisier).
        seed: Random seed.
        max_iterations: Maximum bisection steps.

    Returns:
        The input value at which funding probability crosses the target.
    """
    lo, hi = search_range
    param_type = type(getattr(base_inputs, param_name))

    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        if param_type == int:
            mid = int(mid)

        test_inputs = replace(base_inputs, **{param_name: mid})
        results = run_simulation(test_inputs, n_runs=n_runs, seed=seed)
        prob = results.probability_of_funding()

        if prob < target_probability:
            lo = mid
        else:
            hi = mid

        if abs(hi - lo) < 2:
            break

    return param_type(hi)


def gap_analysis(
    inputs: SimulationInputs,
    target_probability: float = 0.7,
    n_runs: int = 300,
    seed: int = 42,
) -> dict:
    """Run gap analysis across all channels.

    Returns dict of channel -> {you_have, you_need, delta, difficulty}.
    """
    results = {}

    for channel, config in CHANNEL_CONFIGS.items():
        current_value = getattr(inputs, channel)
        required = find_required_value(
            base_inputs=inputs,
            param_name=channel,
            target_probability=target_probability,
            search_range=config["range"],
            n_runs=n_runs,
            seed=seed,
        )
        delta = required - current_value if isinstance(current_value, (int, float)) else required

        results[channel] = {
            "you_have": current_value,
            "you_need": required,
            "delta": delta,
            "difficulty": config["difficulty"],
        }

    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_gap.py -v`
Expected: All 2 tests PASS (note: gap analysis test takes ~30-60 seconds due to bisection)

- [ ] **Step 5: Commit**

```bash
git add src/gap.py tests/test_gap.py
git commit -m "feat: gap analysis with bisection search for required audience sizes"
```

---

## Task 8: Sensitivity Analysis — Tornado Chart Data

**Files:**
- Create: `src/sensitivity.py`
- Create: `tests/test_sensitivity.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sensitivity.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_sensitivity.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/sensitivity.py
"""Sensitivity analysis for tornado charts.

For each input, varies it from a low to high value while holding all others
at their current values. Records the impact on median revenue.
"""

from dataclasses import replace
from collections import OrderedDict
import numpy as np
from src.simulation import SimulationInputs, run_simulation


SENSITIVITY_RANGES = {
    "email_list": (0, 5000),
    "ig_followers": (0, 5000),
    "fb_followers": (0, 2000),
    "daily_ad_budget": (0.0, 500.0),
    "pr_hits": (0, 5),
    "monthly_site_visitors": (0, 5000),
}


def tornado_analysis(
    inputs: SimulationInputs,
    n_runs: int = 500,
    seed: int = 42,
) -> OrderedDict:
    """Run sensitivity analysis across all channels.

    For each channel, sets the input to its low and high range values,
    runs the simulation, and records the median gross revenue.

    Returns:
        OrderedDict sorted by impact (descending). Each entry:
        {low_value, high_value, low_revenue, high_revenue, impact}
    """
    results = {}

    for channel, (lo, hi) in SENSITIVITY_RANGES.items():
        # Low scenario
        low_inputs = replace(inputs, **{channel: lo})
        low_results = run_simulation(low_inputs, n_runs=n_runs, seed=seed)
        low_revenue = float(np.median(low_results.total_raised))

        # High scenario
        high_inputs = replace(inputs, **{channel: hi})
        high_results = run_simulation(high_inputs, n_runs=n_runs, seed=seed)
        high_revenue = float(np.median(high_results.total_raised))

        results[channel] = {
            "low_value": lo,
            "high_value": hi,
            "low_revenue": low_revenue,
            "high_revenue": high_revenue,
            "impact": abs(high_revenue - low_revenue),
        }

    # Sort by impact descending
    sorted_results = OrderedDict(
        sorted(results.items(), key=lambda x: x[1]["impact"], reverse=True)
    )
    return sorted_results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_sensitivity.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/sensitivity.py tests/test_sensitivity.py
git commit -m "feat: sensitivity analysis for tornado chart data generation"
```

---

## Task 9: Market Sizing & Demand Signals

**Files:**
- Create: `src/market.py`
- Create: `src/demand.py`

These are primarily data/narrative modules (not computation-heavy), so they use dataclasses with embedded research rather than heavy testing.

- [ ] **Step 1: Write market sizing module**

```python
# src/market.py
"""Addressable market sizing for CLOAK.

All figures are documented with sources and confidence tiers.
Used as a realism ceiling on simulation gap analysis outputs.
"""

from dataclasses import dataclass


@dataclass
class MarketEstimate:
    """A market size estimate with source attribution."""
    value: int | float
    unit: str
    source: str
    tier: int
    notes: str = ""


# Gun safe market data
US_GUN_OWNERS = MarketEstimate(
    value=82_000_000, unit="people",
    source="Pew Research / ATF estimates, 2024",
    tier=1, notes="~32% of US adults"
)

SAFE_OWNERSHIP_RATE = MarketEstimate(
    value=0.45, unit="ratio",
    source="AFSA industry estimates",
    tier=2, notes="~45% of gun owners have a safe"
)

ELECTRONIC_KEYPAD_RATE = MarketEstimate(
    value=0.65, unit="ratio",
    source="Industry trend data, major brands",
    tier=2, notes="~65% of new safes use electronic locks vs mechanical dials"
)

ANNUAL_NEW_SAFE_SALES = MarketEstimate(
    value=2_500_000, unit="units/year",
    source="AFSA, firearms industry reports",
    tier=2, notes="Includes all types, not just gun safes"
)

# Derived
ADDRESSABLE_SAFE_OWNERS = MarketEstimate(
    value=int(82_000_000 * 0.45 * 0.65), unit="people",
    source="Derived: gun owners * safe rate * electronic keypad rate",
    tier=2, notes="~24M electronic keypad safe owners in US"
)

# Digital reachability
META_TARGETABLE_AUDIENCE = MarketEstimate(
    value=5_000_000, unit="people",
    source="Estimated from Facebook Ads Manager interest targeting",
    tier=3, notes="'Gun safe' + 'home security' interest overlap, needs validation with Ads Manager"
)

MONTHLY_SEARCH_VOLUME = MarketEstimate(
    value=500, unit="searches/month",
    source="Estimated; needs validation via Google Keyword Planner",
    tier=3, notes="Combined: 'safe keypad cover' + 'protect safe keypad' + 'EMP safe protection'"
)


def saturation_check(required_audience: int, channel: str) -> dict:
    """Check if a required audience size is realistic given market constraints.

    Returns dict with: addressable, required, capture_rate, feasibility.
    """
    addressable = META_TARGETABLE_AUDIENCE.value  # default

    capture_rate = required_audience / addressable if addressable > 0 else float("inf")

    if capture_rate < 0.01:
        feasibility = "Easy"
    elif capture_rate < 0.05:
        feasibility = "Achievable"
    elif capture_rate < 0.15:
        feasibility = "Ambitious"
    elif capture_rate < 0.30:
        feasibility = "Very ambitious"
    else:
        feasibility = "Unrealistic"

    return {
        "addressable": addressable,
        "required": required_audience,
        "capture_rate": capture_rate,
        "feasibility": feasibility,
    }
```

- [ ] **Step 2: Write demand signals module**

```python
# src/demand.py
"""Demand signal scoring for CLOAK.

Evaluates available evidence of product-market fit and produces
a composite demand confidence score.
"""

from dataclasses import dataclass


@dataclass
class DemandSignal:
    """A single demand signal with its assessment."""
    name: str
    category: str  # "direct", "indirect", "category"
    value: str
    score: int  # 0-3: 0=no signal, 1=weak, 2=moderate, 3=strong
    source: str
    notes: str = ""


# Current CLOAK demand signals (as of 2026-04-07)
SIGNALS = [
    # Direct
    DemandSignal("Pre-orders / sales", "direct", "1 sale", 0,
                 "Client reported", "One sale total — insufficient to infer demand"),
    DemandSignal("Email list signups", "direct", "0", 0,
                 "Client reported", "No pre-launch email list exists"),
    DemandSignal("IGG pre-launch page", "direct", "Not created", 0,
                 "Client reported", "No IndieGoGo pre-launch page has been set up"),
    DemandSignal("Landing page conversion", "direct", "Unknown", 0,
                 "bosscoversusa.com", "Site exists but no conversion tracking in place"),

    # Indirect
    DemandSignal("Search volume", "indirect", "~500/mo (est.)", 1,
                 "Needs Google Keyword Planner validation",
                 "Combined related terms; low but nonzero"),
    DemandSignal("Forum discussion", "indirect", "Not researched", 1,
                 "Reddit, gun safe forums",
                 "Anecdotal reports of keypad damage exist in forums"),
    DemandSignal("Competitor activity", "indirect", "None", 1,
                 "Market research",
                 "No direct competitors — could mean untapped or nonexistent market"),
    DemandSignal("Adjacent product sales", "indirect", "Moderate", 2,
                 "Amazon, IGG",
                 "Faraday bags, safe dehumidifiers, safe lights sell well"),
    DemandSignal("Ad platform audience size", "indirect", "~5M (est.)", 1,
                 "Needs Facebook Ads Manager validation",
                 "Estimated targetable audience for gun safe + security interests"),

    # Category
    DemandSignal("Gun safe market growth", "category", "Growing", 2,
                 "Industry reports",
                 "Gun safe market growing steadily, driven by legislation and ownership trends"),
    DemandSignal("Electronic keypad trend", "category", "Increasing", 2,
                 "Industry trend data",
                 "New safes increasingly ship with electronic keypads over mechanical dials"),
    DemandSignal("Prepper market growth", "category", "Strong growth", 2,
                 "Market research",
                 "EMP/preparedness market growing, especially post-2020"),
]


def demand_confidence_score() -> dict:
    """Calculate composite demand confidence score.

    Returns:
        Dict with: score (0-36), rating (Weak/Moderate/Strong),
        direct_score, indirect_score, category_score, signals, narrative.
    """
    direct = [s for s in SIGNALS if s.category == "direct"]
    indirect = [s for s in SIGNALS if s.category == "indirect"]
    category = [s for s in SIGNALS if s.category == "category"]

    direct_score = sum(s.score for s in direct)
    indirect_score = sum(s.score for s in indirect)
    category_score = sum(s.score for s in category)
    total = direct_score + indirect_score + category_score
    max_possible = len(SIGNALS) * 3

    if direct_score >= 6:
        rating = "Strong"
        narrative = (
            "Multiple direct demand signals confirm interest. "
            "Simulation results are actionable for campaign planning."
        )
    elif indirect_score >= 6 or total >= 12:
        rating = "Moderate"
        narrative = (
            "Indirect signals suggest a market exists but demand is not validated "
            "with purchases. Simulation results should be read with caution. "
            "Recommend pre-launch validation before committing to a campaign."
        )
    else:
        rating = "Weak"
        narrative = (
            "Minimal demand signals. The simulation models 'what if demand exists?' "
            "scenarios, but the biggest risk is product-market fit, not campaign "
            "mechanics. Strongly recommend completing pre-launch validation steps."
        )

    return {
        "total_score": total,
        "max_possible": max_possible,
        "rating": rating,
        "direct_score": direct_score,
        "indirect_score": indirect_score,
        "category_score": category_score,
        "signals": SIGNALS,
        "narrative": narrative,
    }


VALIDATION_PLAYBOOK = [
    {
        "action": "Create IndieGoGo pre-launch page",
        "cost": "Free",
        "effort": "1 hour",
        "timeline": "Do immediately",
        "impact": "Replaces 'IGG pre-launch page' signal from 0 to 1-3 depending on signups. "
                  "100+ signups in 2 weeks = strong signal.",
    },
    {
        "action": "Run small Facebook ad to landing page ($5-10/day for 2 weeks)",
        "cost": "$70-140",
        "effort": "2 hours setup + monitoring",
        "timeline": "Start within 1 week",
        "impact": "Provides real CTR and signup conversion data. Replaces Tier 3 ad assumptions "
                  "with Tier 1 first-party data. Also builds email list.",
    },
    {
        "action": "Smoke test: 'Buy Now' page capturing email intent",
        "cost": "$200-500 in ads",
        "effort": "4 hours",
        "timeline": "After initial ad test",
        "impact": "Strongest demand signal short of actual sales. If 2%+ of ad clickers "
                  "enter email for 'pre-order notification,' demand is validated.",
    },
    {
        "action": "Post in gun safe forums and subreddits",
        "cost": "Free",
        "effort": "2-3 hours",
        "timeline": "Do immediately",
        "impact": "Qualitative demand signal. Watch for 'where can I buy this?' comments. "
                  "Also builds awareness and potential email signups.",
    },
    {
        "action": "Google Keyword Planner search volume analysis",
        "cost": "Free (with Google Ads account)",
        "effort": "30 minutes",
        "timeline": "Do immediately",
        "impact": "Validates or invalidates the ~500/mo search volume estimate. "
                  "Replaces Tier 3 with Tier 1 for search-driven demand.",
    },
]
```

- [ ] **Step 3: Commit**

```bash
git add src/market.py src/demand.py
git commit -m "feat: market sizing module and demand signal scoring with validation playbook"
```

---

## Task 10: Visualization Functions

**Files:**
- Create: `src/viz.py`

No tests for visualization — these are visual outputs verified by inspection in the notebook.

- [ ] **Step 1: Write visualization module**

```python
# src/viz.py
"""Visualization functions for the CLOAK campaign simulator.

All chart functions return matplotlib Figure objects for notebook rendering.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from collections import OrderedDict

sns.set_theme(style="whitegrid", palette="deep")


def campaign_scorecard(
    prob_funding: float,
    raised_percentiles: dict,
    backer_percentiles: dict,
    median_net_revenue: float,
    demand_rating: str,
    goal: float,
) -> str:
    """Generate a text-based campaign scorecard."""
    lines = [
        "=" * 56,
        f"  CLOAK Campaign Simulation — Results",
        "=" * 56,
        f"  Probability of funding:    {prob_funding:>6.1%}",
        f"  Funding goal:              ${goal:>10,.0f}",
        "-" * 56,
        f"  Expected raised (10th):    ${raised_percentiles[10]:>10,.0f}",
        f"  Expected raised (50th):    ${raised_percentiles[50]:>10,.0f}",
        f"  Expected raised (90th):    ${raised_percentiles[90]:>10,.0f}",
        "-" * 56,
        f"  Expected backers (10th):   {backer_percentiles[10]:>10,.0f}",
        f"  Expected backers (50th):   {backer_percentiles[50]:>10,.0f}",
        f"  Expected backers (90th):   {backer_percentiles[90]:>10,.0f}",
        "-" * 56,
        f"  Net revenue (median):      ${median_net_revenue:>10,.0f}",
        f"  Demand confidence:         {demand_rating:>10s}",
        "=" * 56,
    ]
    return "\n".join(lines)


def funding_trajectory_fan_chart(
    trajectories: np.ndarray,
    goal: float,
    duration_days: int,
) -> plt.Figure:
    """Fan chart showing percentile bands of funding trajectories."""
    fig, ax = plt.subplots(figsize=(12, 6))
    days = np.arange(1, duration_days + 1)

    p10 = np.percentile(trajectories, 10, axis=0)
    p25 = np.percentile(trajectories, 25, axis=0)
    p50 = np.percentile(trajectories, 50, axis=0)
    p75 = np.percentile(trajectories, 75, axis=0)
    p90 = np.percentile(trajectories, 90, axis=0)

    ax.fill_between(days, p10, p90, alpha=0.15, color="steelblue", label="10th–90th")
    ax.fill_between(days, p25, p75, alpha=0.3, color="steelblue", label="25th–75th")
    ax.plot(days, p50, color="steelblue", linewidth=2, label="Median")
    ax.axhline(y=goal, color="red", linestyle="--", linewidth=1.5, label=f"Goal: ${goal:,.0f}")

    ax.set_xlabel("Campaign Day")
    ax.set_ylabel("Cumulative Funds Raised ($)")
    ax.set_title("Funding Trajectory — Monte Carlo Fan Chart")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    return fig


def gap_analysis_table(gap_data: dict, target_pct: int = 70) -> pd.DataFrame:
    """Format gap analysis results as a DataFrame for display."""
    rows = []
    for channel, data in gap_data.items():
        row = {
            "Channel": channel.replace("_", " ").title(),
            "You Have": f"{data['you_have']:,}" if isinstance(data["you_have"], int) else f"${data['you_have']:,.0f}",
            f"You Need ({target_pct}%)": f"{data['you_need']:,}" if isinstance(data["you_need"], int) else f"${data['you_need']:,.0f}",
            "Delta": f"+{data['delta']:,}" if isinstance(data["delta"], int) else f"+${data['delta']:,.0f}",
            "Difficulty": data["difficulty"],
        }
        if "market_check" in data:
            row["Market Check"] = data["market_check"]
        rows.append(row)
    return pd.DataFrame(rows)


def tornado_chart(tornado_data: OrderedDict, baseline_revenue: float) -> plt.Figure:
    """Horizontal tornado chart showing sensitivity of each input."""
    fig, ax = plt.subplots(figsize=(10, 6))

    channels = list(tornado_data.keys())
    low_vals = [tornado_data[c]["low_revenue"] for c in channels]
    high_vals = [tornado_data[c]["high_revenue"] for c in channels]

    y_pos = np.arange(len(channels))

    ax.barh(y_pos, [h - baseline_revenue for h in high_vals],
            left=baseline_revenue, height=0.4, color="steelblue", label="High")
    ax.barh(y_pos, [l - baseline_revenue for l in low_vals],
            left=baseline_revenue, height=0.4, color="lightcoral", label="Low")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([c.replace("_", " ").title() for c in channels])
    ax.axvline(x=baseline_revenue, color="black", linewidth=1)
    ax.set_xlabel("Median Gross Revenue ($)")
    ax.set_title("Sensitivity Analysis — Which Levers Matter Most")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend()
    plt.tight_layout()
    return fig


def demand_signal_dashboard(signals: list, rating: str, narrative: str) -> pd.DataFrame:
    """Format demand signals as a color-coded DataFrame."""
    score_colors = {0: "🔴", 1: "🟡", 2: "🟢", 3: "🟢"}
    rows = []
    for s in signals:
        rows.append({
            "Signal": s.name,
            "Category": s.category.title(),
            "Value": s.value,
            "Strength": score_colors.get(s.score, "⚪"),
            "Source": s.source,
        })
    return pd.DataFrame(rows)


def scenario_comparison_table(scenarios: list[dict]) -> pd.DataFrame:
    """Format scenario comparison as a DataFrame."""
    rows = []
    for s in scenarios:
        rows.append({
            "Scenario": s["name"],
            "Email List": f"{s['inputs'].email_list:,}",
            "Ad Budget": f"${s['inputs'].daily_ad_budget:,.0f}/day",
            "PR Hits": s["inputs"].pr_hits,
            "P(Funded)": f"{s['prob']:.0%}",
            "Expected Raised": f"${s['median_raised']:,.0f}",
            "Net Revenue": f"${s['median_net']:,.0f}",
        })
    return pd.DataFrame(rows)
```

- [ ] **Step 2: Commit**

```bash
git add src/viz.py
git commit -m "feat: visualization functions for scorecard, fan chart, tornado, gap table"
```

---

## Task 11: Kickstarter Data Loader

**Files:**
- Create: `src/data_loader.py`

- [ ] **Step 1: Write data loader module**

```python
# src/data_loader.py
"""Load and filter Kickstarter dataset and IndieGoGo comparables.

The Kickstarter dataset is expected at data/kickstarter/ks-projects-201801.csv
(Kaggle: "Kickstarter Projects" dataset). Download manually or via kaggle CLI:
  kaggle datasets download -d kemical/kickstarter-projects -p data/kickstarter/

The IGG comparables file is at data/igg-comparables.json (manually researched).
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
KS_CSV = DATA_DIR / "kickstarter" / "ks-projects-201801.csv"
IGG_COMPARABLES = DATA_DIR / "igg-comparables.json"


def load_kickstarter(filepath: Path = KS_CSV) -> pd.DataFrame:
    """Load the full Kickstarter dataset."""
    return pd.read_csv(filepath, encoding="latin-1")


def filter_kickstarter_comparables(df: pd.DataFrame) -> pd.DataFrame:
    """Filter Kickstarter data to campaigns comparable to CLOAK.

    Criteria:
    - Category: Technology or Design (closest to home safety/accessories)
    - Goal: $5,000 - $100,000 (reasonable for a physical product)
    - Average pledge: $50 - $500 (CLOAK is $180)
    - State: 'successful' or 'failed' (exclude live, canceled, suspended)
    """
    # Calculate average pledge
    df = df.copy()
    df["avg_pledge"] = df["usd pledged"] / df["backers"].replace(0, np.nan)

    filtered = df[
        (df["main_category"].isin(["Technology", "Design"]))
        & (df["usd_goal_real"].between(5_000, 100_000))
        & (df["avg_pledge"].between(50, 500))
        & (df["state"].isin(["successful", "failed"]))
    ].copy()

    return filtered


def kickstarter_stats(df: pd.DataFrame) -> dict:
    """Derive key statistics from filtered Kickstarter data.

    Returns dict with success_rate, median_backers, median_raised,
    median_goal, avg_pledge_median, duration stats.
    """
    successful = df[df["state"] == "successful"]

    return {
        "total_campaigns": len(df),
        "success_rate": len(successful) / len(df) if len(df) > 0 else 0,
        "median_backers_successful": int(successful["backers"].median()) if len(successful) > 0 else 0,
        "median_raised_successful": float(successful["usd pledged"].median()) if len(successful) > 0 else 0,
        "median_goal": float(df["usd_goal_real"].median()),
        "avg_pledge_median": float(df["avg_pledge"].median()),
        "backers_p10": int(successful["backers"].quantile(0.1)) if len(successful) > 0 else 0,
        "backers_p90": int(successful["backers"].quantile(0.9)) if len(successful) > 0 else 0,
    }


def load_igg_comparables(filepath: Path = IGG_COMPARABLES) -> list[dict]:
    """Load manually researched IndieGoGo comparable campaigns."""
    with open(filepath) as f:
        return json.load(f)


def igg_comparables_stats(comparables: list[dict]) -> dict:
    """Summary statistics from IndieGoGo comparable campaigns."""
    if not comparables:
        return {"count": 0}

    raised = [c["raised"] for c in comparables]
    backers = [c["backers"] for c in comparables]
    goals = [c["goal"] for c in comparables]

    funded = [c for c in comparables if c["raised"] >= c["goal"]]

    return {
        "count": len(comparables),
        "success_rate": len(funded) / len(comparables),
        "median_raised": float(np.median(raised)),
        "median_backers": int(np.median(backers)),
        "median_goal": float(np.median(goals)),
        "min_raised": min(raised),
        "max_raised": max(raised),
    }
```

- [ ] **Step 2: Create IndieGoGo comparables template**

```json
[
  {
    "name": "PLACEHOLDER — Research needed",
    "url": "",
    "category": "Technology",
    "product_type": "Safe accessory / security product",
    "price_point": 0,
    "goal": 0,
    "raised": 0,
    "backers": 0,
    "duration_days": 30,
    "perk_tiers": 0,
    "notes": "Replace with real campaigns. Search IndieGoGo for: Faraday bags, safe accessories, gun safe lights, EMP protection, emergency preparedness gear in $100-300 range."
  }
]
```

Save this as `data/igg-comparables.json`. This template will be populated with real research data during development.

- [ ] **Step 3: Commit**

```bash
git add src/data_loader.py data/igg-comparables.json
git commit -m "feat: Kickstarter data loader with filtering and IGG comparables template"
```

---

## Task 12: Build the Jupyter Notebook

**Files:**
- Create: `notebooks/cloak-campaign-simulator.ipynb`

This is the main deliverable. Each cell maps to the spec's 11-cell structure.

- [ ] **Step 1: Create the notebook with all 11 cells**

Create `notebooks/cloak-campaign-simulator.ipynb` as a Jupyter notebook. The notebook should contain the following cells in order. Each cell is a separate code or markdown cell.

**Cell 1 — Markdown: Title**
```markdown
# CLOAK IndieGoGo Campaign Simulator
**Product:** CLOAK Electronic Safe Keypad Shield — $179.99
**Platform:** IndieGoGo (all-or-nothing, post-Gamefound)
**Method:** Monte Carlo simulation over marketing funnel (10,000 runs)
**Purpose:** Risk assessment, gap analysis, and pre-launch planning
```

**Cell 2 — Code: Setup & Config**
```python
import sys
sys.path.insert(0, '..')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

from src.config import CloakConfig, CampaignConfig, FeeStructure
from src.simulation import SimulationInputs, run_simulation
from src.gap import gap_analysis
from src.sensitivity import tornado_analysis
from src.demand import demand_confidence_score, VALIDATION_PLAYBOOK
from src.market import (
    US_GUN_OWNERS, SAFE_OWNERSHIP_RATE, ELECTRONIC_KEYPAD_RATE,
    ADDRESSABLE_SAFE_OWNERS, META_TARGETABLE_AUDIENCE, saturation_check,
)
from src.data_loader import (
    load_kickstarter, filter_kickstarter_comparables, kickstarter_stats,
    load_igg_comparables, igg_comparables_stats, KS_CSV, IGG_COMPARABLES,
)
from src.viz import (
    campaign_scorecard, funding_trajectory_fan_chart, gap_analysis_table,
    tornado_chart, demand_signal_dashboard, scenario_comparison_table,
)

# === CAMPAIGN CONFIGURATION ===
cloak = CloakConfig(
    standard_price=179.99,
    early_bird_price=149.99,
    early_bird_quantity=50,
    cogs_per_unit=45.00,
    shipping_per_unit=12.00,
)
campaign = CampaignConfig(goal=15_000, duration_days=30)
fees = FeeStructure()

SEED = 42
N_RUNS = 10_000

print(f"CLOAK: ${cloak.standard_price} (early bird: ${cloak.early_bird_price} x {cloak.early_bird_quantity})")
print(f"Campaign: ${campaign.goal:,.0f} goal, {campaign.duration_days} days")
print(f"Fees: {fees.platform_rate:.0%} platform + {fees.processing_rate:.0%} processing + ${fees.per_txn_fee}/txn")
print(f"Simulation: {N_RUNS:,} Monte Carlo runs, seed={SEED}")
```

**Cell 2b — Markdown: Data Foundations Header**
```markdown
## Data Foundations
Kickstarter data (200K+ campaigns) provides the statistical base. Filtered to comparable campaigns, then adjusted for IndieGoGo platform differences. IndieGoGo comparables serve as a validation check.
```

**Cell 2c — Code: Data Foundations**
```python
# Load Kickstarter data (if available)
if KS_CSV.exists():
    ks_raw = load_kickstarter()
    ks_filtered = filter_kickstarter_comparables(ks_raw)
    ks_stats = kickstarter_stats(ks_filtered)

    print(f"=== KICKSTARTER DATA ===")
    print(f"Total campaigns loaded:     {len(ks_raw):>10,}")
    print(f"Comparable campaigns:       {ks_stats['total_campaigns']:>10,}")
    print(f"Success rate (comparable):  {ks_stats['success_rate']:>10.1%}")
    print(f"Median backers (success):   {ks_stats['median_backers_successful']:>10,}")
    print(f"Median raised (success):    ${ks_stats['median_raised_successful']:>10,.0f}")
    print(f"Median goal:                ${ks_stats['median_goal']:>10,.0f}")
    print(f"Median avg pledge:          ${ks_stats['avg_pledge_median']:>10,.2f}")
    print(f"Backers 10th-90th pctl:     {ks_stats['backers_p10']:,} – {ks_stats['backers_p90']:,}")
    print(f"\n[Tier 1: Kickstarter large-N dataset, filtered to Technology/Design, $5K-$100K goal, $50-$500 avg pledge]")
else:
    print("⚠️  Kickstarter CSV not found at data/kickstarter/ks-projects-201801.csv")
    print("   Download from Kaggle: kaggle datasets download -d kemical/kickstarter-projects")
    print("   Simulation will use published benchmark defaults instead.")

# Load IGG comparables
if IGG_COMPARABLES.exists():
    igg_comps = load_igg_comparables()
    igg_stats = igg_comparables_stats(igg_comps)

    print(f"\n=== INDIEGOGO COMPARABLES ===")
    print(f"Campaigns researched:       {igg_stats['count']:>10,}")
    if igg_stats["count"] > 0 and "median_raised" in igg_stats:
        print(f"Success rate:               {igg_stats['success_rate']:>10.1%}")
        print(f"Median raised:              ${igg_stats['median_raised']:>10,.0f}")
        print(f"Median backers:             {igg_stats['median_backers']:>10,}")
        print(f"Range raised:               ${igg_stats['min_raised']:,.0f} – ${igg_stats['max_raised']:,.0f}")
    print(f"\n[Tier 2: Manually researched comparable IGG campaigns]")
else:
    print("\n⚠️  IGG comparables file not found. Run Task 13 (research) first.")
```

**Cell 3 — Markdown: Market Sizing Header**
```markdown
## Market Sizing — Realism Ceiling
The addressable market sets the upper bound on what's achievable. These numbers constrain the gap analysis: if the simulator says "you need X," the market check tells you whether X is realistic.
```

**Cell 4 — Code: Market Sizing**
```python
print("=== ADDRESSABLE MARKET ===\n")
print(f"US gun owners:              {US_GUN_OWNERS.value:>14,}  [{US_GUN_OWNERS.source}]")
print(f"Safe ownership rate:        {SAFE_OWNERSHIP_RATE.value:>14.0%}  [{SAFE_OWNERSHIP_RATE.source}]")
print(f"Electronic keypad rate:     {ELECTRONIC_KEYPAD_RATE.value:>14.0%}  [{ELECTRONIC_KEYPAD_RATE.source}]")
print(f"─" * 60)
print(f"Addressable safe owners:    {ADDRESSABLE_SAFE_OWNERS.value:>14,}  [Tier {ADDRESSABLE_SAFE_OWNERS.tier}]")
print(f"Meta targetable audience:   {META_TARGETABLE_AUDIENCE.value:>14,}  [Tier {META_TARGETABLE_AUDIENCE.tier}]")
print(f"\nNote: Meta audience estimate needs validation via Facebook Ads Manager.")
```

**Cell 5 — Markdown: Demand Signals Header**
```markdown
## Demand Signal Analysis — Go/No-Go Gate
Before the simulation matters, we need to assess whether there's evidence anyone wants this product. This section scores available demand signals honestly.
```

**Cell 6 — Code: Demand Signals**
```python
demand = demand_confidence_score()

print(f"=== DEMAND CONFIDENCE: {demand['rating'].upper()} ===\n")
print(f"Score: {demand['total_score']}/{demand['max_possible']}")
print(f"  Direct signals:   {demand['direct_score']}/12")
print(f"  Indirect signals: {demand['indirect_score']}/15")
print(f"  Category signals: {demand['category_score']}/9")
print(f"\n{demand['narrative']}\n")

print("─" * 60)
display(demand_signal_dashboard(demand["signals"], demand["rating"], demand["narrative"]))

print("\n=== PRE-LAUNCH VALIDATION PLAYBOOK ===\n")
for i, step in enumerate(VALIDATION_PLAYBOOK, 1):
    print(f"{i}. {step['action']}")
    print(f"   Cost: {step['cost']} | Effort: {step['effort']} | When: {step['timeline']}")
    print(f"   Impact: {step['impact']}\n")
```

**Cell 7 — Markdown: Audience Inputs Header**
```markdown
## Audience Inputs — What You Have
Change these values to match the CLOAK team's current state, then re-run the notebook.
```

**Cell 8 — Code: Audience Inputs + Simulation**
```python
# === CHANGE THESE VALUES ===
inputs = SimulationInputs(
    email_list=0,              # Pre-launch email subscribers
    ig_followers=124,          # Instagram followers (from Meta data)
    fb_followers=69,           # Facebook followers (from Meta data)
    daily_ad_budget=0.0,       # Daily paid ads budget ($)
    pr_hits=0,                 # Expected press/media articles
    monthly_site_visitors=100, # Monthly unique visitors to bosscoversusa.com
    cloak=cloak,
    campaign=campaign,
    fees=fees,
)

print("Running simulation...")
results = run_simulation(inputs, n_runs=N_RUNS, seed=SEED)

prob = results.probability_of_funding()
raised_pcts = {p: float(results.percentiles([p])[0]) for p in [10, 50, 90]}
backer_pcts = {p: float(np.percentile(results.total_backers, p)) for p in [10, 50, 90]}
median_net = float(np.median(results.net_revenue))

print(campaign_scorecard(prob, raised_pcts, backer_pcts, median_net, demand["rating"], campaign.goal))
```

**Cell 9 — Code: Funding Trajectory Fan Chart**
```python
fig = funding_trajectory_fan_chart(results.daily_trajectories, campaign.goal, campaign.duration_days)
plt.show()
```

**Cell 10 — Markdown: Gap Analysis Header**
```markdown
## Gap Analysis — What You Need
For each audience channel: what you currently have, what you'd need to reach 70% confidence of funding, and whether that's realistic given the addressable market.
```

**Cell 11 — Code: Gap Analysis**
```python
print("Running gap analysis (this takes ~60 seconds)...")
gap_70 = gap_analysis(inputs, target_probability=0.70, n_runs=300, seed=SEED)

# Add market saturation check
for channel, data in gap_70.items():
    check = saturation_check(data["you_need"] if isinstance(data["you_need"], int) else 0, channel)
    data["market_check"] = check["feasibility"]

display(gap_analysis_table(gap_70, target_pct=70))
```

**Cell 12 — Markdown: Sensitivity Header**
```markdown
## Sensitivity Analysis — Where to Focus
Which levers have the biggest impact on campaign outcomes? Focus your pre-launch effort here.
```

**Cell 13 — Code: Sensitivity / Tornado Chart**
```python
print("Running sensitivity analysis...")
tornado_data = tornado_analysis(inputs, n_runs=500, seed=SEED)
baseline = float(np.median(results.total_raised))

fig = tornado_chart(tornado_data, baseline)
plt.show()

print("\nImpact ranking:")
for channel, data in tornado_data.items():
    print(f"  {channel.replace('_', ' ').title():.<30s} ${data['impact']:>10,.0f} impact range")
```

**Cell 14 — Markdown: Scenarios Header**
```markdown
## Scenario Comparison
Four pre-configured scenarios showing how different levels of pre-launch preparation affect outcomes.
```

**Cell 15 — Code: Scenario Comparison**
```python
from dataclasses import replace

scenarios_config = [
    {"name": "Current State", "overrides": {}},
    {"name": "Modest Prep (8 weeks)", "overrides": {"email_list": 500, "daily_ad_budget": 20.0, "pr_hits": 1}},
    {"name": "Strong Prep (12 weeks)", "overrides": {"email_list": 2000, "daily_ad_budget": 75.0, "pr_hits": 3, "ig_followers": 500}},
    {"name": "Ideal Case", "overrides": {"email_list": 5000, "daily_ad_budget": 100.0, "pr_hits": 5, "ig_followers": 2000, "fb_followers": 500, "monthly_site_visitors": 1000}},
]

scenario_results = []
for sc in scenarios_config:
    sc_inputs = replace(inputs, **sc["overrides"])
    sc_results = run_simulation(sc_inputs, n_runs=N_RUNS, seed=SEED)
    scenario_results.append({
        "name": sc["name"],
        "inputs": sc_inputs,
        "prob": sc_results.probability_of_funding(),
        "median_raised": float(np.median(sc_results.total_raised)),
        "median_net": float(np.median(sc_results.net_revenue)),
    })

display(scenario_comparison_table(scenario_results))

# Overlay trajectory charts
fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#e74c3c", "#f39c12", "#27ae60", "#2980b9"]
for i, sc in enumerate(scenarios_config):
    sc_inputs = replace(inputs, **sc["overrides"])
    sc_results = run_simulation(sc_inputs, n_runs=N_RUNS, seed=SEED)
    p50 = np.percentile(sc_results.daily_trajectories, 50, axis=0)
    days = np.arange(1, campaign.duration_days + 1)
    ax.plot(days, p50, color=colors[i], linewidth=2, label=sc["name"])

ax.axhline(y=campaign.goal, color="red", linestyle="--", alpha=0.5, label=f"Goal: ${campaign.goal:,.0f}")
ax.set_xlabel("Campaign Day")
ax.set_ylabel("Cumulative Funds Raised ($)")
ax.set_title("Scenario Comparison — Median Funding Trajectories")
ax.legend()
plt.tight_layout()
plt.show()
```

**Cell 16 — Markdown: Recommendations**
```markdown
## Recommendations & Next Steps
Based on the simulation results, demand signals, and gap analysis.
```

**Cell 17 — Code: Recommendations**
```python
print("=" * 60)
print("  RECOMMENDATIONS")
print("=" * 60)

if demand["rating"] == "Weak":
    print("\n⚠️  DEMAND CONFIDENCE IS WEAK")
    print("   Before committing to a campaign, complete the validation")
    print("   playbook above. The simulation shows what's POSSIBLE,")
    print("   not what's PROBABLE without proven demand.\n")

print("RANKED PRE-LAUNCH ACTIONS BY SIMULATION IMPACT:\n")

# Use scenario deltas to rank actions
actions = [
    ("Build email list to 500+", "Moves P(funded) from current to modest scenario", "High"),
    ("Run $20/day Facebook ads for 2 weeks", "Provides real conversion data AND builds audience", "High"),
    ("Create IndieGoGo pre-launch page", "Free demand signal + builds early backer list", "Medium"),
    ("Increase Instagram posting to 3x/week", "Leverage existing 124 followers + organic reach", "Medium"),
    ("Secure 1-3 press/media mentions", "High-variance but potentially high-impact", "Medium"),
    ("Post in gun safe forums/communities", "Free demand validation + audience building", "Low cost"),
]

for i, (action, impact, priority) in enumerate(actions, 1):
    print(f"  {i}. [{priority}] {action}")
    print(f"     {impact}\n")

print("─" * 60)
print(f"\nGO/NO-GO FRAMEWORK:")
print(f"  • P(funded) < 20%:  DO NOT LAUNCH without more preparation")
print(f"  • P(funded) 20-50%: RISKY — consider a lower goal or more prep time")
print(f"  • P(funded) 50-70%: VIABLE — proceed with active marketing plan")
print(f"  • P(funded) > 70%:  STRONG — launch with confidence")
print(f"\n  Current P(funded): {prob:.1%}")
```

- [ ] **Step 2: Run the notebook end-to-end**

Run:
```bash
cd /c/GitHub/indiegogo-simulator/notebooks
jupyter nbconvert --to notebook --execute cloak-campaign-simulator.ipynb --output cloak-campaign-simulator-executed.ipynb
```

Expected: Notebook executes without errors. Review output visually in JupyterLab.

- [ ] **Step 3: Commit**

```bash
git add notebooks/cloak-campaign-simulator.ipynb
git commit -m "feat: complete CLOAK campaign simulator notebook with all 11 sections"
```

---

## Task 13: IGG Comparables Research

**Files:**
- Modify: `data/igg-comparables.json`

This is a research task, not a coding task. The engineer (or AI agent) must search IndieGoGo for 10-20 comparable campaigns and populate the JSON file.

- [ ] **Step 1: Research comparable IndieGoGo campaigns**

Search IndieGoGo for campaigns matching these criteria:
- Physical product, $100-300 price point
- Safety/security/preparedness category
- Adjacent products: Faraday bags, safe accessories, gun safe lighting, EMP protection, emergency preparedness gear

For each campaign found, record in `data/igg-comparables.json`:
```json
{
  "name": "Campaign Name",
  "url": "https://www.indiegogo.com/projects/...",
  "category": "Technology",
  "product_type": "Faraday bag",
  "price_point": 149.99,
  "goal": 10000,
  "raised": 45000,
  "backers": 250,
  "duration_days": 30,
  "perk_tiers": 4,
  "notes": "Relevant context"
}
```

- [ ] **Step 2: Commit**

```bash
git add data/igg-comparables.json
git commit -m "data: add researched IndieGoGo comparable campaigns"
```

---

## Task 14: End-to-End Validation & Cleanup

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 2: Run notebook end-to-end and verify outputs**

Open `notebooks/cloak-campaign-simulator.ipynb` in JupyterLab. Run all cells. Verify:
- Scorecard displays with plausible numbers
- Fan chart renders with visible U-shape and goal line
- Gap analysis table has all channels with reasonable deltas
- Tornado chart renders with bars sorted by impact
- Scenario comparison shows increasing probability across scenarios
- Recommendations section displays

- [ ] **Step 3: Commit any fixes**

```bash
git add -A
git commit -m "fix: end-to-end validation fixes"
```
