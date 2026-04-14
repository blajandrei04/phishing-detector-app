import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from app.services.feature_extractor import extract_features

fallback_data = [
    ("https://www.google.com", 0), ("https://github.com", 0), ("https://en.wikipedia.org/wiki/Main_Page", 0),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0), ("https://stackoverflow.com/questions", 0),
    ("https://www.microsoft.com/en-us/", 0), ("https://www.apple.com", 0), ("https://aws.amazon.com/", 0),
    
    ("http://login-update-account-paypal.com", 1), ("http://192.168.1.1/login.php", 1),
    ("http://bit.ly/malicious-link", 1), ("https://secure-update-apple-id.xyz/login?token=1293812", 1),
    ("http://www.bankofamerica.com.update.security.fraud.com/login", 1), ("http://172.16.0.10/admin/index.html", 1),
    ("http://tinyurl.com/free-money", 1), ("https://netflix-payment-update-failed.net", 1),
]

def load_data():
    dataset_path = "datasets/phishing_site_urls.csv"
    
    if os.path.exists(dataset_path):
        print(f"Loading large dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        url_col = "URL" if "URL" in df.columns else df.columns[0]
        label_col = "Label" if "Label" in df.columns else df.columns[1]
        
        # Convert "bad"/"good" to 1/0 so the API works perfectly
        df[label_col] = df[label_col].apply(lambda x: 1 if str(x).strip().lower() == 'bad' else 0)
        
        print(f"Loading ALL {len(df):,} URLs for maximum accuracy training!")
        
        urls = df[url_col].tolist()
        labels = df[label_col].tolist()
    else:
        print("No raw URLs CSV found. Falling back to the 16-URL synthetic dataset.")
        print("💡 TIP: Download the Kaggle 'Phishing Site URLs' dataset to 'datasets/phishing_urls_raw.csv' for the real deal!")
        urls = [item[0] for item in fallback_data]
        labels = [item[1] for item in fallback_data]
        
    return urls, labels

def create_model():
    print("1. Loading Data...")
    urls, labels = load_data()
    
    print(f"2. Extracting features for {len(urls)} URLs... (This might take a minute)")
    features_list = []
    
    for url in urls:
        feats = extract_features(str(url))
        features_list.append(feats)
        
    df = pd.DataFrame(features_list)
    df['is_phishing'] = labels
    
    feature_order = [
        "url_length", "hostname_length", "path_length", "query_length",
        "has_at_symbol", "has_double_slash_redirect",
        "has_hyphen_in_domain", "subdomain_count", "digit_count",
        "special_char_count", "is_shortener", "uses_ip_as_host",
        "num_directories", "num_parameters", "url_entropy", 
        "has_suspicious_warning_words"
    ]
    
    X = df[feature_order]
    y = df['is_phishing']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print("3. Training XGBoost Classifier...")
    # XGBoost configuration for high confidence output
    model = XGBClassifier(
        n_estimators=300, 
        max_depth=7, 
        learning_rate=0.1, 
        random_state=42, 
        n_jobs=-1,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    
    print("4. Evaluating Model...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    print(f"\nModel Accuracy: {acc * 100:.2f}%")
    print(f"Model AUC-ROC:  {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    os.makedirs("artifacts", exist_ok=True)
    model_path = "artifacts/xgb_opt.pkl" 
    joblib.dump(model, model_path)
    print(f"\n5. Highly confident XGBoost model successfully saved to {model_path}!")

if __name__ == "__main__":
    create_model()
