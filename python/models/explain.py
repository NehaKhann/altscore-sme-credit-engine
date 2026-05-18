import pandas as pd
import numpy as np
import logging
import shap
from pathlib import Path

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    "monthly_avg_inflow":         "Average monthly revenue",
    "monthly_std_inflow":         "Revenue stability",
    "cashflow_volatility":        "Cashflow volatility",
    "min_monthly_inflow":         "Minimum monthly revenue",
    "max_to_min_ratio":           "Revenue range ratio",
    "months_positive_cashflow":   "Months with positive cashflow",
    "avg_monthly_net":            "Average monthly net",
    "inflow_trend_slope":         "Revenue trend",
    "pct_bills_on_time":          "Bill payment rate",
    "avg_days_late":              "Average days late",
    "max_days_late":              "Maximum days late",
    "late_payment_count_12m":     "Late payments (12 months)",
    "consecutive_on_time_streak": "Longest on-time streak",
    "payment_consistency_score":  "Payment consistency",
    "utility_payment_score":      "Utility payment score",
    "supplier_payment_score":     "Supplier payment score",
    "months_in_operation":        "Months in operation",
    "revenue_growth_3m":          "Revenue growth (3 months)",
    "revenue_growth_6m":          "Revenue growth (6 months)",
    "unique_categories":          "Transaction diversity",
    "avg_transaction_size":       "Average transaction size",
    "transaction_frequency":      "Transaction frequency",
    "revenue_concentration":      "Revenue concentration",
}


class ExplainerService:
    """SHAP-based explanation service for credit score predictions."""

    def __init__(self, model):
        """Initialise with a trained XGBoost or LightGBM model."""
        self.model    = model
        self.explainer = shap.TreeExplainer(model)
        logger.info("ExplainerService initialised")

    def explain_single(
        self,
        features_df: pd.DataFrame,
        business_id: str
    ) -> dict:
        """
        Explain a single business prediction using SHAP values.
        Returns top 5 positive and negative factors with human-readable labels.
        """
        shap_values = self.explainer.shap_values(features_df)

        # handle both 1D and 2D shap output
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        # pair feature names with shap values
        feature_impacts = list(zip(features_df.columns.tolist(), sv))
        feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)

        top_positive = [
            {
                "feature":     f,
                "label":       FEATURE_LABELS.get(f, f),
                "shap_value":  round(float(v), 4),
                "impact_pts":  round(float(abs(v)) * 100, 1),
            }
            for f, v in feature_impacts if v < 0
        ][:5]

        top_negative = [
            {
                "feature":     f,
                "label":       FEATURE_LABELS.get(f, f),
                "shap_value":  round(float(v), 4),
                "impact_pts":  round(float(abs(v)) * 100, 1),
            }
            for f, v in feature_impacts if v > 0
        ][:5]

        return {
            "business_id":  business_id,
            "top_positive": top_positive,
            "top_negative": top_negative,
        }

    def human_readable_explanation(self, explain_dict: dict) -> str:
        """
        Convert SHAP explanation dict to a plain English summary.
        Example: 'Score boosted by: strong payment history (+45pts).
                  Score reduced by: high cashflow volatility (-28pts).'
        """
        positives = explain_dict.get("top_positive", [])
        negatives = explain_dict.get("top_negative", [])

        pos_text = ", ".join(
            f"{f['label']} (+{abs(f['impact_pts'])}pts)"
            for f in positives[:3]
        )
        neg_text = ", ".join(
            f"{f['label']} (-{abs(f['impact_pts'])}pts)"
            for f in negatives[:3]
        )

        parts = []
        if pos_text:
            parts.append(f"Score boosted by: {pos_text}.")
        if neg_text:
            parts.append(f"Score reduced by: {neg_text}.")

        return " ".join(parts) if parts else "No significant factors identified."

    def get_feature_importance_df(self) -> pd.DataFrame:
        """
        Global feature importance ranked by mean absolute SHAP value.
        Useful for understanding which features drive the model overall.
        """
        raise NotImplementedError(
            "Call explain_single on multiple rows and average shap_values manually."
        )

    def save_waterfall_chart(
        self,
        features_df: pd.DataFrame,
        business_id: str,
        output_path: Path
    ) -> None:
        """Save a SHAP waterfall chart as PNG for a single business."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        shap_values = self.explainer(features_df)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure()
        shap.plots.waterfall(shap_values[0], show=False)
        plt.title(f"Score explanation — {business_id}", fontsize=12)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Waterfall chart saved: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from ingestion.loader import load_all_sources
    from ingestion.cleaner import clean_all
    from features.pipeline import build_feature_matrix
    from models.labels import generate_labels, create_train_test_split
    from models.train import train_xgboost

    sources  = load_all_sources()
    cleaned  = clean_all(sources)
    features = build_feature_matrix(
        cleaned["transactions"],
        cleaned["payments"],
        cleaned["utilities"],
        cleaned["businesses"],
    )

    labels = generate_labels(features)
    X      = features.drop(columns=["business_id"])
    y      = labels
    X_train, X_test, y_train, y_test = create_train_test_split(X, y)

    # train a quick model
    model, _, metrics = train_xgboost(X_train, X_test, y_train, y_test, n_trials=10)
    logger.info(f"Model AUC: {metrics['test_auc']}")

    # explain first test business
    explainer   = ExplainerService(model)
    sample      = X_test.iloc[[0]]
    business_id = X_test.index[0]

    explanation = explainer.explain_single(sample, str(business_id))

    print(f"\nBusiness: {business_id}")
    print("\nTop positive factors (boosted score):")
    for f in explanation["top_positive"]:
        print(f"  {f['label']:<35} +{abs(f['impact_pts'])} pts")

    print("\nTop negative factors (reduced score):")
    for f in explanation["top_negative"]:
        print(f"  {f['label']:<35} -{abs(f['impact_pts'])} pts")

    print(f"\nSummary: {explainer.human_readable_explanation(explanation)}")

    # save waterfall chart
    explainer.save_waterfall_chart(
        sample,
        str(business_id),
        Path("notebooks/charts/waterfall_sample.png")
    )
    print("\nWaterfall chart saved to notebooks/charts/waterfall_sample.png")