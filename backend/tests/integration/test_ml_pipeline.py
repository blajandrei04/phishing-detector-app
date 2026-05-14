import os
import sys
import numpy as np
import pandas as pd
import tempfile
from unittest.mock import patch

# Ensure backend root is in the path to import train_model
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from train_model import (
    extract_all_features,
    get_models,
    evaluate_models,
    fallback_data,
    generate_report
)
from sklearn.model_selection import train_test_split

def test_ml_pipeline_functions_end_to_end():
    """
    Integration test to verify that the ML pipeline can extract features,
    train all three models, and compute evaluation metrics successfully
    on a small mock dataset.
    """
    # 1. Use the fallback data from train_model.py as our mock dataset
    urls = [item[0] for item in fallback_data]
    labels = [item[1] for item in fallback_data]
    
    assert len(urls) > 0
    assert len(set(labels)) == 2  # Binary classification
    
    # 2. Extract features
    X_df, feature_names = extract_all_features(urls)
    
    assert isinstance(X_df, pd.DataFrame)
    assert len(X_df) == len(urls)
    assert len(feature_names) == 16
    assert "url_length" in feature_names
    assert "has_suspicious_warning_words" in feature_names
    
    # 3. Train-Test Split
    y = np.array(labels)
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # 4. Retrieve Models
    models = get_models()
    assert "XGBoost" in models
    assert "Random Forest" in models
    assert "Logistic Regression" in models
    
    # 5. Evaluate Models
    results = evaluate_models(models, X_train, X_test, y_train, y_test)
    
    # 6. Verify Results Structure and validity
    for model_name, model_results in results.items():
        assert "accuracy" in model_results
        assert "auc_roc" in model_results
        assert "f1" in model_results
        assert "model" in model_results
        
        # Verify scores are valid bounded probabilities/metrics
        assert 0.0 <= model_results["accuracy"] <= 1.0
        assert 0.0 <= model_results["auc_roc"] <= 1.0
        assert 0.0 <= model_results["f1"] <= 1.0
        
        # Ensure predictions are generated
        assert len(model_results["y_pred"]) == len(y_test)
        assert len(model_results["y_prob"]) == len(y_test)

@patch('train_model.ARTIFACTS_DIR', new_callable=lambda: tempfile.mkdtemp())
def test_ml_pipeline_report_generation(temp_dir):
    """
    Integration test to verify that the report generation function works
    without throwing errors. We mock ARTIFACTS_DIR to a temp directory
    to avoid overwriting real thesis artifacts.
    """
    urls = [item[0] for item in fallback_data]
    labels = [item[1] for item in fallback_data]
    X_df, feature_names = extract_all_features(urls)
    y = np.array(labels)
    
    # We don't need a split here, just fit on all for testing the report
    models = get_models()
    results = evaluate_models(models, X_df, X_df, y, y)
    
    xgb_model = results["XGBoost"]["model"]
    
    # Generate the report in the temporary directory
    generate_report(results, feature_names, xgb_model, len(urls))
    
    # Verify the report file was created
    report_path = os.path.join(temp_dir, "evaluation_report.md")
    assert os.path.exists(report_path)
    
    # Read the report and verify content
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Model Evaluation Report" in content
        assert "XGBoost" in content
        assert "Random Forest" in content
        assert "Logistic Regression" in content
        assert "URL Length" in content # Checking a feature name
