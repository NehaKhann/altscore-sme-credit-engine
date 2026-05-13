import pandas as pd
import numpy as np
import logging
from scipy import stats

logger = logging.getLogger(__name__)


def compute_cashflow_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute cashflow-based features per business from transaction data.
    All features computed over the last 12 months of data.
    Returns DataFrame with business_id + 8 cashflow feature columns.
    """
    df = transactions_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    # filter to last 12 months
    cutoff = df["date"].max() - pd.DateOffset(months=12)
    df = df[df["date"] >= cutoff]

    # separate credits and debits
    credits = df[df["direction"] == "credit"].copy()
    debits  = df[df["direction"] == "debit"].copy()

    # monthly aggregates
    credits["month"] = credits["date"].dt.to_period("M")
    debits["month"]  = debits["date"].dt.to_period("M")

    monthly_credits = (
        credits.groupby(["business_id", "month"])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "monthly_credit"})
    )
    monthly_debits = (
        debits.groupby(["business_id", "month"])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "monthly_debit"})
    )
    monthly = pd.merge(monthly_credits, monthly_debits, on=["business_id", "month"], how="outer").fillna(0)
    monthly["net"] = monthly["monthly_credit"] - monthly["monthly_debit"]

    features = []

    for biz_id, grp in monthly.groupby("business_id"):
        credits_vals = grp["monthly_credit"].values
        net_vals     = grp["net"].values
        n_months     = len(grp)

        avg_inflow = credits_vals.mean() if n_months > 0 else 0
        std_inflow = credits_vals.std()  if n_months > 1 else 0

        # trend slope — linear regression over monthly inflow
        if n_months >= 3:
            slope, _, _, _, _ = stats.linregress(range(n_months), credits_vals)
        else:
            slope = np.nan

        features.append({
            "business_id":            biz_id,
            "monthly_avg_inflow":     round(avg_inflow, 2),
            "monthly_std_inflow":     round(std_inflow, 2),
            "cashflow_volatility":    round(std_inflow / avg_inflow, 4) if avg_inflow > 0 else np.nan,
            "min_monthly_inflow":     round(credits_vals.min(), 2) if n_months > 0 else 0,
            "max_to_min_ratio":       round(credits_vals.max() / credits_vals.min(), 4) if credits_vals.min() > 0 else np.nan,
            "months_positive_cashflow": int((net_vals > 0).sum()),
            "avg_monthly_net":        round(net_vals.mean(), 2),
            "inflow_trend_slope":     round(slope, 4) if not np.isnan(slope) else np.nan,
        })

    result = pd.DataFrame(features)
    logger.info(f"cashflow features: {len(result)} businesses, {result.shape[1]-1} features")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all

    sources = load_all_sources()
    cleaned = clean_all(sources)
    cf = compute_cashflow_features(cleaned["transactions"])
    print(cf.head())
    print(cf.describe())