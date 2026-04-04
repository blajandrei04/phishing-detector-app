import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from app.services.feature_extractor import extract_features

# 1. We will use a small list of known legitimate and phishing URLs 
# to synthesize a dataset since we need raw URLs to extract our specific 13 features.
raw_data = [
    # Legitimate URLs (Label = 0)
    ("https://www.google.com", 0),
    ("https://github.com", 0),
    ("https://en.wikipedia.org/wiki/Main_Page", 0),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0),
    ("https://stackoverflow.com/questions", 0),
    ("https://www.microsoft.com/en-us/", 0),
    ("https://www.apple.com", 0),
    ("https://aws.amazon.com/", 0),
    
    # Phishing / Suspicious URLs (Label = 1)
    ("http://login-update-account-paypal.com", 1),
    ("http://192.168.1.1/login.php", 1),
    ("http://bit.ly/malicious-link", 1),
    ("https://secure-update-apple-id.xyz/login?token=1293812", 1),
    ("http://www.bankofamerica.com.update.security.fraud.com/login", 1),
    ("http://172.16.0.10/admin/index.html", 1),
    ("http://tinyurl.com/free-money", 1),
    ("https://netflix-payment-update-failed.net", 1),
]

def create_model():
    print("1. Extracting features from URLs...")
    features_list = []
    labels = []
    
    for url, label in raw_data:
        feats = extract_features(url)
        features_list.append(feats)
        labels.append(label)
        
    df = pd.DataFrame(features_list)
    df['is_phishing'] = labels
    
    feature_order = [
        "url_length", "hostname_length", "path_length", "query_length",
        "has_https", "has_at_symbol", "has_double_slash_redirect",
        "has_hyphen_in_domain", "subdomain_count", "digit_count",
        "special_char_count", "is_shortener", "uses_ip_as_host"
    ]
    
    X = df[feature_order]
    y = df['is_phishing']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print("2. Training XGBoost Classifier...")
    model = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    os.makedirs("artifacts", exist_ok=True)
    model_path = "artifacts/xgb_opt.pkl"
    joblib.dump(model, model_path)
    print(f"\n3. Model successfully saved to {model_path}!")

if __name__ == "__main__":
    create_model()
