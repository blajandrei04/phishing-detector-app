# Model Evaluation Report
**Generated:** 2026-04-18 22:37:30
**Dataset:** 549,346 URLs (phishing_site_urls.csv)
**Train/Test Split:** 70% / 30%
**Random State:** 42

---

## 1. Model Comparison Summary

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| XGBoost ✅ | 0.8871 | 0.8735 | 0.7056 | 0.7807 | 0.9370 |
| Random Forest | 0.8730 | 0.9082 | 0.6164 | 0.7344 | 0.9276 |
| Logistic Regression | 0.7985 | 0.8606 | 0.3487 | 0.4963 | 0.7677 |

**Best Model: XGBoost** (selected based on highest AUC-ROC score)

## 2. Why XGBoost?

XGBoost was selected as the production model because:
- **Highest AUC-ROC (0.9370)** — demonstrates superior discrimination between phishing and legitimate URLs across all threshold values.
- **Strong F1-Score (0.7807)** — indicates an excellent balance between precision (minimizing false alarms) and recall (catching actual threats).
- **Tree-based architecture** — naturally handles non-linear feature interactions (e.g., the combination of IP-as-host + suspicious keywords is more indicative than either alone).
- **SHAP compatibility** — TreeExplainer provides exact, polynomial-time SHAP values for explainability.

## 3. Feature Importance (Top 10)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | IP as Host | 0.3996 |
| 2 | Suspicious Keywords | 0.3135 |
| 3 | @ Symbol | 0.0472 |
| 4 | Query Length | 0.0326 |
| 5 | Digit Count | 0.0296 |
| 6 | Directory Depth | 0.0285 |
| 7 | Path Length | 0.0260 |
| 8 | Subdomain Count | 0.0234 |
| 9 | URL Shortener | 0.0203 |
| 10 | Hyphen in Domain | 0.0198 |

## 4. Extracted Features (16 total)

The following URL-derived features were engineered for the ML pipeline:

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | url_length | Numeric | Total character count of the URL |
| 2 | hostname_length | Numeric | Length of the hostname portion |
| 3 | path_length | Numeric | Length of the URL path |
| 4 | query_length | Numeric | Length of query string |
| 5 | has_at_symbol | Binary | Presence of @ in URL (redirect trick) |
| 6 | has_double_slash_redirect | Binary | // redirect pattern detected |
| 7 | has_hyphen_in_domain | Binary | Hyphen in hostname (cybersquatting) |
| 8 | subdomain_count | Numeric | Number of subdomains |
| 9 | digit_count | Numeric | Count of digits in URL |
| 10 | special_char_count | Numeric | Count of special characters |
| 11 | is_shortener | Binary | Known URL shortener service |
| 12 | uses_ip_as_host | Binary | IP address used instead of domain |
| 13 | num_directories | Numeric | Directory depth in path |
| 14 | num_parameters | Numeric | Number of query parameters |
| 15 | url_entropy | Numeric | Shannon entropy (randomness measure) |
| 16 | has_suspicious_warning_words | Numeric | Count of phishing keywords |

## 5. Visualization Artifacts

- `model_comparison.png` — Bar chart of all metrics across three models
- `confusion_matrices.png` — Side-by-side confusion matrices
- `roc_curves.png` — Overlaid ROC curves with AUC values
- `precision_recall_curves.png` — Precision-Recall curves
- `feature_importance.png` — XGBoost feature importance ranking
