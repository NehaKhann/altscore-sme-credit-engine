import pandas as pd
import numpy as np
import logging
import mlflow
import xgboost as xgb
import lightgbm as lgb
import optuna
from sklearn.metrics import roc_auc_score
from scipy import stats
from pathlib import Path

from ingestion.loader import load_all_sources
from ingestion.cleaner import clean_all
from features.pipeline import build_feature_matrix, get_feature_columns
from models.labels import generate_labels, create_train_test_split

logger = logging.getLogger(__name__)
optuna.logging.set_verbosity(optuna.logging.WARNING)

MLFLOW_EXPERIMENT = "altscore-credit-scoring"


def compute_ks_statistic(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """KS statistic — max separation between default and non-default score distributions."""
    defaults     = y_prob[y_true == 1]
    non_defaults = y_prob[y_true == 0]
    ks, _        = stats.ks_2samp(defaults, non_defaults)
    return round(ks, 4)


def prob_to_score(prob: float) -> int:
    """Convert default probability to 300-850 credit score."""
    score = 850 - int(prob * 550)
    return max(300, min(850, score))


def get_risk_band(score: int) -> str:
    """Convert numeric score to risk band label."""
    if score >= 750:
        return "Low"
    elif score >= 600:
        return "Medium"
    return "High"


def train_xgboost(
    X_train, X_test, y_train, y_test, n_trials: int = 30
) -> tuple:
    """Train XGBoost with Optuna hyperparameter tuning. Returns (model, metrics)."""

    def objective(trial):
        params = {
            "max_depth":        trial.suggest_int("max_depth", 2, 6),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3),
            "n_estimators":     trial.suggest_int("n_estimators", 50, 300),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "scale_pos_weight": trial.suggest_float("scale_pos_weight", 1.0, 5.0),
            "eval_metric":      "auc",
            "use_label_encoder": False,
            "random_state":     42,
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, verbose=False)
        prob  = model.predict_proba(X_test)[:, 1]
        return roc_auc_score(y_test, prob)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_params.update({"eval_metric": "auc", "use_label_encoder": False, "random_state": 42})

    model = xgb.XGBClassifier(**best_params)
    model.fit(X_train, y_train, verbose=False)

    prob   = model.predict_proba(X_test)[:, 1]
    auc    = round(roc_auc_score(y_test, prob), 4)
    gini   = round(2 * auc - 1, 4)
    ks     = compute_ks_statistic(y_test.values, prob)

    metrics = {"test_auc": auc, "gini": gini, "ks_statistic": ks}
    return model, best_params, metrics


def train_lightgbm(
    X_train, X_test, y_train, y_test, n_trials: int = 30
) -> tuple:
    """Train LightGBM with Optuna hyperparameter tuning. Returns (model, metrics)."""

    def objective(trial):
        params = {
            "max_depth":        trial.suggest_int("max_depth", 2, 6),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3),
            "n_estimators":     trial.suggest_int("n_estimators", 50, 300),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "is_unbalance":     True,
            "random_state":     42,
            "verbose":          -1,
        }
        model = lgb.LGBMClassifier(**params)
        model.fit(X_train, y_train)
        prob  = model.predict_proba(X_test)[:, 1]
        return roc_auc_score(y_test, prob)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_params.update({"is_unbalance": True, "random_state": 42, "verbose": -1})

    model = lgb.LGBMClassifier(**best_params)
    model.fit(X_train, y_train)

    prob   = model.predict_proba(X_test)[:, 1]
    auc    = round(roc_auc_score(y_test, prob), 4)
    gini   = round(2 * auc - 1, 4)
    ks     = compute_ks_statistic(y_test.values, prob)

    metrics = {"test_auc": auc, "gini": gini, "ks_statistic": ks}
    return model, best_params, metrics


def run_training(n_trials: int = 30) -> dict:
    """Full training pipeline — loads data, trains both models, logs to MLflow."""

    # ── load and prepare data ────────────────────────────────────────────────
    logger.info("Loading data...")
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

    mlflow.set_experiment(MLFLOW_EXPERIMENT)
    results = {}

    # ── train XGBoost ────────────────────────────────────────────────────────
    logger.info("Training XGBoost...")
    with mlflow.start_run(run_name="xgboost"):
        model, params, metrics = train_xgboost(
            X_train, X_test, y_train, y_test, n_trials
        )
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")
        xgb_run_id = mlflow.active_run().info.run_id
        logger.info(f"XGBoost — AUC: {metrics['test_auc']} | Gini: {metrics['gini']} | KS: {metrics['ks_statistic']}")
        results["xgboost"] = {"run_id": xgb_run_id, "metrics": metrics, "model": model}

    # ── train LightGBM ───────────────────────────────────────────────────────
    logger.info("Training LightGBM...")
    with mlflow.start_run(run_name="lightgbm"):
        model, params, metrics = train_lightgbm(
            X_train, X_test, y_train, y_test, n_trials
        )
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")
        lgb_run_id = mlflow.active_run().info.run_id
        logger.info(f"LightGBM — AUC: {metrics['test_auc']} | Gini: {metrics['gini']} | KS: {metrics['ks_statistic']}")
        results["lightgbm"] = {"run_id": lgb_run_id, "metrics": metrics, "model": model}

    # ── pick best model ──────────────────────────────────────────────────────
    best_name = max(results, key=lambda k: results[k]["metrics"]["test_auc"])
    best      = results[best_name]
    logger.info(f"\nBest model: {best_name} with AUC {best['metrics']['test_auc']}")

    # ── show sample predictions ──────────────────────────────────────────────
    best_model = best["model"]
    probs      = best_model.predict_proba(X_test)[:, 1]
    scores     = [prob_to_score(p) for p in probs]
    bands      = [get_risk_band(s) for s in scores]

    print("\n── Sample predictions ──────────────────────────────")
    print(f"{'Business':<12} {'Score':>6} {'Band':<8} {'Default%':>9} {'Actual':>7}")
    print("-" * 50)
    for i, (biz_id) in enumerate(X_test.index):
        print(f"{biz_id:<12} {scores[i]:>6} {bands[i]:<8} {probs[i]*100:>8.1f}% {int(y_test.iloc[i]):>7}")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_training(n_trials=20)