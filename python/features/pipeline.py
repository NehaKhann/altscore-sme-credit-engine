import pandas as pd
import numpy as np
import logging

from features.cashflow import compute_cashflow_features
from features.payments import compute_payment_features
from features.business import compute_business_features

logger = logging.getLogger(__name__)


def build_feature_matrix(
    transactions_df: pd.DataFrame,
    payments_df: pd.DataFrame,
    utilities_df: pd.DataFrame,
    businesses_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assembles all features into one matrix ready for model training.
    Merges cashflow, payment, and business features on business_id.
    Fills NaN with column median — safer than zero for ML.
    Returns DataFrame with business_id + all 23 feature columns.
    """
    logger.info("Building feature matrix...")

    cf = compute_cashflow_features(transactions_df)
    pf = compute_payment_features(payments_df, utilities_df)
    bf = compute_business_features(transactions_df, businesses_df)

    features = (
        cf.merge(pf, on="business_id", how="outer")
          .merge(bf, on="business_id", how="outer")
    )

    # columns allowed to have high nulls — fill with 0 (no trend = flat)
    trend_cols = ["inflow_trend_slope", "revenue_growth_3m", "revenue_growth_6m"]
    for col in trend_cols:
        if col in features.columns:
            features[col] = features[col].fillna(0)

    # validate — no OTHER column should be more than 20% null
    null_pcts = features[
        [c for c in features.columns if c not in trend_cols]
    ].isnull().mean()
    bad_cols = null_pcts[null_pcts > 0.2]
    if len(bad_cols) > 0:
        raise ValueError(
            f"These columns exceed 20% nulls: {bad_cols.to_dict()}"
        )

    # fill remaining NaN with column median
    numeric_cols = features.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        median = features[col].median()
        features[col] = features[col].fillna(median)

    logger.info(
        f"Feature matrix ready: {features.shape[0]} businesses, "
        f"{features.shape[1] - 1} features, "
        f"{features.isnull().sum().sum()} nulls remaining"
    )

    return features


def get_feature_columns(features_df: pd.DataFrame) -> list[str]:
    """Returns list of feature column names excluding business_id."""
    return [c for c in features_df.columns if c != "business_id"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all

    sources  = load_all_sources()
    cleaned  = clean_all(sources)

    features = build_feature_matrix(
        cleaned["transactions"],
        cleaned["payments"],
        cleaned["utilities"],
        cleaned["businesses"],
    )

    print(f"\nShape: {features.shape}")
    print(f"\nColumns:\n{features.columns.tolist()}")
    print(f"\nNull counts:\n{features.isnull().sum()}")
    print(f"\nSample:\n{features.head(3)}")
    print(f"\nStats:\n{features.describe().round(2)}")