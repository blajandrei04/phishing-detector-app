# Model Evaluation Report
**Generated:** 2026-06-12 13:19:14
**Dataset:** 549,346 URLs (phishing_site_urls.csv)
**Train/Test Split:** 70% / 30%
**Random State:** 42
**Features:** 22 (v2 — includes has_https, TLD type, brand detection, etc.)

---

## 1. Model Comparison Summary

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| XGBoost ✅ | 0.9142 | 0.8297 | 0.8790 | 0.8536 | 0.9682 |
| Random Forest | 0.8939 | 0.9085 | 0.6976 | 0.7892 | 0.9427 |
| Logistic Regression | 0.8336 | 0.8407 | 0.5128 | 0.6370 | 0.8311 |

**Best Model: XGBoost** (selected based on highest AUC-ROC score)

## 2. Cross-Validation Results (Stratified 5-Fold)

XGBoost hyperparameters were tuned using **RandomizedSearchCV** with 30 iterations
across a stratified 5-fold cross-validation scheme.

| Metric | Value |
|--------|-------|
| Mean AUC-ROC | 0.9676 |
| Std AUC-ROC | ± 0.0003 |
| Mean Train AUC | 0.9881062969277246 |

### Per-Fold Scores

| Fold | AUC-ROC |
|------|---------|
| Fold 1 | 0.9669 |
| Fold 2 | 0.9671 |
| Fold 3 | 0.9679 |
| Fold 4 | 0.9678 |
| Fold 5 | 0.9676 |

### Tuned Hyperparameters

| Parameter | Value |
|-----------|-------|
| colsample_bytree | 0.9 |
| gamma | 0 |
| learning_rate | 0.1 |
| max_depth | 9 |
| min_child_weight | 1 |
| n_estimators | 500 |
| subsample | 0.7 |

## 3. Class Distribution & Imbalance Handling

| Class | Count | Proportion |
|-------|-------|------------|
| Legitimate (0) | 392,924 | 71.5% |
| Phishing (1) | 156,422 | 28.5% |

**scale_pos_weight = 2.5119** (ratio of negative to positive samples, applied to XGBoost)

## 4. Why XGBoost?

XGBoost was selected as the production model because:
- **Highest AUC-ROC (0.9682)** — demonstrates superior discrimination between phishing and legitimate URLs across all threshold values.
- **Strong F1-Score (0.8536)** — indicates an excellent balance between precision (minimizing false alarms) and recall (catching actual threats).
- **Tree-based architecture** — naturally handles non-linear feature interactions (e.g., the combination of IP-as-host + suspicious keywords is more indicative than either alone).
- **SHAP compatibility** — TreeExplainer provides exact, polynomial-time SHAP values for explainability.
- **Cross-validated** — 5-fold stratified CV confirms the model generalizes well (AUC: 0.9676 ± 0.0003).

## 5. Feature Importance (Top 10)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | Suspicious Keywords | 0.2485 |
| 2 | Exotic TLD | 0.2249 |
| 3 | Brand Name Detected | 0.1473 |
| 4 | @ Symbol | 0.0808 |
| 5 | Query Length | 0.0322 |
| 6 | Digit Count | 0.0298 |
| 7 | Directory Depth | 0.0283 |
| 8 | IP as Host | 0.0255 |
| 9 | Subdomain Count | 0.0226 |
| 10 | URL Shortener | 0.0220 |

## 6. Extracted Features (22 total)

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
