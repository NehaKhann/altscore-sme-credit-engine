import logging
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.entities.model_registry.model_version_stages import ALL_STAGES
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_NAME       = "altscore-credit-v1"
EXPERIMENT_NAME  = "altscore-credit-scoring"


def register_best_model() -> str:
    """
    Finds the best run in the experiment by test_auc
    and registers it in the MLflow model registry.
    Returns the registered model version.
    """
    client = MlflowClient()

    # get experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        raise ValueError(f"Experiment '{EXPERIMENT_NAME}' not found. Run train.py first.")

    # find best run by test_auc
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.test_auc DESC"],
        max_results=1,
    )

    if not runs:
        raise ValueError("No runs found. Run train.py first.")

    best_run = runs[0]
    run_id   = best_run.info.run_id
    auc      = best_run.data.metrics.get("test_auc", 0)
    logger.info(f"Best run: {run_id} | AUC: {auc}")

    # register the model
    model_uri = f"runs:/{run_id}/model"
    result    = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
    version   = result.version

    logger.info(f"Registered model '{MODEL_NAME}' version {version}")
    return version


def promote_to_production(version: str) -> None:
    """
    Promotes a registered model version to Production stage.
    Archives any existing Production model first.
    """
    client = MlflowClient()

    # archive existing production model
    try:
        prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        for v in prod_versions:
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=v.version,
                stage="Archived",
            )
            logger.info(f"Archived version {v.version}")
    except Exception:
        pass

    # promote new version
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=version,
        stage="Production",
    )
    logger.info(f"Version {version} promoted to Production")


def load_production_model() -> tuple:
    """
    Loads the current Production model from the registry.
    Returns (model, version_string).
    Falls back to latest run if no Production model exists.
    """
    client = MlflowClient()

    try:
        prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        if prod_versions:
            version   = prod_versions[0].version
            run_id    = prod_versions[0].run_id
            model_uri = f"models:/{MODEL_NAME}/Production"
            model     = mlflow.sklearn.load_model(model_uri)
            logger.info(f"Loaded Production model v{version}")
            return model, f"v{version}"
    except Exception as e:
        logger.warning(f"Could not load Production model: {e}")

    # fallback — load best run directly
    logger.info("Falling back to best run model...")
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.test_auc DESC"],
        max_results=1,
    )
    if not runs:
        raise ValueError("No models found. Run train.py first.")

    run_id    = runs[0].info.run_id
    model_uri = f"runs:/{run_id}/model"
    model     = mlflow.sklearn.load_model(model_uri)
    logger.info(f"Loaded model from run {run_id}")
    return model, run_id[:8]


def promote_if_better(
    new_run_id: str,
    metric: str = "test_auc",
    threshold: float = 0.01,
) -> bool:
    """
    Compares a new run against the current Production model.
    Promotes new model only if it beats current by threshold.
    Returns True if promoted, False if not.
    """
    client = MlflowClient()

    # get new run metric
    new_run     = client.get_run(new_run_id)
    new_metric  = new_run.data.metrics.get(metric, 0)

    # get current production metric
    try:
        prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        if prod_versions:
            prod_run_id    = prod_versions[0].run_id
            prod_run       = client.get_run(prod_run_id)
            current_metric = prod_run.data.metrics.get(metric, 0)
        else:
            current_metric = 0
    except Exception:
        current_metric = 0

    logger.info(f"Current {metric}: {current_metric} | New {metric}: {new_metric}")

    if new_metric >= current_metric + threshold:
        model_uri = f"runs:/{new_run_id}/model"
        result    = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
        promote_to_production(result.version)
        logger.info(f"Promoted new model — improvement: +{round(new_metric - current_metric, 4)}")
        return True

    logger.info("New model did not improve enough — keeping current Production model")
    return False


def list_model_versions() -> pd.DataFrame:
    """
    Returns a DataFrame of all registered model versions with their metrics.
    """
    client   = MlflowClient()
    versions = []

    try:
        for mv in client.search_model_versions(f"name='{MODEL_NAME}'"):
            run = client.get_run(mv.run_id)
            versions.append({
                "version":     mv.version,
                "stage":       mv.current_stage,
                "run_id":      mv.run_id[:8],
                "test_auc":    round(run.data.metrics.get("test_auc", 0), 4),
                "gini":        round(run.data.metrics.get("gini", 0), 4),
                "ks_statistic":round(run.data.metrics.get("ks_statistic", 0), 4),
                "created_at":  mv.creation_timestamp,
            })
    except Exception as e:
        logger.warning(f"Could not list versions: {e}")

    return pd.DataFrame(versions)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("\n── Step 1: Register best model ─────────────────────")
    version = register_best_model()

    print("\n── Step 2: Promote to Production ───────────────────")
    promote_to_production(version)

    print("\n── Step 3: Load Production model ───────────────────")
    model, version_str = load_production_model()
    print(f"Loaded: {version_str} | Type: {type(model).__name__}")

    print("\n── Step 4: List all versions ───────────────────────")
    df = list_model_versions()
    print(df.to_string(index=False))