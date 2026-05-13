import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker("ar_SA")
random.seed(42)
np.random.seed(42)

BUSINESSES_COUNT = 50
MONTHS = 18
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"

INDUSTRIES = ["retail", "food", "services", "manufacturing", "construction"]
CITIES = ["Riyadh", "Jeddah", "Dammam", "Khobar", "Mecca"]
CATEGORIES = ["inventory", "salary", "rent", "utilities", "equipment", "sales", "refund"]


def generate_businesses() -> pd.DataFrame:
    """Generate a list of 50 fake SME businesses."""
    businesses = []
    for i in range(BUSINESSES_COUNT):
        is_risky = i < int(BUSINESSES_COUNT * 0.3)  # 30% risky
        businesses.append({
            "business_id": f"BIZ_{i+1:04d}",
            "name": f"{fake.company()} Co.",
            "industry": random.choice(INDUSTRIES),
            "registered_date": fake.date_between(start_date="-5y", end_date="-6m"),
            "city": random.choice(CITIES),
            "is_risky": is_risky,
        })
    return pd.DataFrame(businesses)


def generate_transactions(businesses_df: pd.DataFrame) -> pd.DataFrame:
    """Generate 18 months of bank transactions per business."""
    transactions = []
    for _, biz in businesses_df.iterrows():
        is_risky = biz["is_risky"]
        for month in range(MONTHS):
            # risky businesses have irregular cashflow
            monthly_credits = random.randint(3, 8) if not is_risky else random.randint(1, 12)
            monthly_debits = random.randint(2, 6)

            base_amount = random.uniform(5000, 50000) if not is_risky else random.uniform(500, 60000)

            for _ in range(monthly_credits):
                transactions.append({
                    "business_id": biz["business_id"],
                    "date": fake.date_between(
                        start_date=f"-{MONTHS - month}m",
                        end_date=f"-{MONTHS - month - 1}m"
                    ),
                    "amount": round(base_amount * random.uniform(0.5, 1.5), 2),
                    "direction": "credit",
                    "category": random.choice(["sales", "refund", "investment"]),
                })

            for _ in range(monthly_debits):
                transactions.append({
                    "business_id": biz["business_id"],
                    "date": fake.date_between(
                        start_date=f"-{MONTHS - month}m",
                        end_date=f"-{MONTHS - month - 1}m"
                    ),
                    "amount": round(base_amount * random.uniform(0.2, 0.8), 2),
                    "direction": "debit",
                    "category": random.choice(["inventory", "salary", "rent", "utilities", "equipment"]),
                })

    return pd.DataFrame(transactions)


def generate_supplier_payments(businesses_df: pd.DataFrame) -> pd.DataFrame:
    """Generate supplier payment records per business."""
    payments = []
    for _, biz in businesses_df.iterrows():
        is_risky = biz["is_risky"]
        num_payments = random.randint(10, 30)

        for _ in range(num_payments):
            due_date = fake.date_between(start_date="-18m", end_date="today")

            if is_risky:
                status = random.choices(
                    ["on_time", "late", "missed"],
                    weights=[0.4, 0.4, 0.2]
                )[0]
            else:
                status = random.choices(
                    ["on_time", "late", "missed"],
                    weights=[0.85, 0.12, 0.03]
                )[0]

            if status == "on_time":
                paid_date = due_date
                days_late = 0
            elif status == "late":
                days_late = random.randint(1, 45)
                paid_date = fake.date_between(
                    start_date=due_date,
                    end_date="+45d"
                )
            else:
                paid_date = None
                days_late = 999

            payments.append({
                "business_id": biz["business_id"],
                "due_date": due_date,
                "paid_date": paid_date,
                "amount": round(random.uniform(500, 20000), 2),
                "supplier_name": fake.company(),
                "status": status,
                "days_late": days_late,
            })

    return pd.DataFrame(payments)


def generate_utility_bills(businesses_df: pd.DataFrame) -> pd.DataFrame:
    """Generate monthly utility bill records per business."""
    bills = []
    for _, biz in businesses_df.iterrows():
        is_risky = biz["is_risky"]

        for month in range(MONTHS):
            for utility in ["electricity", "water", "internet"]:
                due_date = fake.date_between(
                    start_date=f"-{MONTHS - month}m",
                    end_date=f"-{MONTHS - month - 1}m"
                )

                if is_risky:
                    days_late = random.choices(
                        [0, random.randint(1, 30), random.randint(31, 90)],
                        weights=[0.5, 0.35, 0.15]
                    )[0]
                else:
                    days_late = random.choices(
                        [0, random.randint(1, 10)],
                        weights=[0.9, 0.1]
                    )[0]

                paid_date = fake.date_between(
                    start_date=due_date,
                    end_date=f"+{max(days_late, 1)}d"
                ) if days_late < 999 else None

                bills.append({
                    "business_id": biz["business_id"],
                    "bill_date": due_date,
                    "paid_date": paid_date,
                    "amount": round(random.uniform(200, 5000), 2),
                    "utility_type": utility,
                    "days_late": days_late,
                })

    return pd.DataFrame(bills)


def main():
    """Generate all synthetic datasets and save to CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Generating businesses...")
    businesses = generate_businesses()
    businesses.drop(columns=["is_risky"]).to_csv(DATA_DIR / "businesses.csv", index=False)
    logger.info(f"  {len(businesses)} businesses saved")

    logger.info("Generating transactions...")
    transactions = generate_transactions(businesses)
    transactions.to_csv(DATA_DIR / "transactions.csv", index=False)
    logger.info(f"  {len(transactions)} transactions saved")

    logger.info("Generating supplier payments...")
    payments = generate_supplier_payments(businesses)
    payments.to_csv(DATA_DIR / "supplier_payments.csv", index=False)
    logger.info(f"  {len(payments)} payments saved")

    logger.info("Generating utility bills...")
    utilities = generate_utility_bills(businesses)
    utilities.to_csv(DATA_DIR / "utility_bills.csv", index=False)
    logger.info(f"  {len(utilities)} utility bills saved")

    logger.info("Done. Files saved to: " + str(DATA_DIR))


if __name__ == "__main__":
    main()