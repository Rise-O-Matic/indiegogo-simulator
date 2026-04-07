"""Demand signal scoring for CLOAK."""
from dataclasses import dataclass

@dataclass
class DemandSignal:
    name: str
    category: str
    value: str
    score: int
    source: str
    notes: str = ""

SIGNALS = [
    DemandSignal("Pre-orders / sales", "direct", "1 sale", 0, "Client reported", "One sale total"),
    DemandSignal("Email list signups", "direct", "0", 0, "Client reported", "No pre-launch email list"),
    DemandSignal("IGG pre-launch page", "direct", "Not created", 0, "Client reported", "No page set up"),
    DemandSignal("Landing page conversion", "direct", "Unknown", 0, "bosscoversusa.com", "No conversion tracking"),
    DemandSignal("Search volume", "indirect", "~500/mo (est.)", 1, "Needs Google Keyword Planner validation"),
    DemandSignal("Forum discussion", "indirect", "Not researched", 1, "Reddit, gun safe forums"),
    DemandSignal("Competitor activity", "indirect", "None", 1, "Market research", "No direct competitors"),
    DemandSignal("Adjacent product sales", "indirect", "Moderate", 2, "Amazon, IGG", "Faraday bags, safe accessories sell well"),
    DemandSignal("Ad platform audience size", "indirect", "~5M (est.)", 1, "Needs Facebook Ads Manager validation"),
    DemandSignal("Gun safe market growth", "category", "Growing", 2, "Industry reports"),
    DemandSignal("Electronic keypad trend", "category", "Increasing", 2, "Industry trend data"),
    DemandSignal("Prepper market growth", "category", "Strong growth", 2, "Market research"),
]

def demand_confidence_score():
    direct = [s for s in SIGNALS if s.category == "direct"]
    indirect = [s for s in SIGNALS if s.category == "indirect"]
    category = [s for s in SIGNALS if s.category == "category"]
    direct_score = sum(s.score for s in direct)
    indirect_score = sum(s.score for s in indirect)
    category_score = sum(s.score for s in category)
    total = direct_score + indirect_score + category_score
    max_possible = len(SIGNALS) * 3
    if direct_score >= 6:
        rating, narrative = "Strong", "Multiple direct demand signals confirm interest. Simulation results are actionable."
    elif indirect_score >= 6 or total >= 12:
        rating, narrative = "Moderate", "Indirect signals suggest a market exists but demand is not validated with purchases. Recommend pre-launch validation."
    else:
        rating, narrative = "Weak", "Minimal demand signals. The simulation models 'what if demand exists?' scenarios. Strongly recommend completing pre-launch validation steps."
    return {"total_score": total, "max_possible": max_possible, "rating": rating,
            "direct_score": direct_score, "indirect_score": indirect_score, "category_score": category_score,
            "signals": SIGNALS, "narrative": narrative}

VALIDATION_PLAYBOOK = [
    {"action": "Create IndieGoGo pre-launch page", "cost": "Free", "effort": "1 hour", "timeline": "Do immediately",
     "impact": "Replaces 'IGG pre-launch page' signal. 100+ signups in 2 weeks = strong signal."},
    {"action": "Run small Facebook ad to landing page ($5-10/day for 2 weeks)", "cost": "$70-140", "effort": "2 hours setup",
     "timeline": "Start within 1 week", "impact": "Provides real CTR and conversion data. Replaces Tier 3 ad assumptions."},
    {"action": "Smoke test: 'Buy Now' page capturing email intent", "cost": "$200-500 in ads", "effort": "4 hours",
     "timeline": "After initial ad test", "impact": "Strongest demand signal short of actual sales."},
    {"action": "Post in gun safe forums and subreddits", "cost": "Free", "effort": "2-3 hours",
     "timeline": "Do immediately", "impact": "Qualitative demand signal. Watch for 'where can I buy this?' comments."},
    {"action": "Google Keyword Planner search volume analysis", "cost": "Free", "effort": "30 minutes",
     "timeline": "Do immediately", "impact": "Validates or invalidates the ~500/mo search volume estimate."},
]
