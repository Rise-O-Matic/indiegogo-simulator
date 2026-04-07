# IndieGoGo Campaign Simulator for CLOAK

**Date:** 2026-04-07
**Status:** Draft
**Product:** CLOAK Electronic Safe Keypad Shield by Boss Covers USA
**Form Factor:** Jupyter Notebook (Python)

---

## 1. Problem Statement

Boss Covers USA is preparing to launch CLOAK -- a $179.99 removable keypad shield for electronic safes -- on IndieGoGo, targeted for June 2026. The product protects against EMP, fire, water, and physical impact through a 6-layer construction system.

The company has:
- One sale to date
- No proven demand signals
- No pre-launch email list
- Minimal social media presence
- A live website (bosscoversusa.com) with threat-specific SEO landing pages but negligible traffic

Before committing to a crowdfunding campaign, they need to understand:
1. **What is the probability of the campaign succeeding** under various conditions?
2. **What audience and marketing assets need to be built** before launch to reach acceptable confidence levels?
3. **Is there sufficient evidence of demand** to justify running a campaign at all?
4. **What is the gap** between the current state and a fundable state?

No tool exists to answer these questions. There is no IndieGoGo campaign simulator -- open source, commercial, or SaaS -- anywhere. Academic ML projects classify Kickstarter campaigns as success/fail but do not simulate day-by-day funding trajectories or model pre-launch planning scenarios.

## 2. Solution Overview

A Jupyter Notebook that combines a **marketing funnel model** with **Monte Carlo simulation** to project crowdfunding campaign outcomes under uncertainty. The notebook is bespoke for the CLOAK campaign but built on generalizable crowdfunding research.

### Core Approach: Hybrid Funnel + Monte Carlo

The campaign is modeled as a marketing funnel:

```
Audience Sources -> Daily Page Views -> Daily New Backers -> Gross Revenue -> Net Revenue
```

Each conversion rate in the funnel is not a single number but a **probability distribution** (Beta for rates, LogNormal for counts). The Monte Carlo engine samples from these distributions 10,000 times, producing a full range of possible outcomes rather than a single point estimate.

### Key Insight

The simulator's most valuable output is the **gap analysis**: "Here's where you are. Here's where you need to be. Here's the delta." For a client starting from near-zero, this reframes the tool from "will we succeed?" to "what do we need to build, and is that realistic?"

## 3. Data Strategy

### 3.1 Three-Tier Confidence System

Every parameter in the model is tagged with a confidence tier:

| Tier | Label | Source | Uncertainty Band |
|------|-------|--------|-----------------|
| **Tier 1** | Research-backed | Kickstarter large-N dataset (200K+ campaigns) + IndieGoGo adjustment factors, published academic studies, industry reports | Narrow |
| **Tier 2** | Comparable-inferred | 10-20 manually researched IndieGoGo campaigns with similar characteristics | Medium |
| **Tier 3** | Assumed/estimated | Best-guess for CLOAK-specific parameters with no direct evidence | Wide |

Every chart and output labels which tiers are driving the result. Tier 3 parameters receive the widest Monte Carlo distributions, and the gap analysis specifically calls out: "your biggest risk is in Tier 3 assumptions."

### 3.2 Kickstarter as Foundation

The Kickstarter dataset on Kaggle (200K+ projects) provides the statistical foundation. It includes category, goal, pledged amount, backer count, duration, and outcome for each campaign.

**What transfers well across platforms (same human behavior):**
- Conversion funnel dynamics (traffic -> page view -> back)
- U-shaped funding curve (documented on both platforms)
- Effect of goal amount on success probability
- Effect of campaign duration on outcomes
- Price point / average pledge relationships
- Category performance patterns

**What needs a platform adjustment factor:**
- Success rates: Kickstarter ~42% vs IndieGoGo ~9-30% (Kickstarter curates more aggressively)
- Organic platform discovery: Kickstarter drives more internal traffic
- Backer pool size and demographics
- Fee structure differences

**Approach:**
1. Filter Kickstarter data to comparable campaigns: physical product, $100-300 price, Home/Technology/Safety categories
2. Derive conversion rate distributions and funding curve parameters from this filtered set
3. Apply IndieGoGo adjustment multipliers for known platform differences
4. Validate adjusted predictions against 10-20 manually researched IndieGoGo comparable campaigns
5. If adjusted model matches real IGG outcomes, proceed with confidence; if not, recalibrate

### 3.3 IndieGoGo Comparable Campaigns

Manually research 10-20 IndieGoGo campaigns with characteristics similar to CLOAK:
- Physical product, $100-300 price point
- Safety/security/preparedness niche
- American-made positioning
- Adjacent categories: safe accessories, Faraday bags, emergency preparedness gear, gun safe lighting

For each, document:
- Product type, price point, category
- Goal vs. actual raised
- Number of backers
- Campaign duration
- Perk structure
- Pre-launch email list size (if mentioned in campaign updates)

This research is performed during notebook development and the data is embedded as a static dataset in the notebook. The client does not need to do this research.

This serves as the empirical sanity check for the Kickstarter-derived model.

### 3.4 Meta Business Suite Data (First-Party)

Real performance data from the Bosscovers USA Meta accounts, captured 2026-04-07.
Stored in `data/meta-insights-2026-04-07.md`.

**Facebook (28-day period, Mar 10 - Apr 6, 2026):**
- 69 followers (lifetime)
- 101 views, 60 unique viewers, 4 content interactions, 1 link click, 31 page visits
- 65.3% of views from non-followers (organic discovery works at small scale)

**Instagram (same period):**
- 124 followers
- 645 views, 119 reach, 25 content interactions
- ~3.9% engagement rate (above platform average)
- 50.7% of views from non-followers

**What this calibrates:**
- Social follower-to-view rates: real data replaces benchmarks (Tier 2 instead of Tier 3)
- Instagram outperforms Facebook ~6:1 on views -- simulator weights IG channel higher
- FB link click rate: ~1% (1/101) -- usable as a floor estimate for social-to-page-visit conversion
- IG engagement rate: ~3.9% -- usable for interaction modeling
- No paid ad data (zero campaigns run) -- ad conversion stays at benchmark defaults
- Posting frequency very low (1 post + 2 stories in 28 days) -- engagement is organic, not driven by content volume

**Confidence tier:** Tier 2 (real first-party data, but small sample sizes warrant wide distributions)

### 3.5 Published Benchmarks

- **Funding curve:** U-shaped -- ~33% first 48h, ~33% middle, ~33% final 48h (multiple academic studies)
- **Critical threshold:** Reaching 30% of goal in first 48 hours; below this correlates with 65% failure rate
- **Email conversion rates:** 1-5% subscriber-to-backer (industry reports, Mailchimp benchmarks)
- **Social conversion rates:** 0.5-2% follower-to-backer (platform benchmark reports)
- **Ad performance:** CPM, CTR, conversion rates for physical products by platform (Meta, Google)
- **IndieGoGo fees:** 5% platform + ~3% + $0.20/txn payment processing = ~8% total
- **IndieGoGo organic discovery:** Derived from platform traffic data (~5M monthly visits, category distribution)

### 3.5 IndieGoGo API

The public API provides:
- `GET /api/public/projects/getActiveCrowdfundingProjects` -- all active campaigns
- `GET /api/public/projects/getCrowdfundingProject` -- specific project by URL
- Data includes: goal, funds raised, backer count, start/end dates, rewards, currency

Used for: snapshotting currently-active comparable campaigns, validating fee structures, checking category performance.

Limitations: No historical data, no day-by-day funding curves, no bulk access.

## 4. Simulation Model Architecture

### 4.1 Funnel Structure

```
1. AUDIENCE SOURCES      2. TRAFFIC          3. CONVERSION      4. REVENUE        5. NET OUTCOME
┌──────────────────┐   ┌──────────────┐   ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│ Email list        │──>│              │   │              │  │             │  │              │
│ Social followers  │──>│  Daily page  │──>│  Daily new   │─>│ Gross funds │─>│ Net revenue  │
│ Paid ads          │──>│  views       │   │  backers     │  │ raised      │  │ after fees   │
│ PR/media hits     │──>│              │   │              │  │             │  │              │
│ Website traffic   │──>│              │   │              │  │             │  │              │
│ IGG organic       │──>│              │   │              │  │             │  │              │
│ Word-of-mouth     │──>│              │   │              │  │             │  │              │
└──────────────────┘   └──────────────┘   └──────────────┘  └─────────────┘  └──────────────┘
     Each has a             Shaped by          Each source       Perk mix          IGG 5% +
     reach + CTR            U-curve            has its own       determines        ~3% processing
     distribution           (time decay)       conversion rate   avg pledge        + COGS + shipping
```

### 4.2 Audience Source Models

Each traffic source is modeled independently with its own reach and conversion distributions:

**Email list:**
- Input: list size (count)
- Open rate: Beta distribution, default ~20-25%
- CTR: Beta distribution, default ~2-4%
- Page-view-to-backer conversion: Beta distribution, derived from Kickstarter data
- Timing: bulk of email-driven traffic arrives in first 48 hours (launch blast)

**Social followers (per platform):**
- Input: follower count per platform
- Organic reach rate: Beta distribution, ~2-5% of followers see a post
- CTR from post: Beta distribution, ~1-3%
- Page-view-to-backer conversion: Beta distribution, lower than email
- Timing: posts spread across campaign with emphasis on launch and final days

**Paid ads:**
- Input: daily budget ($)
- CPM: LogNormal distribution, derived from Meta/Google benchmarks for physical products
- CTR: Beta distribution, ~1-2%
- Ad-view-to-backer conversion: Beta distribution, ~0.5-2%
- Timing: spread evenly or front-loaded (configurable)

**PR/media:**
- Input: expected number of press hits
- Reach per hit: LogNormal distribution (high variance -- one article could reach 1K or 100K)
- CTR: Beta distribution, very low
- Timing: typically clustered around launch

**Website traffic:**
- Input: monthly unique visitors, organic search traffic
- Campaign-period traffic multiplier: ratio (traffic often spikes during campaign)
- Site-to-IGG click-through rate: Beta distribution
- Conversion rate: Beta distribution, higher than cold traffic (these visitors sought out the product)

**IGG organic discovery:**
- Not a user input -- derived from platform data
- Based on IndieGoGo's ~5M monthly visits, category share, and algorithmic boost for campaigns hitting early milestones
- Modeled as a daily visitor rate with a boost multiplier if the campaign is trending

**Word-of-mouth:**
- Multiplier: each backer tells X people, Y% of those visit the page
- Creates a compounding effect in the simulation
- Highly uncertain (Tier 3), modeled with wide distributions

### 4.3 U-Shaped Funding Curve

Daily traffic from all sources is modulated by a time-decay function that produces the characteristic U-shape:

- **Days 1-2:** High activity (launch burst). ~33% of total traffic.
- **Days 3 to N-2:** Gradual decay to a baseline (the "valley"). ~33% of total traffic.
- **Days N-1 to N:** Surge (deadline urgency). ~33% of total traffic.

The curve is parameterized from Kickstarter data and adjusted for campaign duration. A 30-day campaign has a deeper valley than a 20-day campaign.

### 4.4 Monte Carlo Engine

```python
for run in range(10_000):
    # Sample conversion rates from distributions
    # For each campaign day:
    #   - Calculate traffic from each source (modulated by U-curve)
    #   - Convert traffic to backers at sampled rates
    #   - Assign perk tier (early bird if available, else standard)
    #   - Accumulate revenue
    # Record: daily funding trajectory, total raised, total backers, funded Y/N
```

Outputs per run:
- Day-by-day cumulative funding array (length = campaign duration)
- Total funds raised
- Total backers
- Funded: boolean (total >= goal)
- Net revenue after fees and COGS

Aggregated across all runs:
- Probability of funding (% of runs where funded == True)
- Percentile bands (10th/25th/50th/75th/90th) for total raised
- Percentile bands for the day-by-day trajectory (fan chart data)
- Per-source contribution breakdown

### 4.5 Revenue Model

```
Gross revenue = (early_bird_backers * early_bird_price) + (standard_backers * standard_price)
Platform fee = gross_revenue * 0.05
Processing fee = (gross_revenue * 0.03) + (total_backers * 0.20)
COGS = total_backers * cogs_per_unit
Shipping = total_backers * shipping_per_unit
Net revenue = gross_revenue - platform_fee - processing_fee - COGS - shipping
```

Early bird allocation: first N backers get early bird pricing (N = early_bird_quantity), remainder pay standard price. In the simulation, backers arrive chronologically so early birds are consumed in order.

## 5. Market Sizing Module

Positioned before the simulation as a **realism ceiling** on all projections.

### 5.1 Parameters

| Parameter | Source |
|-----------|--------|
| US gun safe owners | Industry data (AFSA, firearms industry reports) |
| Electronic keypad subset | % of safes with electronic vs. mechanical locks |
| Annual new safe purchases | Market reports |
| Digitally reachable audience | Facebook Ads Manager audience estimates, Google Keyword Planner |
| Awareness of keypad vulnerability | Estimated (very low -- CLOAK is creating a category) |
| Adjacent market sizes | Faraday bag market, safe accessories, preparedness gear |

### 5.2 How It Feeds the Simulation

- **Saturation check:** If the gap analysis says "you need 50,000 email subscribers" but the total reachable audience is 200,000, that's a 25% capture rate -- extremely ambitious. The notebook flags this.
- **Ad targeting ceiling:** Facebook ad audiences have finite size. The simulator warns if ad budget implies reaching more people than exist in the targeting pool.
- **Organic discovery calibration:** A niche product in a small market gets less IndieGoGo algorithmic lift than a mass-market gadget.

## 6. Demand Signal Analysis Module

Positioned before the simulation as a **go/no-go gate**.

### 6.1 Signal Categories

**Direct demand signals (strongest):**
- Pre-orders / actual sales (currently: 1)
- Email list signups for launch notification
- IndieGoGo pre-launch page signups
- Landing page conversion rate (any visitor action)

**Indirect demand signals (supporting):**
- Google search volume for relevant terms ("safe keypad cover," "protect safe keypad," "EMP safe protection," "faraday safe")
- Forum/community discussion (Reddit, gun safe forums, prepper communities)
- Competitor activity (currently: none -- could mean untapped market or no market)
- Adjacent product sales (Faraday bags, safe dehumidifiers, safe lighting)
- Ad platform audience size estimates

**Category-level signals (context):**
- Gun safe market growth trajectory
- Electronic vs. mechanical keypad trend
- Prepper/preparedness market growth

### 6.2 Demand Confidence Score

The notebook produces a composite score:

- **Strong:** Multiple direct signals confirm demand. Simulation results are actionable.
- **Moderate:** Indirect signals suggest a market but not validated with purchases. Simulation results should be read with caution. Recommend pre-launch validation.
- **Weak:** Minimal signals. The simulation models "what if demand exists?" but the biggest risk is product-market fit, not campaign mechanics.

### 6.3 Pre-Launch Validation Playbook

Ranked by cost/effort, each with expected impact on the simulation:

1. **Free:** Create IndieGoGo pre-launch page, measure signups over 2-4 weeks
2. **$50-200:** Small Facebook ad campaign to landing page, measure CTR and signup rate
3. **$200-500:** Smoke test -- targeted ads to "buy now" page that captures intent (email)
4. **$0:** Post in gun safe forums/subreddits, gauge reaction
5. **$0:** Search volume analysis for related terms
6. **$0:** Survey existing safe owner communities about keypad concerns

Each validation step feeds back into the simulator as Tier 1 or Tier 2 data, replacing Tier 3 assumptions and tightening the probability distributions.

## 7. Outputs & Visualizations

### 7.1 Campaign Scorecard

Summary cell showing key metrics:
- Probability of funding (% of 10,000 runs that hit the goal)
- Expected raised: 10th / 50th / 90th percentile
- Expected backers: 10th / 50th / 90th percentile
- Net revenue after fees/COGS (median)
- Demand confidence rating

### 7.2 Funding Trajectory Fan Chart

- X-axis: campaign day (1 to N)
- Y-axis: cumulative funds raised ($)
- Shaded bands: 10th/25th/50th/75th/90th percentile envelopes
- Horizontal reference line at funding goal
- U-shape visible in the trajectory slope

### 7.3 Gap Analysis Table

For each audience channel:
- **"You have"** -- current input value
- **"You need"** -- required value for 50% / 70% / 90% confidence of funding
- **"Delta"** -- the gap in concrete terms
- **"Difficulty"** -- qualitative rating (Easy/Medium/Hard/Uncontrollable)
- **"Market check"** -- is the target realistic given addressable market?

**"You Need" computation method:** For each audience source, the simulator runs a series of Monte Carlo batches while varying that one input (holding all others at their current values). It finds the input value at which the target confidence threshold (e.g., 70% of runs fund successfully) is crossed. This is essentially a bisection search over the input space for each channel independently.

### 7.4 Sensitivity Tornado Chart

Horizontal bar chart showing which inputs swing the outcome most. Each bar shows the impact on expected revenue when that input is varied from its 10th to 90th percentile while holding all others at median. Tells you where to focus pre-launch effort.

### 7.5 Demand Signal Dashboard

Scorecard of each demand signal with color coding (green/yellow/red), data source citation, and overall demand confidence narrative.

### 7.6 Scenario Comparison Table

Side-by-side comparison of named scenarios:

| Scenario | Description | Inputs | Prob. of Funding | Expected Raised | Net Revenue |
|----------|-------------|--------|-----------------|-----------------|-------------|
| Current state | What you have today | Actual values | Low | Low | Likely negative |
| Modest prep | Reasonable 8-week pre-launch effort | 500 email, $500 ads, 1 PR hit | Moderate | Moderate | Break-even range |
| Strong prep | Aggressive 12-week pre-launch effort | 2,000 email, $2,000 ads, 3 PR hits | Moderate-High | Good | Positive |
| Ideal | Best realistic case | 5,000 email, $3,000 ads, 5 PR hits | High | Strong | Strong |

Each scenario gets its own scorecard and trajectory chart.

### 7.7 Pre-Launch Roadmap

Ranked list of actions with:
- Description of the action
- Expected cost and effort
- Expected impact on simulation (e.g., "building a 1,000-person email list moves funding probability from 15% to 40%")
- Timeline recommendation

## 8. Notebook Structure

```
Cell 01: SETUP & CONFIG
         Imports, random seed, CLOAK product constants, campaign parameters

Cell 02: DATA FOUNDATIONS
         Load Kickstarter dataset, filter to comparables
         Load/document IndieGoGo comparable campaigns
         Derive conversion rate distributions
         IndieGoGo adjustment factors
         Document confidence tiers for every parameter

Cell 03: MARKET SIZING
         Addressable market research
         Digital audience sizing
         Market context summary and saturation thresholds

Cell 04: DEMAND SIGNAL ANALYSIS
         Score each demand signal
         Demand confidence rating
         Pre-launch validation playbook with expected simulation impact

Cell 05: AUDIENCE INPUTS
         Email list size, social followers by platform, ad budget,
         PR/media expectations, website traffic
         (IGG organic derived by model, not user input)

Cell 06: SIMULATION ENGINE
         Define funnel stages and conversion distributions
         U-curve time distribution function
         Monte Carlo loop (10,000 runs)
         Record per-run metrics

Cell 07: PRIMARY OUTPUTS
         Campaign scorecard
         Funding trajectory fan chart
         Probability of funding gauge

Cell 08: GAP ANALYSIS
         "You have" vs "You need" at 50%/70%/90% confidence
         Delta table with difficulty ratings
         Market saturation sanity check

Cell 09: SENSITIVITY ANALYSIS
         Tornado chart
         Per-channel contribution breakdown

Cell 10: SCENARIO COMPARISON
         Pessimistic / Baseline / Optimistic / Custom
         Side-by-side scorecards
         Overlay trajectory charts

Cell 11: RECOMMENDATIONS & NEXT STEPS
         Ranked pre-launch actions with expected impact
         Go/no-go framework
         Pre-launch timeline
```

### Design Principles

- Every cell that uses an assumption cites its source and confidence tier
- All charts include the funding goal as a reference line
- The notebook runs end-to-end in under 30 seconds (numpy vectorization)
- Inputs are concentrated in cells 01 and 05 for easy tweaking and re-running
- Named scenarios are pre-configured parameter sets in cell 10

## 9. Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Runtime | Python 3.13 | Already installed on dev machine |
| Notebook | Jupyter / JupyterLab | Interactive, visual, exploratory |
| Numerics | numpy | Vectorized Monte Carlo, fast |
| Data | pandas | Tables, filtering, scenario management |
| Distributions | scipy.stats | Beta, LogNormal, etc. |
| Visualization | matplotlib + seaborn | Fan charts, tornado charts, trajectories |
| Interactive charts | plotly (optional) | Hover tooltips, zoom in notebook |
| API calls | requests | IndieGoGo API, optional Kaggle download |
| Dataset | Kaggle Kickstarter CSV | 200K+ campaigns, static download |

## 10. Feasibility Assessment

### What Makes This Feasible

- **The math is solved.** Monte Carlo simulation of a marketing funnel is computationally straightforward. numpy handles 10,000 runs in seconds.
- **The Kickstarter dataset exists.** 200K+ campaigns with rich metadata. Filtering to comparable campaigns gives a meaningful statistical base.
- **Jupyter is forgiving.** Every assumption visible, every chart inline, every parameter tweakable. No deployment or infrastructure.
- **Scope is contained.** One notebook, one product, no generalization layer.

### Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| IndieGoGo-specific data is scarce | Medium | Kickstarter base + adjustment factors + manual comparables validation |
| Conversion rate assumptions may be wrong for this niche | Medium | Wide uncertainty bands on Tier 3 params; demand validation playbook |
| No first-party data to calibrate against | High | Simulator is transparent about this; demand signal section flags it explicitly |
| Model may give false confidence | Medium | Conservative defaults, wide confidence intervals, demand score as gate |
| Kickstarter-to-IndieGoGo transfer may be poor | Low-Medium | Validate against manually-researched IGG comparables; flag divergence |
| CLOAK is creating a new category (no direct comparables) | High | Use adjacent categories; acknowledge as biggest uncertainty |

### Verdict

**Feasible with caveats.** The simulator can be built and will produce useful outputs. The biggest limitation is data, not tooling. With one sale and a novel product category, uncertainty bands will be wide. But that is the point: the simulator's most valuable output is showing how much is unknown and providing a concrete roadmap to close those gaps before committing to a campaign.

The tool is honest, not oracular. It maps the space of possible outcomes and highlights what actions would shift the odds.

## 11. Out of Scope

- Multi-product or multi-campaign support (CLOAK only)
- Real-time campaign tracking (this is pre-launch planning)
- Web-based UI or deployment (local Jupyter notebook)
- ML-based prediction models (funnel + Monte Carlo is more transparent and appropriate given data constraints)
- Automated data pipeline (Kickstarter CSV is a one-time download; IGG comparables are manually researched)
- Integration with ad platforms or email tools

## 12. Success Criteria

The simulator is successful if it can answer these questions for the CLOAK team:

1. Given our current state, what is the probability of the campaign funding?
2. What specific audience assets do we need to build before launch, and how large does each need to be?
3. Which pre-launch activities will have the biggest impact on our odds?
4. Is there sufficient evidence of demand to justify running the campaign?
5. What funding goal should we set to maximize success probability while covering costs?
6. What does the day-by-day funding trajectory likely look like, and when are the critical moments?

## 13. Platform Context

**IndieGoGo post-Gamefound acquisition (October 2025):**
- All campaigns are now all-or-nothing (flexible funding discontinued)
- Fees: 5% platform + ~3% + $0.20/txn processing
- InDemand (post-campaign): 5% for IGG-origin campaigns, 8% for external
- Built-in stretch goals system
- ~5M monthly visits, 38M registered users
- Technology category success rate: ~20%
- 74.7% of projects raise less than $50,000
- Campaign duration: up to 60 days allowed, 20-40 day sweet spot

**CLOAK product details:**
- Price: $179.99 (standard perk), early bird price configurable (default $149.99)
- Two-piece removable keypad shield for electronic safes
- Six protective layers: Cerakote aluminum, copper/nickel Faraday, fireproof felt, nylon 6/12
- Protects against: EMP, fire (300F+), water/moisture, physical impact
- Fits 95% of large safes (7.75" cover, 6.5" keypad opening)
- 16 neodymium magnets, 60-second tool-free installation
- Target market: gun safe owners, preparedness-minded, American-made buyers
- Expected launch: June 2026
