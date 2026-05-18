import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def generate_labels(feature_matrix: pd.DataFrame) -> pd.Series:
    """
    Generate credit default labels for each business.
    A business is labeled 1 (default) if 2 or more risk conditions are met.
    Returns Series with business_id as index, values 0 or 1.
    """
    df = feature_matrix.set_index("business_id").copy()

    # score each condition — need 2 or more to be a default
    risk_score = (
        (df["cashflow_volatility"]       > 0.6).astype(int) +
        (df["pct_bills_on_time"]         < 0.7).astype(int) +
        (df["max_days_late"]             > 45).astype(int)  +
        (df["avg_days_late"]             > 15).astype(int)  +
        (df["payment_consistency_score"] < 0.5).astype(int) +
        (df["revenue_growth_3m"]         < -0.1).astype(int)
    )

    # default if 2 or more conditions triggered
    labels = (risk_score >= 2).astype(int)

    # add 5% random noise
    np.random.seed(42)
    noise_mask = np.random.random(len(labels)) < 0.05
    labels[noise_mask] = 1 - labels[noise_mask]

    # log class balance
    n_defaults  = labels.sum()
    n_total     = len(labels)
    pct_default = round(n_defaults / n_total * 100, 1)
    logger.info(f"Labels: {n_defaults}/{n_total} defaults ({pct_default}%)")

    return labels

def create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Stratified 80/20 train/test split.
    Stratified ensures same class balance in both sets.
    """
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    logger.info(f"Train: {len(X_train)} rows, Test: {len(X_test)} rows")
    logger.info(f"Train defaults: {y_train.sum()} ({round(y_train.mean()*100,1)}%)")
    logger.info(f"Test defaults:  {y_test.sum()} ({round(y_test.mean()*100,1)}%)")

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all
    from features.pipeline import build_feature_matrix

    sources  = load_all_sources()
    cleaned  = clean_all(sources)
    features = build_feature_matrix(
        cleaned["transactions"],
        cleaned["payments"],
        cleaned["utilities"],
        cleaned["businesses"],
    )

    labels = generate_labels(features)
    print(f"\nLabel distribution:\n{labels.value_counts()}")
    print(f"\nSample labels:\n{labels.head(10)}")

    X = features.drop(columns=["business_id"])
    y = labels

    X_train, X_test, y_train, y_test = create_train_test_split(X, y)
    print(f"\nX_train shape: {X_train.shape}")
    print(f"X_test shape:  {X_test.shape}")