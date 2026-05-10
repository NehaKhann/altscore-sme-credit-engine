# Score 80-100 → LOW risk    (good candidate for loan)
# Score 60-79  → MEDIUM risk (possible with conditions)
# Score 40-59  → HIGH risk   (unlikely to get loan)
# Score 0-39   → VERY HIGH   (bank will reject)

# Later this gets replaced with real XGBoost/LightGBM ML model
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class BusinessInput(BaseModel):
    monthly_revenue: float
    years_in_operation: int
    num_transactions: int

def calculate_score(monthly_revenue: float, years_in_operation: int, num_transactions: int) -> float:
    score = 0.0
    # Revenue score (max 40 points)
    if monthly_revenue >= 50000:
        score += 40
    elif monthly_revenue >= 20000:
        score += 30
    elif monthly_revenue >= 10000:
        score += 20
    else:
        score += 10
    # Years score (max 30 points)
    if years_in_operation >= 5:
        score += 30
    elif years_in_operation >= 3:
        score += 20
    elif years_in_operation >= 1:
        score += 10
    else:
        score += 5
    # Transactions score (max 30 points)
    if num_transactions >= 100:
        score += 30
    elif num_transactions >= 50:
        score += 20
    elif num_transactions >= 20:
        score += 10
    else:
        score += 5
    return round(score, 2)

def get_risk_level(score: float) -> str:
    if score >= 80:
        return "LOW"
    elif score >= 60:
        return "MEDIUM"
    elif score >= 40:
        return "HIGH"
    else:
        return "VERY_HIGH"

@router.post("/predict")
async def predict(data: BusinessInput):
    score = calculate_score(
        data.monthly_revenue,
        data.years_in_operation,
        data.num_transactions
    )
    risk = get_risk_level(score)
    return {
        "credit_score": score,
        "risk_level": risk,
        "breakdown": {
            "revenue_score": min(40, (data.monthly_revenue / 50000) * 40),
            "experience_score": min(30, (data.years_in_operation / 5) * 30),
            "transaction_score": min(30, (data.num_transactions / 100) * 30)
        }
    }
