# Phishing Detector — Python/FastAPI Backend

A high-performance asynchronous REST API built with **FastAPI** that serves real-time machine learning predictions, extracts URL features, performs dynamic network assessments, and manages admin controls.

---

## 🛠️ Technology Stack

*   **FastAPI**: Asynchronous Python web framework for lightning-fast RESTful APIs.
*   **XGBoost Classifier**: Gradient boosted decision trees model trained for high accuracy phishing prediction.
*   **SHAP (SHapley Additive exPlanations)**: TreeExplainer engine providing mathematically rigorous explainability (XAI) for predictions on the fly.
*   **SQLAlchemy & SQLite**: Light-weight database schema definition and object-relational mapping (ORM) for session tracking, scan history logs, and administrator feedback database.
*   **PyJWT & BCrypt**: Secure password hashing and JSON Web Token authentication with role-based restrictions.

---

## 📂 Directory Structure

```
backend/
├── app/
│   ├── api/                   # Router endpoints (health, analyze, history, stats, auth)
│   ├── core/                  # Configurations (settings, logging, security, JWT helper tokens)
│   ├── db/                    # SQLite connection, Session maker, SQLAlchemy models
│   ├── models/                # Pydantic schemas for request/response serialization
│   ├── services/              # Core business services
│   │   ├── dynamic_analyzer.py   # Real-time DNS lookup, SSL check, and WHOIS parser
│   │   ├── feature_extractor.py  # 22-lexical & heuristic feature engineering rules
│   │   ├── model_loader.py       # Thread-safe XGBoost classifier loading & prediction
│   │   └── shap_explainer.py     # TreeExplainer wrapper mapping feature contribution weights
│   └── main.py                # App entry point, CORS settings, database initializations
├── artifacts/                 # Serialized model (.pkl), evaluation figures, metadata JSON
├── datasets/                  # Model training data (phishing_site_urls.csv)
├── tests/                     # Test suite (unit, integration, and endpoint tests)
├── train_model.py             # Stratified 5-fold CV hyperparameter tuning & evaluation script
└── requirements.txt           # Pinned python project dependencies
```

---

## 🧪 Feature Extraction & Predictions

When a URL is submitted, the API triggers a two-phase assessment:

### Phase 1: Machine Learning & SHAP
1.  **Lexical Feature Engineering**: Extracts 22 mathematical, structural, and keyword features from the URL string.
2.  **Inference**: Feeds the vector into the trained XGBoost model to compute a threat probability (risk score between 0.0 and 1.0).
3.  **Explainability**: Uses the SHAP TreeExplainer to compute exact Shapley values, highlighting which features increased or decreased the threat risk.

### Phase 2: Live Active Inspection
1.  **DNS Host Lookup**: Resolves the hostname to check active IP routing.
2.  **SSL Certificate Handshake**: Probes port 443, performs an SSL handshake, checks validity, and extracts details (Common Name, Issuer, expiration date).
3.  **WHOIS Age Retrieval**: Connects directly to authoritative registrar WHOIS servers on port 43, retrieves raw registration text, and parses creation dates to determine domain age.

---

## 🚀 Setup & Run Instructions

### Prerequisites
*   **Python**: Version 3.10 or 3.11+
*   **Virtualenv**: Recommended

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Pinned Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload
```
*   **Local URL**: `http://localhost:8000`
*   **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`

### 4. Run Model Training and Tuning Pipeline
To retrain the model, perform hyperparameter optimization, and output new visualization plots:
```bash
python train_model.py
```

### 5. Running the Test Suite
```bash
pytest
```
*   Configuration parameters are located in `pytest.ini`.
*   Includes unit tests for feature extractors, active scanners, and integration checks for the model training lifecycle.
