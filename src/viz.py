"""Visualization functions for the CLOAK campaign simulator."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from collections import OrderedDict

sns.set_theme(style="whitegrid", palette="deep")

def campaign_scorecard(prob_funding, raised_percentiles, backer_percentiles, median_net_revenue, demand_rating, goal):
    lines = [
        "=" * 56, f"  CLOAK Campaign Simulation — Results", "=" * 56,
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

def funding_trajectory_fan_chart(trajectories, goal, duration_days):
    fig, ax = plt.subplots(figsize=(12, 6))
    days = np.arange(1, duration_days + 1)
    p10 = np.percentile(trajectories, 10, axis=0)
    p25 = np.percentile(trajectories, 25, axis=0)
    p50 = np.percentile(trajectories, 50, axis=0)
    p75 = np.percentile(trajectories, 75, axis=0)
    p90 = np.percentile(trajectories, 90, axis=0)
    ax.fill_between(days, p10, p90, alpha=0.15, color="steelblue", label="10th-90th")
    ax.fill_between(days, p25, p75, alpha=0.3, color="steelblue", label="25th-75th")
    ax.plot(days, p50, color="steelblue", linewidth=2, label="Median")
    ax.axhline(y=goal, color="red", linestyle="--", linewidth=1.5, label=f"Goal: ${goal:,.0f}")
    ax.set_xlabel("Campaign Day")
    ax.set_ylabel("Cumulative Funds Raised ($)")
    ax.set_title("Funding Trajectory — Monte Carlo Fan Chart")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend(loc="upper left")
    plt.tight_layout()
    return fig

def gap_analysis_table(gap_data, target_pct=70):
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

def tornado_chart(tornado_data, baseline_revenue):
    fig, ax = plt.subplots(figsize=(10, 6))
    channels = list(tornado_data.keys())
    low_vals = [tornado_data[c]["low_revenue"] for c in channels]
    high_vals = [tornado_data[c]["high_revenue"] for c in channels]
    y_pos = np.arange(len(channels))
    ax.barh(y_pos, [h - baseline_revenue for h in high_vals], left=baseline_revenue, height=0.4, color="steelblue", label="High")
    ax.barh(y_pos, [l - baseline_revenue for l in low_vals], left=baseline_revenue, height=0.4, color="lightcoral", label="Low")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c.replace("_", " ").title() for c in channels])
    ax.axvline(x=baseline_revenue, color="black", linewidth=1)
    ax.set_xlabel("Median Gross Revenue ($)")
    ax.set_title("Sensitivity Analysis — Which Levers Matter Most")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend()
    plt.tight_layout()
    return fig

def demand_signal_dashboard(signals, rating, narrative):
    score_colors = {0: "🔴", 1: "🟡", 2: "🟢", 3: "🟢"}
    rows = []
    for s in signals:
        rows.append({"Signal": s.name, "Category": s.category.title(), "Value": s.value,
                      "Strength": score_colors.get(s.score, "⚪"), "Source": s.source})
    return pd.DataFrame(rows)

def scenario_comparison_table(scenarios):
    rows = []
    for s in scenarios:
        rows.append({"Scenario": s["name"], "Email List": f"{s['inputs'].email_list:,}",
                      "Ad Budget": f"${s['inputs'].daily_ad_budget:,.0f}/day", "PR Hits": s["inputs"].pr_hits,
                      "P(Funded)": f"{s['prob']:.0%}", "Expected Raised": f"${s['median_raised']:,.0f}",
                      "Net Revenue": f"${s['median_net']:,.0f}"})
    return pd.DataFrame(rows)
