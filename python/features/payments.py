import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def compute_payment_features(
    payments_df: pd.DataFrame,
    utilities_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute payment behavior features per business.
    Combines supplier payments and utility bills into one feature set.
    Returns DataFrame with business_id + 8 payment feature columns.
    """
    pay = payments_df.copy()
    util = utilities_df.copy()

    pay["due_date"]  = pd.to_datetime(pay["due_date"])
    util["bill_date"] = pd.to_datetime(util["bill_date"])

    # filter to last 12 months
    pay_cutoff  = pay["due_date"].max()  - pd.DateOffset(months=12)
    util_cutoff = util["bill_date"].max() - pd.DateOffset(months=12)
    pay  = pay[pay["due_date"]   >= pay_cutoff]
    util = util[util["bill_date"] >= util_cutoff]

    features = []

    all_business_ids = set(pay["business_id"].unique()) | set(util["business_id"].unique())

    for biz_id in all_business_ids:
        p = pay[pay["business_id"] == biz_id]
        u = util[util["business_id"] == biz_id]

        # ── supplier payment features ────────────────────────────────────────
        total_payments = len(p)
        if total_payments > 0:
            on_time_count        = (p["status"] == "on_time").sum()
            pct_on_time          = round(on_time_count / total_payments, 4)
            avg_days_late        = round(p["days_late"].replace(999, np.nan).mean(), 2)
            max_days_late        = int(p["days_late"].replace(999, 0).max())
            late_count_12m       = int((p["status"].isin(["late", "missed"])).sum())

            # longest consecutive on-time streak
            statuses = p.sort_values("due_date")["status"].tolist()
            streak = max_streak = 0
            for s in statuses:
                if s == "on_time":
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 0

            # consistency score — lower std of days_late = more consistent
            days_late_vals = p["days_late"].replace(999, 60).values
            std_late = days_late_vals.std() if len(days_late_vals) > 1 else 0
            mean_late = days_late_vals.mean()
            consistency = round(1 - (std_late / (mean_late + 1)), 4)
            consistency = max(0.0, min(1.0, consistency))
        else:
            pct_on_time    = np.nan
            avg_days_late  = np.nan
            max_days_late  = 0
            late_count_12m = 0
            max_streak     = 0
            consistency    = np.nan

        # ── utility bill features ────────────────────────────────────────────
        total_utility = len(u)
        if total_utility > 0:
            util_on_time   = (u["days_late"] == 0).sum()
            utility_score  = round(util_on_time / total_utility, 4)
        else:
            utility_score  = np.nan

        # ── supplier-only score ──────────────────────────────────────────────
        supplier_score = pct_on_time

        features.append({
            "business_id":               biz_id,
            "pct_bills_on_time":         pct_on_time,
            "avg_days_late":             avg_days_late,
            "max_days_late":             max_days_late,
            "late_payment_count_12m":    late_count_12m,
            "consecutive_on_time_streak":max_streak,
            "payment_consistency_score": consistency,
            "utility_payment_score":     utility_score,
            "supplier_payment_score":    supplier_score,
        })

    result = pd.DataFrame(features)
    logger.info(f"payment features: {len(result)} businesses, {result.shape[1]-1} features")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all

    sources = load_all_sources()
    cleaned = clean_all(sources)
    pf = compute_payment_features(cleaned["payments"], cleaned["utilities"])
    print(pf.head())
    print(pf.describe())