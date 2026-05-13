import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "synthetic"


def load_transactions(path: Path) -> pd.DataFrame:
    """Load and parse transactions CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Transactions file not found: {path}")
    df = pd.read_csv(path, parse_dates=["date"])
    df.columns = df.columns.str.lower().str.strip()
    logger.info(f"Loaded transactions: {len(df)} rows")
    return df


def load_payments(path: Path) -> pd.DataFrame:
    """Load and parse supplier payments CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Payments file not found: {path}")
    df = pd.read_csv(path, parse_dates=["due_date", "paid_date"])
    df.columns = df.columns.str.lower().str.strip()
    logger.info(f"Loaded payments: {len(df)} rows")
    return df


def load_utilities(path: Path) -> pd.DataFrame:
    """Load and parse utility bills CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Utilities file not found: {path}")
    df = pd.read_csv(path, parse_dates=["bill_date", "paid_date"])
    df.columns = df.columns.str.lower().str.strip()
    logger.info(f"Loaded utilities: {len(df)} rows")
    return df


def load_businesses(path: Path) -> pd.DataFrame:
    """Load and parse businesses CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Businesses file not found: {path}")
    df = pd.read_csv(path, parse_dates=["registered_date"])
    df.columns = df.columns.str.lower().str.strip()
    logger.info(f"Loaded businesses: {len(df)} rows")
    return df


def load_all_sources(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Load all 4 CSV sources and return as a dictionary."""
    logger.info(f"Loading all data sources from: {data_dir}")
    return {
        "transactions": load_transactions(data_dir / "transactions.csv"),
        "payments":     load_payments(data_dir / "supplier_payments.csv"),
        "utilities":    load_utilities(data_dir / "utility_bills.csv"),
        "businesses":   load_businesses(data_dir / "businesses.csv"),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sources = load_all_sources()
    for name, df in sources.items():
        print(f"\n--- {name} ---")
        print(df.dtypes)
        print(df.head(2))