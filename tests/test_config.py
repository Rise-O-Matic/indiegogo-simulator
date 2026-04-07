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
