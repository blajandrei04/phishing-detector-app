"""
Model Training & Comparison Script for Phishing Detector
=========================================================
Trains three classifiers (XGBoost, Random Forest, Logistic Regression),
compares their performance, and saves publication-ready evaluation
artifacts to the artifacts/ directory.

v2 Enhancements:
  - 22 features (was 16) including has_https, tld_type, brand detection, etc.
  - Stratified 5-Fold Cross-Validation with RandomizedSearchCV for XGBoost
  - Automatic class imbalance handling via scale_pos_weight
  - Model versioning with model_metadata.json

Output files:
  artifacts/xgb_opt.pkl                 - Best model (XGBoost) for API
  artifacts/model_metadata.json         - Model versioning metadata
  artifacts/model_comparison.png        - Side-by-side metrics bar chart
  artifacts/confusion_matrices.png      - Confusion matrices for all models
  artifacts/roc_curves.png              - ROC curves overlay
  artifacts/precision_recall_curves.png - Precision-Recall curves overlay
  artifacts/feature_importance.png      - XGBoost feature importance
  artifacts/evaluation_report.md        - Full text report for thesis
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
from datetime import datetime

from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_score
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from app.services.feature_extractor import extract_features

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
ARTIFACTS_DIR = "artifacts"
DATASET_PATH = "datasets/phishing_site_urls.csv"
RANDOM_STATE = 42
TEST_SIZE = 0.3
CV_FOLDS = 5
RANDOMIZED_SEARCH_ITER = 30

# Style
if HAS_PLOTTING:
    sns.set_theme(style="whitegrid", font_scale=1.1)
COLORS = {
    "xgboost": "#2563eb",
    "random_forest": "#22c55e",
    "logistic_regression": "#f59e0b"
}

# 22-feature order (v2)
FEATURE_ORDER = [
    "url_length", "hostname_length", "path_length", "query_length",
    "has_https", "has_at_symbol", "has_double_slash_redirect",
    "has_hyphen_in_domain", "subdomain_count", "digit_count",
    "special_char_count", "is_shortener", "uses_ip_as_host",
    "num_directories", "num_parameters", "url_entropy",
    "has_suspicious_warning_words",
    # v2 features
    "tld_type", "vowel_consonant_ratio", "contains_brand_name",
    "punycode_detected", "path_to_length_ratio",
]

LABELS_MAP = {
    "url_length": "URL Length", "hostname_length": "Hostname Length",
    "path_length": "Path Length", "query_length": "Query Length",
    "has_https": "HTTPS Protocol", "has_at_symbol": "@ Symbol",
    "has_double_slash_redirect": "Double Slash",
    "has_hyphen_in_domain": "Hyphen in Domain", "subdomain_count": "Subdomain Count",
    "digit_count": "Digit Count", "special_char_count": "Special Chars",
    "is_shortener": "URL Shortener", "uses_ip_as_host": "IP as Host",
    "num_directories": "Directory Depth", "num_parameters": "Query Params",
    "url_entropy": "URL Entropy", "has_suspicious_warning_words": "Suspicious Keywords",
    "tld_type": "Exotic TLD", "vowel_consonant_ratio": "Vowel/Consonant Ratio",
    "contains_brand_name": "Brand Name Detected", "punycode_detected": "Punycode (IDN)",
    "path_to_length_ratio": "Path/Length Ratio",
}

fallback_data = [
    ("https://www.google.com", 0), ("https://github.com", 0), ("https://en.wikipedia.org/wiki/Main_Page", 0),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0), ("https://stackoverflow.com/questions", 0),
    ("https://www.microsoft.com/en-us/", 0), ("https://www.apple.com", 0), ("https://aws.amazon.com/", 0),
    ("http://login-update-account-paypal.com", 1), ("http://192.168.1.1/login.php", 1),
    ("http://bit.ly/malicious-link", 1), ("https://secure-update-apple-id.xyz/login?token=1293812", 1),
    ("http://www.bankofamerica.com.update.security.fraud.com/login", 1), ("http://172.16.0.10/admin/index.html", 1),
    ("http://tinyurl.com/free-money", 1), ("https://netflix-payment-update-failed.net", 1),
]


def load_data() -> tuple[list[str], list[int]]:
    if os.path.exists(DATASET_PATH):
        print(f"  Loading dataset from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)
        url_col = "URL" if "URL" in df.columns else df.columns[0]
        label_col = "Label" if "Label" in df.columns else df.columns[1]
        df[label_col] = df[label_col].apply(lambda x: 1 if str(x).strip().lower() == 'bad' else 0)
        print(f"  Loaded {len(df):,} URLs ({df[label_col].sum():,} phishing, {(df[label_col]==0).sum():,} legitimate)")
        return df[url_col].tolist(), df[label_col].tolist()
    else:
        print("  No CSV found — using 16-URL fallback dataset.")
        return [u[0] for u in fallback_data], [u[1] for u in fallback_data]


def extract_all_features(urls: list[str]) -> tuple[pd.DataFrame, list[str]]:
    print(f"  Extracting features for {len(urls):,} URLs...")
    features_list = [extract_features(str(u)) for u in urls]
    df = pd.DataFrame(features_list)
    return df[FEATURE_ORDER], FEATURE_ORDER


# ──────────────────────────────────────────────
# Model definitions
# ──────────────────────────────────────────────
def get_models(scale_pos_weight: float = 1.0) -> dict:
    """Return baseline models. XGBoost uses scale_pos_weight for class imbalance."""
    return {
        "XGBoost": XGBClassifier(
            n_estimators=300, max_depth=7, learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE, n_jobs=-1, eval_metric='logloss'
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=15, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=2000, random_state=RANDOM_STATE, n_jobs=-1))
        ])
    }


def tune_xgboost(X_train, y_train, scale_pos_weight: float = 1.0) -> tuple:
    """
    Hyperparameter tuning with RandomizedSearchCV + Stratified K-Fold.
    Returns (best_model, best_params, cv_results_dict).
    """
    print("\n  [CV] Running Stratified 5-Fold Cross-Validation with RandomizedSearchCV...")
    print(f"  [CV] Testing {RANDOMIZED_SEARCH_ITER} random hyperparameter combinations...")

    param_distributions = {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [3, 5, 7, 9, 11],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'min_child_weight': [1, 3, 5],
        'gamma': [0, 0.1, 0.3],
    }

    base_xgb = XGBClassifier(
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        eval_metric='logloss',
    )

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=param_distributions,
        n_iter=RANDOMIZED_SEARCH_ITER,
        scoring='roc_auc',
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    best_params = search.best_params_

    # Collect CV scores for reporting
    cv_results = {
        "mean_auc": float(search.best_score_),
        "std_auc": float(search.cv_results_['std_test_score'][search.best_index_]),
        "mean_train_auc": float(search.cv_results_['mean_train_score'][search.best_index_]),
        "all_fold_scores": [float(s) for s in cross_val_score(
            best_model, X_train, y_train, cv=cv, scoring='roc_auc'
        )],
    }

    print(f"\n  [CV] Best AUC-ROC: {cv_results['mean_auc']:.4f} ± {cv_results['std_auc']:.4f}")
    print(f"  [CV] Best parameters: {best_params}")

    return best_model, best_params, cv_results


# ──────────────────────────────────────────────
# Evaluation
# ──────────────────────────────────────────────
def evaluate_models(models: dict, X_train: np.ndarray | pd.DataFrame, X_test: np.ndarray | pd.DataFrame, y_train: np.ndarray, y_test: np.ndarray) -> dict:
    results = {}
    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        results[name] = {
            "model": model,
            "y_pred": y_pred,
            "y_prob": y_prob,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "auc_roc": roc_auc_score(y_test, y_prob),
            "report": classification_report(y_test, y_pred, output_dict=True)
        }
        print(f"    Accuracy: {results[name]['accuracy']*100:.2f}%  |  AUC: {results[name]['auc_roc']:.4f}")
    return results


# ──────────────────────────────────────────────
# Visualization Functions
# ──────────────────────────────────────────────
def plot_model_comparison(results: dict) -> None:
    """Bar chart comparing all models across key metrics."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_model_comparison.")
        return
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc_roc']
    labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
    model_names = list(results.keys())
    colors = [COLORS.get(n.lower().replace(" ", "_"), "#888") for n in model_names]

    x = np.arange(len(metrics))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, name in enumerate(model_names):
        values = [results[name][m] for m in metrics]
        bars = ax.bar(x + i * width, values, width, label=name, color=colors[i],
                      edgecolor='white', linewidth=1.5, alpha=0.9)
        # Value labels on top
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold', pad=15)
    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, fontweight='bold')
    ax.set_ylim(0, 1.12)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/model_comparison.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved model_comparison.png")


def plot_confusion_matrices(results: dict, y_test: np.ndarray) -> None:
    """Side-by-side confusion matrices."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_confusion_matrices.")
        return
    model_names = list(results.keys())
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for i, name in enumerate(model_names):
        cm = confusion_matrix(y_test, results[name]['y_pred'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i],
                    xticklabels=['Legitimate', 'Phishing'],
                    yticklabels=['Legitimate', 'Phishing'],
                    cbar=False, linewidths=0.5, linecolor='white')
        axes[i].set_title(name, fontsize=13, fontweight='bold', pad=10)
        axes[i].set_ylabel('Actual' if i == 0 else '', fontweight='bold')
        axes[i].set_xlabel('Predicted', fontweight='bold')

    fig.suptitle('Confusion Matrices', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/confusion_matrices.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved confusion_matrices.png")


def plot_roc_curves(results: dict, y_test: np.ndarray) -> None:
    """Overlaid ROC curves."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_roc_curves.")
        return
    fig, ax = plt.subplots(figsize=(8, 7))
    colors_list = [COLORS.get(n.lower().replace(" ", "_"), "#888") for n in results.keys()]

    for (name, data), color in zip(results.items(), colors_list):
        fpr, tpr, _ = roc_curve(y_test, data['y_prob'])
        ax.plot(fpr, tpr, color=color, lw=2.5,
                label=f'{name} (AUC = {data["auc_roc"]:.4f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='Random Baseline')
    ax.set_xlabel('False Positive Rate', fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontweight='bold')
    ax.set_title('ROC Curves — Model Comparison', fontsize=16, fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.05])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/roc_curves.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved roc_curves.png")


def plot_precision_recall_curves(results: dict, y_test: np.ndarray) -> None:
    """Overlaid precision-recall curves."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_precision_recall_curves.")
        return
    fig, ax = plt.subplots(figsize=(8, 7))
    colors_list = [COLORS.get(n.lower().replace(" ", "_"), "#888") for n in results.keys()]

    for (name, data), color in zip(results.items(), colors_list):
        precision, recall, _ = precision_recall_curve(y_test, data['y_prob'])
        ax.plot(recall, precision, color=color, lw=2.5, label=name)

    ax.set_xlabel('Recall', fontweight='bold')
    ax.set_ylabel('Precision', fontweight='bold')
    ax.set_title('Precision-Recall Curves — Model Comparison', fontsize=16, fontweight='bold', pad=15)
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.05])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/precision_recall_curves.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved precision_recall_curves.png")


def plot_feature_importance(model: XGBClassifier, feature_names: list[str]) -> None:
    """XGBoost feature importance horizontal bar chart."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_feature_importance.")
        return
    importances = model.feature_importances_
    indices = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(10, 9))
    labels = [LABELS_MAP.get(feature_names[i], feature_names[i]) for i in indices]
    values = importances[indices]

    # Color gradient
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(values)))

    bars = ax.barh(range(len(indices)), values, color=colors, edgecolor='white', linewidth=0.5)

    # Value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9, fontweight='bold')

    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(labels, fontweight='500')
    ax.set_xlabel('Feature Importance (Gain)', fontweight='bold')
    ax.set_title('XGBoost — Feature Importance Ranking (22 Features)', fontsize=16, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/feature_importance.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved feature_importance.png")


def plot_cv_scores(cv_results: dict) -> None:
    """Bar chart of per-fold AUC-ROC scores from cross-validation."""
    if not HAS_PLOTTING:
        print("  [SKIP] Matplotlib/Seaborn not installed, skipping plot_cv_scores.")
        return
    fold_scores = cv_results.get("all_fold_scores", [])
    if not fold_scores:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    folds = [f"Fold {i+1}" for i in range(len(fold_scores))]
    colors = ['#2563eb' if s >= cv_results['mean_auc'] else '#93c5fd' for s in fold_scores]

    bars = ax.bar(folds, fold_scores, color=colors, edgecolor='white', linewidth=1.5)
    ax.axhline(y=cv_results['mean_auc'], color='#ef4444', linestyle='--', lw=2,
               label=f"Mean AUC = {cv_results['mean_auc']:.4f} ± {cv_results['std_auc']:.4f}")

    for bar, val in zip(bars, fold_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('AUC-ROC Score', fontweight='bold')
    ax.set_title('Stratified 5-Fold Cross-Validation Results', fontsize=16, fontweight='bold', pad=15)
    ax.set_ylim(min(fold_scores) - 0.02, 1.01)
    ax.legend(fontsize=12, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{ARTIFACTS_DIR}/cv_fold_scores.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] Saved cv_fold_scores.png")


def save_model_metadata(
    best_name: str, best_params: dict, cv_results: dict,
    test_metrics: dict, feature_names: list[str],
    dataset_size: int, class_dist: dict, scale_pos_weight: float
) -> None:
    """Save model versioning metadata alongside the model."""
    metadata = {
        "model_name": best_name,
        "trained_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "dataset_size": dataset_size,
        "n_features": len(feature_names),
        "feature_order": feature_names,
        "best_params": best_params,
        "cv_scores": cv_results,
        "test_metrics": {
            "accuracy": test_metrics.get("accuracy", 0),
            "precision": test_metrics.get("precision", 0),
            "recall": test_metrics.get("recall", 0),
            "f1": test_metrics.get("f1", 0),
            "auc_roc": test_metrics.get("auc_roc", 0),
        },
        "class_distribution": class_dist,
        "scale_pos_weight": scale_pos_weight,
        "cv_folds": CV_FOLDS,
        "randomized_search_iterations": RANDOMIZED_SEARCH_ITER,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
    }

    path = f"{ARTIFACTS_DIR}/model_metadata.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"  [OK] Saved model_metadata.json")


def generate_report(
    results: dict, feature_names: list[str], xgb_model: XGBClassifier,
    dataset_size: int, cv_results: dict = None, best_params: dict = None,
    class_dist: dict = None, scale_pos_weight: float = 1.0
) -> None:
    """Generate a Markdown evaluation report for the thesis."""
    best_name = max(results.keys(), key=lambda k: results[k]['auc_roc'])
    best = results[best_name]

    report = f"""# Model Evaluation Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dataset:** {dataset_size:,} URLs (phishing_site_urls.csv)
**Train/Test Split:** {int((1-TEST_SIZE)*100)}% / {int(TEST_SIZE*100)}%
**Random State:** {RANDOM_STATE}
**Features:** {len(feature_names)} (v2 — includes has_https, TLD type, brand detection, etc.)

---

## 1. Model Comparison Summary

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
"""
    for name, data in results.items():
        marker = " ✅" if name == best_name else ""
        report += f"| {name}{marker} | {data['accuracy']:.4f} | {data['precision']:.4f} | {data['recall']:.4f} | {data['f1']:.4f} | {data['auc_roc']:.4f} |\n"

    report += f"""
**Best Model: {best_name}** (selected based on highest AUC-ROC score)
"""

    # CV Results section
    if cv_results:
        report += f"""
## 2. Cross-Validation Results (Stratified {CV_FOLDS}-Fold)

XGBoost hyperparameters were tuned using **RandomizedSearchCV** with {RANDOMIZED_SEARCH_ITER} iterations
across a stratified {CV_FOLDS}-fold cross-validation scheme.

| Metric | Value |
|--------|-------|
| Mean AUC-ROC | {cv_results['mean_auc']:.4f} |
| Std AUC-ROC | ± {cv_results['std_auc']:.4f} |
| Mean Train AUC | {cv_results.get('mean_train_auc', 'N/A')} |

### Per-Fold Scores

| Fold | AUC-ROC |
|------|---------|
"""
        for i, score in enumerate(cv_results.get('all_fold_scores', []), 1):
            report += f"| Fold {i} | {score:.4f} |\n"

    # Best parameters section
    if best_params:
        report += f"""
### Tuned Hyperparameters

| Parameter | Value |
|-----------|-------|
"""
        for param, value in sorted(best_params.items()):
            report += f"| {param} | {value} |\n"

    # Class imbalance section
    if class_dist:
        report += f"""
## 3. Class Distribution & Imbalance Handling

| Class | Count | Proportion |
|-------|-------|------------|
| Legitimate (0) | {class_dist.get('legitimate', 0):,} | {class_dist.get('legitimate', 0)/dataset_size*100:.1f}% |
| Phishing (1) | {class_dist.get('phishing', 0):,} | {class_dist.get('phishing', 0)/dataset_size*100:.1f}% |

**scale_pos_weight = {scale_pos_weight:.4f}** (ratio of negative to positive samples, applied to XGBoost)
"""
    else:
        report += "\n## 3. Why " + best_name + "?\n\n"

    report += f"""
## 4. Why {best_name}?

{best_name} was selected as the production model because:
- **Highest AUC-ROC ({best['auc_roc']:.4f})** — demonstrates superior discrimination between phishing and legitimate URLs across all threshold values.
- **Strong F1-Score ({best['f1']:.4f})** — indicates an excellent balance between precision (minimizing false alarms) and recall (catching actual threats).
- **Tree-based architecture** — naturally handles non-linear feature interactions (e.g., the combination of IP-as-host + suspicious keywords is more indicative than either alone).
- **SHAP compatibility** — TreeExplainer provides exact, polynomial-time SHAP values for explainability.
"""
    if cv_results:
        report += f"- **Cross-validated** — {CV_FOLDS}-fold stratified CV confirms the model generalizes well (AUC: {cv_results['mean_auc']:.4f} ± {cv_results['std_auc']:.4f}).\n"

    report += f"""
## 5. Feature Importance (Top 10)

| Rank | Feature | Importance |
|------|---------|------------|
"""
    importances = xgb_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for rank, idx in enumerate(indices[:10], 1):
        name = LABELS_MAP.get(feature_names[idx], feature_names[idx])
        report += f"| {rank} | {name} | {importances[idx]:.4f} |\n"

    report += f"""
## 6. Extracted Features ({len(feature_names)} total)

The following URL-derived features were engineered for the ML pipeline:

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | url_length | Numeric | Total character count of the URL |
| 2 | hostname_length | Numeric | Length of the hostname portion |
| 3 | path_length | Numeric | Length of the URL path |
| 4 | query_length | Numeric | Length of query string |
| 5 | has_https | Binary | Whether the URL uses HTTPS protocol |
| 6 | has_at_symbol | Binary | Presence of @ in URL (redirect trick) |
| 7 | has_double_slash_redirect | Binary | // redirect pattern detected |
| 8 | has_hyphen_in_domain | Binary | Hyphen in hostname (cybersquatting) |
| 9 | subdomain_count | Numeric | Number of subdomains |
| 10 | digit_count | Numeric | Count of digits in URL |
| 11 | special_char_count | Numeric | Count of special characters |
| 12 | is_shortener | Binary | Known URL shortener service |
| 13 | uses_ip_as_host | Binary | IP address used instead of domain |
| 14 | num_directories | Numeric | Directory depth in path |
| 15 | num_parameters | Numeric | Number of query parameters |
| 16 | url_entropy | Numeric | Shannon entropy (randomness measure) |
| 17 | has_suspicious_warning_words | Numeric | Count of phishing keywords |
| 18 | tld_type | Binary | Exotic TLD vs common TLD (.com, .org) |
| 19 | vowel_consonant_ratio | Float | V/C ratio in hostname (DGA detection) |
| 20 | contains_brand_name | Binary | Known brand name detected in URL |
| 21 | punycode_detected | Binary | IDN homograph attack indicator (xn--) |
| 22 | path_to_length_ratio | Float | Normalized path depth by URL length |

## 7. Visualization Artifacts

- `model_comparison.png` — Bar chart of all metrics across three models
- `confusion_matrices.png` — Side-by-side confusion matrices
- `roc_curves.png` — Overlaid ROC curves with AUC values
- `precision_recall_curves.png` — Precision-Recall curves
- `feature_importance.png` — XGBoost feature importance ranking (22 features)
- `cv_fold_scores.png` — Per-fold AUC-ROC scores from cross-validation
- `model_metadata.json` — Model versioning metadata with hyperparameters
"""
    with open(f"{ARTIFACTS_DIR}/evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("  [OK] Saved evaluation_report.md")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main() -> None:
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    print("=" * 60)
    print("  PHISHING DETECTOR — MODEL TRAINING & EVALUATION (v2)")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/8] Loading Data...")
    urls, labels = load_data()
    dataset_size = len(urls)

    # Step 2: Extract features (22 features)
    print("\n[2/8] Feature Extraction (22 features)...")
    X, feature_names = extract_all_features(urls)
    y = np.array(labels)

    # Compute class distribution and imbalance weight
    n_positive = int(np.sum(y == 1))
    n_negative = int(np.sum(y == 0))
    scale_pos_weight = n_negative / n_positive if n_positive > 0 else 1.0
    class_dist = {"legitimate": n_negative, "phishing": n_positive}
    print(f"  Class distribution: {n_negative:,} legitimate, {n_positive:,} phishing")
    print(f"  scale_pos_weight = {scale_pos_weight:.4f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"  Train: {len(X_train):,} | Test: {len(X_test):,}")

    # Step 3: Hyperparameter tuning via Cross-Validation
    print("\n[3/8] Hyperparameter Tuning (Stratified 5-Fold CV)...")
    tuned_xgb, best_params, cv_results = tune_xgboost(X_train, y_train, scale_pos_weight)

    # Step 4: Train all models (using the tuned XGBoost)
    print("\n[4/8] Training All Models for Comparison...")
    models = get_models(scale_pos_weight)
    # Replace the default XGBoost with the tuned version
    models["XGBoost"] = tuned_xgb
    results = evaluate_models(models, X_train, X_test, y_train, y_test)

    # Step 5: Save best model + metadata
    print("\n[5/8] Saving Best Model & Metadata...")
    best_name = max(results.keys(), key=lambda k: results[k]['auc_roc'])
    best_model = results[best_name]['model']
    model_path = f"{ARTIFACTS_DIR}/xgb_opt.pkl"
    joblib.dump(best_model, model_path)
    print(f"  [OK] Saved {best_name} to {model_path}")

    # Save model metadata for versioning
    save_model_metadata(
        best_name=best_name,
        best_params=best_params,
        cv_results=cv_results,
        test_metrics=results[best_name],
        feature_names=feature_names,
        dataset_size=dataset_size,
        class_dist=class_dist,
        scale_pos_weight=scale_pos_weight,
    )

    # Step 6: Generate visualizations
    print("\n[6/8] Generating Visualizations...")
    plot_model_comparison(results)
    plot_confusion_matrices(results, y_test)
    plot_roc_curves(results, y_test)
    plot_precision_recall_curves(results, y_test)
    plot_feature_importance(results["XGBoost"]["model"], feature_names)
    plot_cv_scores(cv_results)

    # Step 7: Generate report
    print("\n[7/8] Generating Evaluation Report...")
    generate_report(
        results, feature_names, results["XGBoost"]["model"], dataset_size,
        cv_results=cv_results, best_params=best_params,
        class_dist=class_dist, scale_pos_weight=scale_pos_weight
    )

    # Step 8: Final summary
    print("\n[8/8] Done!")
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE! (v2)")
    print("=" * 60)
    print(f"\n  Best model: {best_name}")
    print(f"  Accuracy:   {results[best_name]['accuracy']*100:.2f}%")
    print(f"  AUC-ROC:    {results[best_name]['auc_roc']:.4f}")
    if cv_results:
        print(f"  CV AUC-ROC: {cv_results['mean_auc']:.4f} ± {cv_results['std_auc']:.4f}")
    print(f"  Features:   {len(feature_names)}")
    print(f"\n  All artifacts saved to {ARTIFACTS_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
