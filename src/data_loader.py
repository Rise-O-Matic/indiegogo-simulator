"""Load and filter Kickstarter dataset and IndieGoGo comparables."""
import json
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
KS_CSV = DATA_DIR / "kickstarter" / "ks-projects-201801.csv"
IGG_COMPARABLES = DATA_DIR / "igg-comparables.json"

def load_kickstarter(filepath=KS_CSV):
    return pd.read_csv(filepath, encoding="latin-1")

def filter_kickstarter_comparables(df):
    df = df.copy()
    df["avg_pledge"] = df["usd pledged"] / df["backers"].replace(0, np.nan)
    return df[
        (df["main_category"].isin(["Technology", "Design"]))
        & (df["usd_goal_real"].between(5_000, 100_000))
        & (df["avg_pledge"].between(50, 500))
        & (df["state"].isin(["successful", "failed"]))
    ].copy()

def kickstarter_stats(df):
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

def load_igg_comparables(filepath=IGG_COMPARABLES):
    with open(filepath) as f:
        return json.load(f)

def igg_comparables_stats(comparables):
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
