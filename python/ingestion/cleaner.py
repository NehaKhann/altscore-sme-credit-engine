import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transactions DataFrame — remove nulls, duplicates and cap outliers."""
    before = len(df)

    df = df.dropna(subset=["business_id", "date", "amount"])
    df = df.drop_duplicates()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]
    df["date"] = pd.to_datetime(df["date"])

    # cap outliers per business — anything above 99th percentile gets clamped
    def cap_outliers(group: pd.DataFrame) -> pd.DataFrame:
        cap = group["amount"].quantile(0.99)
        group["amount"] = group["amount"].clip(upper=cap)
        return group

    df = df.groupby("business_id", group_keys=False).apply(cap_outliers)
    df = df.reset_index(drop=True)

    after = len(df)
    logger.info(f"clean_transactions: {before} → {after} rows ({before - after} dropped)")
    return df


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Clean supplier payments — fix dates and compute days_late."""
    before = len(df)

    df = df.dropna(subset=["business_id", "due_date"])
    df = df.drop_duplicates()
    df["due_date"] = pd.to_datetime(df["due_date"])
    df["paid_date"] = pd.to_datetime(df["paid_date"], errors="coerce")

    # drop original days_late from CSV before recomputing
    if "days_late" in df.columns:
        df = df.drop(columns=["days_late"])

    def compute_days_late(row):
        if pd.isna(row["paid_date"]):
            return 999
        delta = (row["paid_date"] - row["due_date"]).days
        return max(0, delta)

    df["days_late"] = df.apply(compute_days_late, axis=1).astype("int64")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]
    df = df.reset_index(drop=True)

    after = len(df)
    logger.info(f"clean_payments: {before} → {after} rows ({before - after} dropped)")
    return df

def clean_utilities(df: pd.DataFrame) -> pd.DataFrame:
    """Clean utility bills — same pattern as payments."""
    before = len(df)

    df = df.dropna(subset=["business_id", "bill_date"])
    df = df.drop_duplicates()
    df["bill_date"] = pd.to_datetime(df["bill_date"])
    df["paid_date"] = pd.to_datetime(df["paid_date"], errors="coerce")
    df["days_late"] = df["days_late"].fillna(999).astype(int)
    df["days_late"] = df["days_late"].clip(lower=0)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]
    df = df.reset_index(drop=True)

    after = len(df)
    logger.info(f"clean_utilities: {before} → {after} rows ({before - after} dropped)")
    return df


def clean_businesses(df: pd.DataFrame) -> pd.DataFrame:
    """Clean businesses — remove nulls and fix date types."""
    before = len(df)

    df = df.dropna(subset=["business_id", "name"])
    df = df.drop_duplicates(subset=["business_id"])
    df["registered_date"] = pd.to_datetime(df["registered_date"])
    df = df.reset_index(drop=True)

    after = len(df)
    logger.info(f"clean_businesses: {before} → {after} rows ({before - after} dropped)")
    return df


def clean_all(sources: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Run all cleaners on the full sources dictionary."""
    logger.info("Running all cleaners...")
    return {
        "transactions": clean_transactions(sources["transactions"]),
        "payments":     clean_payments(sources["payments"]),
        "utilities":    clean_utilities(sources["utilities"]),
        "businesses":   clean_businesses(sources["businesses"]),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from loader import load_all_sources
    sources = load_all_sources()
    cleaned = clean_all(sources)
    for name, df in cleaned.items():
        print(f"\n--- {name} ---")
        print(f"Shape: {df.shape}")
        print(f"Nulls:\n{df.isnull().sum()}")