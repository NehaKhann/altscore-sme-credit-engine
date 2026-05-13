import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_business_features(
    transactions_df: pd.DataFrame,
    businesses_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute business maturity and growth features per business.
    Returns DataFrame with business_id + 7 business feature columns.
    """
    df  = transactions_df.copy()
    biz = businesses_df.copy()

    df["date"]            = pd.to_datetime(df["date"])
    biz["registered_date"] = pd.to_datetime(biz["registered_date"])

    credits = df[df["direction"] == "credit"].copy()
    credits["month"] = credits["date"].dt.to_period("M")

    monthly_credits = (
        credits.groupby(["business_id", "month"])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "monthly_credit"})
    )

    features = []

    for _, row in biz.iterrows():
        biz_id = row["business_id"]
        mc = monthly_credits[monthly_credits["business_id"] == biz_id].copy()
        mc = mc.sort_values("month")

        # ── business maturity ────────────────────────────────────────────────
        today = pd.Timestamp.today()
        months_in_operation = max(
            0,
            (today.year - row["registered_date"].year) * 12
            + (today.month - row["registered_date"].month)
        )

        # ── revenue growth ───────────────────────────────────────────────────
        if len(mc) >= 6:
            last_3  = mc["monthly_credit"].iloc[-3:].mean()
            prior_3 = mc["monthly_credit"].iloc[-6:-3].mean()
            revenue_growth_3m = round(
                (last_3 - prior_3) / prior_3, 4
            ) if prior_3 > 0 else np.nan
        else:
            revenue_growth_3m = np.nan

        if len(mc) >= 12:
            last_6  = mc["monthly_credit"].iloc[-6:].mean()
            prior_6 = mc["monthly_credit"].iloc[-12:-6].mean()
            revenue_growth_6m = round(
                (last_6 - prior_6) / prior_6, 4
            ) if prior_6 > 0 else np.nan
        else:
            revenue_growth_6m = np.nan

        # ── transaction diversity ────────────────────────────────────────────
        biz_credits = credits[credits["business_id"] == biz_id]

        unique_categories  = biz_credits["category"].nunique()
        avg_txn_size       = round(biz_credits["amount"].mean(), 2) if len(biz_credits) > 0 else 0
        txn_frequency      = round(len(biz_credits) / max(months_in_operation, 1), 2)

        # revenue concentration — top category as % of total inflow
        if len(biz_credits) > 0:
            top_cat_amount = biz_credits.groupby("category")["amount"].sum().max()
            total_amount   = biz_credits["amount"].sum()
            revenue_concentration = round(top_cat_amount / total_amount, 4) if total_amount > 0 else np.nan
        else:
            revenue_concentration = np.nan

        features.append({
            "business_id":          biz_id,
            "months_in_operation":  months_in_operation,
            "revenue_growth_3m":    revenue_growth_3m,
            "revenue_growth_6m":    revenue_growth_6m,
            "unique_categories":    unique_categories,
            "avg_transaction_size": avg_txn_size,
            "transaction_frequency":txn_frequency,
            "revenue_concentration":revenue_concentration,
        })

    result = pd.DataFrame(features)
    logger.info(f"business features: {len(result)} businesses, {result.shape[1]-1} features")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all

    sources = load_all_sources()
    cleaned = clean_all(sources)
    bf = compute_business_features(cleaned["transactions"], cleaned["businesses"])
    print(bf.head())
    print(bf.describe())