"""
SHAP-based Explainable AI (XAI) service for phishing URL predictions.

Uses TreeExplainer (optimized for XGBoost) to compute per-feature
SHAP values that explain exactly *why* a given URL was classified
as phishing, suspicious, or legitimate.
"""
import logging
import numpy as np
import shap

logger = logging.getLogger(__name__)

# Human-readable labels for each feature
FEATURE_LABELS = {
    "url_length": "URL Length",
    "hostname_length": "Hostname Length",
    "path_length": "Path Length",
    "query_length": "Query String Length",
    "has_at_symbol": "Contains @ Symbol",
    "has_double_slash_redirect": "Double-Slash Redirect",
    "has_hyphen_in_domain": "Hyphen in Domain",
    "subdomain_count": "Subdomain Count",
    "digit_count": "Digit Count",
    "special_char_count": "Special Characters",
    "is_shortener": "URL Shortener Detected",
    "uses_ip_as_host": "IP Address as Host",
    "num_directories": "Directory Depth",
    "num_parameters": "Query Parameters",
    "url_entropy": "URL Entropy (Randomness)",
    "has_suspicious_warning_words": "Suspicious Keywords",
}

FEATURE_ORDER = [
    "url_length", "hostname_length", "path_length", "query_length",
    "has_at_symbol", "has_double_slash_redirect",
    "has_hyphen_in_domain", "subdomain_count", "digit_count",
    "special_char_count", "is_shortener", "uses_ip_as_host",
    "num_directories", "num_parameters", "url_entropy",
    "has_suspicious_warning_words"
]


class ShapExplainer:
    """Wraps a SHAP TreeExplainer around the trained XGBoost model."""

    def __init__(self):
        self.explainer = None

    def initialize(self, model) -> None:
        """Create a TreeExplainer from the given model.
        Must be called after the model is loaded."""
        if model is None:
            logger.warning("Cannot initialize SHAP explainer — model is None")
            return
        try:
            self.explainer = shap.TreeExplainer(model)
            logger.info("SHAP TreeExplainer initialized successfully")
        except Exception as exc:
            logger.exception(f"Failed to initialize SHAP explainer: {exc}")
            self.explainer = None

    def explain(self, features: dict) -> dict:
        """
        Compute SHAP values for a single prediction.

        Returns a dict with:
          - shap_values: list of {feature, label, value, shap_value, impact}
            sorted by absolute impact (descending)
          - base_value: the model's average prediction (expected value)
        """
        if self.explainer is None:
            return {"shap_values": [], "base_value": 0.5}

        # Build the feature vector in the correct order
        x = np.array([[features.get(name, 0) for name in FEATURE_ORDER]])

        try:
            shap_values = self.explainer.shap_values(x)

            # TreeExplainer can return a list (per class) or a 2D array
            if isinstance(shap_values, list):
                # For binary classification, take class 1 (phishing)
                sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
            elif shap_values.ndim == 3:
                sv = shap_values[0, :, 1]
            else:
                sv = shap_values[0]

            base_value = self.explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = float(base_value[1]) if len(base_value) > 1 else float(base_value[0])
            else:
                base_value = float(base_value)

            # Build the explanation list
            explanations = []
            for i, name in enumerate(FEATURE_ORDER):
                shap_val = float(sv[i])
                explanations.append({
                    "feature": name,
                    "label": FEATURE_LABELS.get(name, name),
                    "value": features.get(name, 0),
                    "shap_value": round(shap_val, 4),
                    "impact": "increases_risk" if shap_val > 0 else "decreases_risk"
                })

            # Sort by absolute SHAP value (most important first)
            explanations.sort(key=lambda e: abs(e["shap_value"]), reverse=True)

            return {
                "shap_values": explanations,
                "base_value": round(base_value, 4)
            }

        except Exception as exc:
            logger.exception(f"SHAP explanation failed: {exc}")
            return {"shap_values": [], "base_value": 0.5}
