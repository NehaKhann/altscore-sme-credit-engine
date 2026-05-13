import pandas as pd
import logging
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)


# ── Pydantic models ──────────────────────────────────────────────────────────

class TransactionRow(BaseModel):
    business_id: str
    date: date
    amount: float
    direction: str
    category: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Amount must be positive, got {v}")
        return v

    @field_validator("direction")
    @classmethod
    def direction_must_be_valid(cls, v: str) -> str:
        if v not in ("credit", "debit"):
            raise ValueError(f"Direction must be credit or debit, got {v}")
        return v


class PaymentRow(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    business_id: str
    due_date: date
    paid_date: Optional[date] = None
    amount: float
    status: str
    days_late: int

    @field_validator("days_late", mode="before")
    @classmethod
    def coerce_to_int(cls, v) -> int:
        return int(v)  # converts numpy int32/int64 to native Python int

class UtilityRow(BaseModel):
    business_id: str
    bill_date: date
    paid_date: Optional[date] = None
    amount: float
    utility_type: str
    days_late: int

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Amount must be positive, got {v}")
        return v

    @field_validator("days_late")
    @classmethod
    def days_late_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"days_late must be >= 0, got {v}")
        return v


class BusinessRow(BaseModel):
    business_id: str
    name: str
    industry: str
    registered_date: date
    city: str

    @model_validator(mode="after")
    def name_must_not_be_empty(self) -> "BusinessRow":
        if not self.name.strip():
            raise ValueError("Business name cannot be empty")
        return self


# ── Validation function ──────────────────────────────────────────────────────

def validate_dataframe(
    df: pd.DataFrame,
    model: type
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Validate every row of a DataFrame against a Pydantic model.
    Returns (valid_rows_df, list_of_errors).
    """
    valid_rows = []
    errors = []

    for idx, row in df.iterrows():
        try:
            # convert row to dict and clean pandas types
            row_dict = {}
            for k, v in row.to_dict().items():
                if pd.isna(v) if not isinstance(v, (list, dict)) else False:
                    row_dict[k] = None
                elif hasattr(v, 'date'):  # converts Timestamp → date
                    row_dict[k] = v.date()
                elif hasattr(v, 'item'):  # converts numpy int/float → Python native
                    row_dict[k] = v.item()
                else:
                    row_dict[k] = v

            model(**row_dict)
            valid_rows.append(row)
        except Exception as e:
            errors.append({
                "row_index": idx,
                "error_message": str(e),
                "row_data": row.to_dict(),
            })

    valid_df = pd.DataFrame(valid_rows).reset_index(drop=True) if valid_rows else pd.DataFrame()

    total = len(df)
    valid = len(valid_df)
    logger.info(f"{model.__name__}: {valid}/{total} rows valid, {len(errors)} errors")

    return valid_df, errors


def validate_all(
    cleaned: dict[str, pd.DataFrame]
) -> tuple[dict[str, pd.DataFrame], dict[str, list]]:
    """Run validation on all cleaned DataFrames."""
    logger.info("Running validation on all sources...")

    models = {
        "transactions": TransactionRow,
        "payments":     PaymentRow,
        "utilities":    UtilityRow,
        "businesses":   BusinessRow,
    }

    validated = {}
    all_errors = {}

    for name, df in cleaned.items():
        valid_df, errors = validate_dataframe(df, models[name])
        validated[name] = valid_df
        all_errors[name] = errors

    return validated, all_errors


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from loader import load_all_sources
    from cleaner import clean_all

    sources = load_all_sources()
    cleaned = clean_all(sources)
    validated, errors = validate_all(cleaned)

    for name, errs in errors.items():
        if errs:
            print(f"\n--- {name} errors ({len(errs)}) ---")
            for e in errs[:3]:  # show first 3 only
                print(f"  Row {e['row_index']}: {e['error_message']}")
        else:
            print(f"\n--- {name}: all rows valid ---")