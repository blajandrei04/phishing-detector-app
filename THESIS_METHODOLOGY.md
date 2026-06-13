# Methodology: Data Processing & Feature Engineering

This document outlines the methodology used to develop the machine learning component of the Phishing Detector web application, specifically focusing on data preprocessing, feature extraction, and model training.

## 1. Dataset Selection & Preprocessing

The model is trained on a large-scale, composite dataset (`phishing_site_urls.csv`). This dataset was chosen to ensure the model generalizes well to real-world URLs, moving beyond synthetic or extremely limited academic datasets.

### Label Normalization
The dataset contains raw URLs and a class label. During the ingestion phase, the labels are normalized into a binary classification format:
*   `bad` (Phishing/Malicious) → `1`
*   `good` (Legitimate) → `0`

## 2. Feature Engineering

Because raw URLs are unstructured text, they cannot be fed directly into standard tree-based models. A robust feature extraction pipeline (`backend/app/services/feature_extractor.py`) was engineered to compute 22 distinct numerical and binary features from every URL. 

These features are categorized into Lexical, Structural, and Heuristic features.

### 2.1 Basic Lexical Features
Basic structural counts that provide a baseline for the URL's shape.
1.  **`url_length`** (Numeric): The total character length of the complete URL string. Phishing URLs tend to be longer to obscure the actual payload or domain.
2.  **`hostname_length`** (Numeric): The character length of the parsed hostname.
3.  **`path_length`** (Numeric): The character length of the URL path (the portion after the domain).
4.  **`query_length`** (Numeric): The length of the query parameters.
5.  **`path_to_length_ratio`** (Float): The ratio of the path length to the total URL length. Helpful for identifying deep path structures hiding payloads.

### 2.2 Suspicious Pattern Flags (Binary Indicators)
Heuristic flags that check for known evasion techniques and common phishing patterns.
6.  **`has_https`**: Indicates if the URL uses the secure `https` scheme. While many phishing sites now use HTTPS, its absence on modern logins is highly suspicious.
7.  **`has_at_symbol`**: The presence of `@` in the URL. Browsers ignore everything before the `@`, a classic trick to obscure the actual destination domain.
8.  **`has_double_slash_redirect`**: Detects the `//` pattern within the path, often used for open redirects.
9.  **`has_hyphen_in_domain`**: Phishers frequently use hyphens for cybersquatting (e.g., `secure-paypal-login.com`).
10. **`is_shortener`**: Checks the domain against a known list of URL shorteners (e.g., `bit.ly`, `tinyurl.com`). Malicious actors use these to hide the final destination.
11. **`uses_ip_as_host`**: True if the hostname is a direct IP address (e.g., `http://192.168.1.1/login`) rather than a resolved domain name.
12. **`punycode_detected`**: Detects IDN homograph attacks via the presence of `xn--` in the hostname.
13. **`tld_type`**: Evaluates the Top-Level Domain (TLD). Returns 1 if the URL uses an exotic/suspicious TLD, or 0 if it uses a common, trusted TLD (e.g., `.com`, `.org`).

### 2.3 Advanced Structural Features
More complex metrics measuring the mathematical properties and depth of the URL.
14. **`subdomain_count`** (Numeric): The number of subdomains. Phishers often nest subdomains to appear legitimate (e.g., `login.apple.com.secure.xyz`).
15. **`digit_count`** (Numeric): The total number of numeric characters in the URL string.
16. **`special_char_count`** (Numeric): The total count of special characters (`@?&=%.-_~`). High volumes of special characters can indicate obfuscation.
17. **`num_directories`** (Numeric): The depth of the directory structure (number of `/` in the path).
18. **`num_parameters`** (Numeric): The number of query parameters passed in the URL.
19. **`url_entropy`** (Numeric): The Shannon Entropy of the URL string. High entropy indicates randomness, which is a strong signal for Domain Generation Algorithms (DGAs) or randomized obfuscation strings.
20. **`vowel_consonant_ratio`** (Float): The ratio of vowels to consonants in the hostname. An unnatural ratio is highly predictive of DGA-generated random domains.

### 2.4 Keyword & Brand Heuristics
21. **`has_suspicious_warning_words`** (Numeric): A count of sensitive keywords found anywhere in the URL (e.g., "login", "update", "verify", "secure", "account", "bank").
22. **`contains_brand_name`**: Binary indicator showing if a known brand (e.g., "paypal", "google", "apple") appears as bait in a domain/path where the SLD does not match the official brand.

## 3. Model Training Pipeline

The machine learning pipeline (`backend/train_model.py`) executes the following steps:

1.  **Ingestion & Splitting**: The dataset is loaded and split into a 70% Training / 30% Testing distribution using a stratified split to maintain the class balance.
2.  **Extraction**: The 16 features are extracted for all URLs in the dataset.
3.  **Training**: Three distinct classifier architectures are trained:
    *   **XGBoost Classifier** (Gradient Boosting Decision Trees)
    *   **Random Forest Classifier** (Bagged Decision Trees)
    *   **Logistic Regression** (Linear baseline, strictly scaled)
4.  **Evaluation**: Models are scored against Accuracy, Precision, Recall, F1, and AUC-ROC on the unseen test set.
5.  **Artifact Generation**: The pipeline outputs the best performing model (`xgb_opt.pkl`) alongside comprehensive visual plots (`roc_curves.png`, `feature_importance.png`, etc.) to the `artifacts/` directory for thesis documentation.
