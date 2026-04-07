"""Audience source traffic models.

Each function takes audience size inputs + U-curve weights + RNG,
samples conversion rates from distributions, and returns daily backer counts.
"""

import numpy as np
from src import distributions as D


def _sample(dist_param, rng) -> float:
    """Sample a single value from a DistParam's distribution."""
    return float(dist_param.dist.rvs(random_state=rng))


def email_traffic(list_size, duration_days, weights, rng, emails_per_campaign=5):
    """Model email-driven backers across the campaign.

    Args:
        emails_per_campaign: Number of blast emails sent over the campaign period.
            Typical campaigns send launch, mid, final-push, and reminder emails.
            Default 5 reflects a realistic drip sequence.
    """
    if list_size == 0:
        return np.zeros(duration_days)
    open_rate = _sample(D.EMAIL_OPEN_RATE, rng)
    ctr = _sample(D.EMAIL_CTR, rng)
    page_to_backer = _sample(D.EMAIL_PAGE_TO_BACKER, rng)
    # Multiply by emails_per_campaign: each blast is an independent send opportunity
    total_page_views = list_size * open_rate * ctr * emails_per_campaign
    total_backers_expected = total_page_views * page_to_backer
    email_weights = np.copy(weights)
    email_weights[0] *= 5.0
    email_weights[1] *= 3.0
    email_weights /= email_weights.sum()
    expected_daily = total_backers_expected * email_weights
    return rng.poisson(np.maximum(expected_daily, 0))


def social_traffic(ig_followers, fb_followers, duration_days, weights, rng):
    total_backers_expected = 0.0
    if ig_followers > 0:
        ig_reach = ig_followers * _sample(D.IG_REACH_RATE, rng)
        ig_clicks = ig_reach * _sample(D.IG_CTR, rng)
        ig_backers = ig_clicks * _sample(D.IG_PAGE_TO_BACKER, rng)
        total_backers_expected += ig_backers * 6
    if fb_followers > 0:
        fb_reach = fb_followers * _sample(D.FB_REACH_RATE, rng)
        fb_clicks = fb_reach * _sample(D.FB_CTR, rng)
        fb_backers = fb_clicks * _sample(D.FB_PAGE_TO_BACKER, rng)
        total_backers_expected += fb_backers * 6
    if total_backers_expected == 0:
        return np.zeros(duration_days)
    expected_daily = total_backers_expected * weights
    return rng.poisson(np.maximum(expected_daily, 0))


def paid_ads_traffic(daily_budget, duration_days, weights, rng):
    if daily_budget <= 0:
        return np.zeros(duration_days)
    cpm = _sample(D.AD_CPM, rng)
    ctr = _sample(D.AD_CTR, rng)
    page_to_backer = _sample(D.AD_PAGE_TO_BACKER, rng)
    daily_impressions = (daily_budget / cpm) * 1000
    daily_clicks = daily_impressions * ctr
    daily_expected_backers = daily_clicks * page_to_backer
    ad_weights = 0.5 * np.ones(duration_days) / duration_days + 0.5 * weights
    expected_daily = daily_expected_backers * duration_days * ad_weights
    return rng.poisson(np.maximum(expected_daily, 0))


def pr_traffic(num_hits, duration_days, weights, rng):
    if num_hits <= 0:
        return np.zeros(duration_days)
    total_backers_expected = 0.0
    for _ in range(num_hits):
        reach = _sample(D.PR_REACH_PER_HIT, rng)
        clicks = reach * _sample(D.PR_CTR, rng)
        backers = clicks * _sample(D.PR_PAGE_TO_BACKER, rng)
        total_backers_expected += backers
    pr_weights = np.copy(weights)
    pr_weights[:7] *= 3.0
    pr_weights /= pr_weights.sum()
    expected_daily = total_backers_expected * pr_weights
    return rng.poisson(np.maximum(expected_daily, 0))


def website_traffic(monthly_visitors, duration_days, weights, rng):
    if monthly_visitors <= 0:
        return np.zeros(duration_days)
    multiplier = _sample(D.SITE_CAMPAIGN_MULTIPLIER, rng)
    campaign_daily_visitors = (monthly_visitors / 30.0) * multiplier
    ctr = _sample(D.SITE_TO_IGG_CTR, rng)
    page_to_backer = _sample(D.SITE_PAGE_TO_BACKER, rng)
    daily_expected = campaign_daily_visitors * ctr * page_to_backer
    expected_daily = daily_expected * duration_days * weights
    return rng.poisson(np.maximum(expected_daily, 0))


def igg_organic_traffic(duration_days, weights, rng, trending_boost=1.0):
    daily_visitors = _sample(D.IGG_DAILY_CATEGORY_VISITORS, rng) * trending_boost
    page_to_backer = _sample(D.IGG_PAGE_TO_BACKER, rng)
    daily_expected = daily_visitors * page_to_backer
    organic_weights = 0.7 * np.ones(duration_days) / duration_days + 0.3 * weights
    expected_daily = daily_expected * duration_days * organic_weights
    return rng.poisson(np.maximum(expected_daily, 0))


def word_of_mouth_traffic(cumulative_backers, duration_days, rng):
    tells = _sample(D.WOM_TELLS, rng)
    visit_rate = _sample(D.WOM_VISIT_RATE, rng)
    page_to_backer = _sample(D.WOM_PAGE_TO_BACKER, rng)
    wom_backers = np.zeros(duration_days)
    for day in range(1, duration_days):
        new_referrals = cumulative_backers[day - 1] * tells * visit_rate * page_to_backer
        wom_backers[day] = rng.poisson(max(new_referrals, 0))
    return wom_backers


def total_daily_backers(email_list, ig_followers, fb_followers, daily_ad_budget,
                        pr_hits, monthly_site_visitors, duration_days, weights, rng):
    backers = np.zeros(duration_days)
    backers += email_traffic(email_list, duration_days, weights, rng)
    backers += social_traffic(ig_followers, fb_followers, duration_days, weights, rng)
    backers += paid_ads_traffic(daily_ad_budget, duration_days, weights, rng)
    backers += pr_traffic(pr_hits, duration_days, weights, rng)
    backers += website_traffic(monthly_site_visitors, duration_days, weights, rng)
    backers += igg_organic_traffic(duration_days, weights, rng)
    cumulative = np.cumsum(backers)
    backers += word_of_mouth_traffic(cumulative, duration_days, rng)
    return backers.astype(int)
