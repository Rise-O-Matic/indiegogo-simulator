"""Conversion rate distributions for each traffic source.

Each distribution is tagged with a confidence tier:
- Tier 1: Research-backed (Kickstarter data, independent benchmark studies with large N)
- Tier 2: Comparable-inferred (IGG comparables, Meta first-party data, practitioner reports)
- Tier 3: Assumed/estimated (CLOAK-specific, poorly-sourced, wide uncertainty bands)

All rates use Beta distributions (bounded 0-1).
All counts use LogNormal distributions (positive, right-skewed).

Beta(a, b) parameterisation: mean = a/(a+b), concentration n = a+b.
Higher n = tighter (more confident) prior.

GROUNDED PRIORS — 2026-04-08
These priors are set from external benchmarks, NOT from CMA-ES calibration.
CMA-ES calibration produced epistatic compensation artifacts where individual
parameters were individually wrong but cancelled in aggregate. This version
restores each parameter to a defensible prior from independent sources.

After updating priors, re-run CMA-ES calibration:
    python -m src.calibrate
    python -m src.calibrate --apply data/calibrated-params.json

Key benchmark sources used:
- Email: Klaviyo 2024 industry report, Mailchimp benchmarks, Crush Crowdfunding
- Social reach: Social Status 2025, SocialInsider 2025 (independent measurement panels)
- Meta ads: Triple Whale 2025 (35,000 brands), WordStream 2025, Affect Group CPM data
- Crowdfunding conversions: Prelaunch Club, The 1-3 Rule (Tarrida), LaunchBoom
- PR: Similarweb (thefirearmblog.com, ammoland.com), referral traffic benchmarks (FigPii)
- IGG organic: Platform-level Similarweb data, LaunchBoom/Growth Turbine practitioner notes
- WOM: IZA referral incentives study, Kickbooster data (incentivised upper bound)
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
# Funnel chain: list_size × open_rate × ctr × page_to_backer × 5_emails
# Open rate × CTR = click rate of full list per email.
# End-to-end: 0.42 × 0.10 × 0.18 × 5 = 3.8% of list backs — matches CF practitioner "2–5%" benchmark.
# Note: EMAIL_CTR here is CTOR (clicks/openers), not CTR of total list.

EMAIL_OPEN_RATE = DistParam(
    stats.beta(a=16.8, b=23.2),  # mean=0.42
    tier=2,
    source="Crowdfunding warm pre-launch lists: 40–50% open rate (Crush Crowdfunding, Enventys). "
           "General Klaviyo hardware benchmark is 30.9%; crowdfunding lists skew higher due to explicit opt-in intent."
)

EMAIL_CTR = DistParam(
    stats.beta(a=3.0, b=27.0),  # mean=0.10 (CTOR: clicks/openers)
    tier=2,
    source="~10% click-to-open rate for a crowdfunding launch email with single clear CTA. "
           "Klaviyo automated flow CTOR for hardware: 5.65%; launch emails with high-intent list land higher. "
           "Cross-check: 40% open × 10% CTOR = 4% of list clicks, matching Klaviyo baseline for triggered flows."
)

EMAIL_PAGE_TO_BACKER = DistParam(
    stats.beta(a=3.6, b=16.4),  # mean=0.18
    tier=3,
    source="~18% of email clickers back the campaign. "
           "Derived: practitioner benchmark is 3–5% of total list backs; "
           "with 4% click rate, back/click ≈ 18%. Wide band warranted — $200 price suppresses this. "
           "Prelaunch Club case studies show warm-list email converts 4–10× better than cold social."
)

# --- Social (Instagram) ---
# Funnel: ig_followers × reach_rate × ctr × page_to_backer × 6_posts
# reach_rate: fraction of followers who see a given post
# ctr: fraction of post-viewers who click bio link (two-step: view→profile→click)
# page_to_backer: fraction of IG-referred visitors who pledge

IG_REACH_RATE = DistParam(
    stats.beta(a=4.0, b=96.0),  # mean=0.040
    tier=1,
    source="4% average organic reach per post (Social Status 2025 independent panel; SocialInsider 2025: 4%, "
           "down 18% YoY). Consistent across multiple measurement panels. "
           "Small accounts (<5K followers) may reach slightly higher % but absolute exposure is tiny."
)

IG_CTR = DistParam(
    stats.beta(a=0.2, b=24.8),  # mean=0.008 (0.8% of post-viewers click bio link)
    tier=3,
    source="~0.8% of post-viewers click the link-in-bio. "
           "Modelled as: 15% of viewers visit profile × 5% of profile visitors click bio link = 0.75%. "
           "No clean published benchmark isolates this two-step rate; Agorapulse study found ~2 clicks/post "
           "regardless of follower count, implying very low end-to-end rate. High uncertainty — wide band."
)

IG_PAGE_TO_BACKER = DistParam(
    stats.beta(a=0.6, b=39.4),  # mean=0.015
    tier=2,
    source="~1.5% of IG-referred visitors back the campaign. "
           "IG organic is cold-to-lukewarm traffic; applies the '1–3 rule' lower end (Tarrida). "
           "Referral traffic converts at 2.9–5.4% for general purchases (FigPii); crowdfunding has "
           "more friction (risk, delay) so lower. $200 price applies additional downward pressure."
)

# --- Social (Facebook) ---
# Funnel: fb_followers × reach_rate × ctr × page_to_backer × 6_posts

FB_REACH_RATE = DistParam(
    stats.beta(a=1.6, b=78.4),  # mean=0.020
    tier=1,
    source="2% organic reach rate per post (Social Status 2025: 1.37% industry average; "
           "Socialinsider: 2–4% considered strong, 1–2% average). "
           "Organic reach collapse on FB is well-established across all measurement sources."
)

FB_CTR = DistParam(
    stats.beta(a=0.1, b=49.9),  # mean=0.002 (0.2% of post-viewers click a post link)
    tier=3,
    source="~0.2% of post-viewers click the post link. "
           "Socialinsider: FB overall engagement rate 0.15–0.20%; link clicks are ~30–50% of engagements. "
           "Implies link CTR of 0.05–0.10% of reach. 0.2% is a modest upper estimate for "
           "product-focused content with explicit CTA. High uncertainty."
)

FB_PAGE_TO_BACKER = DistParam(
    stats.beta(a=0.6, b=39.4),  # mean=0.015
    tier=2,
    source="~1.5% of FB-referred visitors back. Same rationale as IG: 1–3 rule lower end, "
           "crowdfunding friction, $200 price penalty."
)

# --- Paid ads (Meta / Facebook) ---
# Funnel: (daily_budget / cpm) × 1000 impressions → × ctr clicks → × page_to_backer backers
# Implied median CPA: $14 CPM / (2% CTR × 1.2% p2b × 1000/CPM) ≈ $58/backer
# This is consistent with "niche physical product, cold audience, $200 price" range.
# Industry-wide median CPA is $38 (Triple Whale all-industry) and $49 (electronics).
# A $200 product with no pixel data warrants a premium above the established-brand baseline.

AD_CPM = DistParam(
    stats.lognorm(s=0.3500, scale=29.5896),  # median=$14, mean≈$14.9
    tier=1,
    source="Electronics median CPM: $11.45 (Triple Whale 2025, 35K brands). "
           "Sports & Outdoors niche: $12–18 after 2025 CPM inflation (+8–38% YoY, Affect Group). "
           "CLOAK targeting (gun safe owners, prepper/tactical hobbyists) is narrow, pushing CPM up vs. "
           "broad electronics. $14 median with s=0.35 reflects $8–25 realistic range. "
           "Note: Meta policy explicitly allows gun safe/accessory advertising (not weapons)."
)

AD_CTR = DistParam(
    stats.beta(a=2.0, b=98.0),  # mean=0.020
    tier=1,
    source="2% ad CTR for physical product on Meta. "
           "Triple Whale 2025: Electronics median CTR 2.19%, Sports & Outdoors 1.91%. "
           "WordStream 2025: 1.51% average traffic CTR, up to 2.5% for lead-gen. "
           "Strong visual creative (product demo video) supports the 2% central estimate."
)

AD_PAGE_TO_BACKER = DistParam(
    stats.beta(a=0.6, b=49.4),  # mean=0.012
    tier=2,
    source="~1.2% of cold ad visitors back/buy. "
           "Triple Whale 2025: Electronics CVR 1.20%, Sports & Outdoors 1.28% (DTC purchases from cold ads). "
           "For crowdfunding, cold traffic converts below DTC: more friction, risk perception, delayed delivery. "
           "At $200 price point (above typical KS tech range), apply downward adjustment. "
           "LaunchBoom '3% lead-to-backer' applies to a two-step funnel with pre-warmed leads, not cold clicks."
)

# --- PR / media ---
# One PR 'hit' = one article placement on a niche tactical/gun/prepper blog.
# Funnel: reach_per_hit × ctr → clicks × page_to_backer → backers per hit

PR_REACH_PER_HIT = DistParam(
    stats.lognorm(s=0.8000, scale=1617.6432),  # median=3,000 article views, high variance
    tier=2,
    source="Niche tactical/gun blog article reach. "
           "Similarweb data: The Firearm Blog ~200–500K monthly site visits; "
           "Ammoland publishes 25 articles/day so per-article traffic ~500–3,000. "
           "Pew Pew Tactical (larger, more mainstream): 5,000–15,000 per review. "
           "Central estimate 3,000 views/article for a mid-tier placement. s=0.8 reflects "
           "wide variance between a brief mention and a full review on a major outlet."
)

PR_CTR = DistParam(
    stats.beta(a=1.0, b=19.0),  # mean=0.050
    tier=3,
    source="~5% of article readers click through to the product page. "
           "Editorial inline links in a product review/mention: 3–10% CTR (practitioners). "
           "Referral traffic conversion data (FigPii, InvespCRO): 2.9–5.4% to purchase — "
           "but that's conversion of referral visitors, not article click-through. "
           "5% is a reasonable midpoint for a well-placed link in a genuine review. High uncertainty."
)

PR_PAGE_TO_BACKER = DistParam(
    stats.beta(a=0.9, b=29.1),  # mean=0.030
    tier=2,
    source="~3% of press-referred visitors back the campaign. "
           "Press referrals are 'warm by proxy' — editorial framing pre-qualifies the audience. "
           "Referral traffic converts at 2.9–5.4% generally; crowdfunding lower due to friction. "
           "Tactical blog readers are high-intent for relevant accessories."
)


# --- IGG organic ---
# Platform organic discovery: people browsing IndieGoGo who land on the campaign.
# IGG has ~5M monthly site visits (Similarweb), but most is search-driven, not browse-driven.
# Practitioners universally note IGG requires you to 'bring your own audience'; platform
# discovery is minimal for unknown brands (LaunchBoom, Growth Turbine).
# Estimate: ~50–200 total platform-sourced views over 30-day campaign = ~2–7/day.

IGG_DAILY_CATEGORY_VISITORS = DistParam(
    stats.lognorm(s=1.0000, scale=79.5708),  # median=5/day, very high variance
    tier=3,
    source="~5 platform-organic visitors/day for an unknown brand with no IGG featured placement. "
           "Derived: 5M IGG monthly visits / ~3,000 active campaigns / 30 days ≈ 55/day average, "
           "but this is highly skewed. Featured campaigns get 10–50× more. Unknown brands get "
           "far below average. Practitioner consensus: IGG organic is negligible without placement. "
           "s=1.0 reflects extreme uncertainty (order-of-magnitude range is plausible)."
)

IGG_PAGE_TO_BACKER = DistParam(
    stats.beta(a=0.4, b=19.6),  # mean=0.020
    tier=3,
    source="~2% of IGG platform-organic visitors back the campaign. "
           "IGG platform browsers are somewhat pre-qualified (on a CF site), "
           "warmer than cold social but colder than email. 1–3 rule midpoint."
)

# --- Word of mouth ---
# Each new backer is modelled as telling WOM_TELLS people, of whom WOM_VISIT_RATE
# fraction visit the page, and WOM_PAGE_TO_BACKER fraction of those back.
# Unincentivised organic WOM for physical products is weak: viral coefficient k << 1.
# IZA referral study: even with incentives, referral rates are very low.
# k < 0.1 naturally; CLOAK's niche (2A accessories) further limits viral spread.

WOM_TELLS = DistParam(
    stats.lognorm(s=0.6000, scale=0.0835),  # median=0.3 people told per backer
    tier=3,
    source="Each backer refers ~0.3 people on average (unincentivised organic WOM). "
           "IZA field experiment: unincentivised crowdfunding referral rate very low. "
           "Kickbooster data (with incentives): ~1.4 sign-ups per paid lead — upper bound with program. "
           "General ecommerce viral coefficient for physical goods without referral program: k=0.1–0.3. "
           "CLOAK niche limits shareability vs. mainstream tech. s=0.6 = high variance."
)

WOM_VISIT_RATE = DistParam(
    stats.beta(a=3.0, b=17.0),  # mean=0.15
    tier=3,
    source="~15% of told people actually visit the campaign page. "
           "No direct published benchmark. Assumes meaningful intent filter — "
           "most people told about a product don't act. 15% is generous given $200 price."
)

WOM_PAGE_TO_BACKER = DistParam(
    stats.beta(a=3.0, b=17.0),  # mean=0.15
    tier=3,
    source="~15% of WOM referral visitors back the campaign. "
           "WOM visitors are warm (peer referral), so higher than cold traffic. "
           "Comparable to warm email visitor quality. 1–3 rule upper end."
)
