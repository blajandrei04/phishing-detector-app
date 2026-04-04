from pathlib import Path
import logging
import joblib


logger = logging.getLogger(__name__)


class ModelLoader:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load(self) -> None:
        path = Path(self.model_path)
        if not path.exists():
            logger.warning(f"Model file not found at {self.model_path}. Using fallback scoring.")
            self.model = None
            return

        try:
            self.model = joblib.load(path)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as exc:
            logger.exception(f"Failed to load model: {exc}")
            self.model = None

    def predict_score(self, features: dict) -> float:
        # Fallback if model unavailable
        if self.model is None:
            return 0.42

        # Convert feature dict to stable ordered vector
        feature_order = [
            "url_length",
            "hostname_length",
            "path_length",
            "query_length",
            "has_https",
            "has_at_symbol",
            "has_double_slash_redirect",
            "has_hyphen_in_domain",
            "subdomain_count",
            "digit_count",
            "special_char_count",
            "is_shortener",
            "uses_ip_as_host",
        ]
        x = [[features.get(name, 0) for name in feature_order]]

        # Preferred path for classifiers with probabilities
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(x)[0]
            # Binary assumption: class 1 = phishing probability
            if len(proba) > 1:
                return float(proba[1])
            return float(proba[0])

        # Fallback for models without predict_proba
        pred = self.model.predict(x)[0]
        return float(pred)