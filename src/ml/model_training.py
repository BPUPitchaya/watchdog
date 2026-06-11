"""
NSL-KDD Model Training Script - FIXED WITH CROSS-VALIDATION
Trains a Random Forest classifier on the actual NSL-KDD text dataset.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score 
import joblib

# Selected features (must match feature_extractor.py and test script)
SELECTED_FEATURES = [
    'src_bytes', 'same_srv_rate', 'flag', 'dst_host_serror_rate', 
    'serror_rate', 'diff_srv_rate', 'dst_host_same_srv_rate', 
    'srv_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_same_src_port_rate',
    'dst_host_diff_srv_rate', 'count', 'dst_bytes', 'dst_host_srv_diff_host_rate',
    'protocol_type', 'srv_count', 'dst_host_srv_count', 'service', 
    'dst_host_rerror_rate', 'dst_host_count'
]

COLUMN_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty_level'
]

def load_real_dataset(filepath):
    """Load actual NSL-KDD dataset using tab separation."""
    print(f"Loading dataset from {filepath}...")
    try:
        df = pd.read_csv(filepath, header=None, names=COLUMN_NAMES, sep='\t', engine='python')
        print(f"Dataset successfully loaded: {df.shape[0]} samples, {df.shape[1]} features")
        return df
    except Exception as e:
        print(f"Critical Error loading dataset at {filepath}: {e}")
        return None

def preprocess_data(df, encoders=None, scaler=None, fit=True):
    print("Preprocessing data...")
    df = df.copy()
    
    # Clean and binary-map the labels
    df['label'] = df['label'].astype(str).str.replace('.', '', regex=False).str.strip().str.lower()
    df['label'] = df['label'].apply(lambda x: 'normal' if x == 'normal' else 'attack')
    
    categorical_features = ['protocol_type', 'service', 'flag']
    if encoders is None:
        encoders = {}
    
    for feature in categorical_features:
        if fit:
            le = LabelEncoder()
            df[feature] = le.fit_transform(df[feature].astype(str))
            encoders[feature] = le
        else:
            if feature in encoders:
                le = encoders[feature]
                df[feature] = df[feature].astype(str).apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )
    
    X = df[SELECTED_FEATURES].copy()
    y = df['label']
    
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    if fit:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)
        
    return X_scaled, y, encoders, scaler

def main():
    data_dir = 'models'
    train_file = os.path.join(data_dir, 'KDDTrain+.txt')
    test_file = os.path.join(data_dir, 'KDDTest+.txt')
    
    # Force check for real files to avoid synthetic fallback loop
    if not os.path.exists(train_file) or not os.path.exists(test_file):
        print(f"CRITICAL: Ensure your real data text files are saved inside the '{data_dir}/' directory!")
        return

    # Load real data arrays
    train_df = load_real_dataset(train_file)
    test_df = load_real_dataset(test_file)
    
    if train_df is None or test_df is None:
        return

    # Process and align structures
    X_train, y_train, encoders, scaler = preprocess_data(train_df, fit=True)
    X_test, y_test, _, _ = preprocess_data(test_df, encoders=encoders, scaler=scaler, fit=False)
    
    # Define the model template
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    # Calculate 5-Fold Cross-Validation Accuracy using the training data split
    print("\n[INFO] Calculating 5-Fold Cross-Validation Accuracy...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
    print(f"-> All Fold Scores: {cv_scores}")
    print(f"-> Mean Cross-Validation Accuracy: {cv_scores.mean() * 100:.2f}%\n")
    
    print("Training Random Forest classifier on real data...")
    model.fit(X_train, y_train)
    
    # Verify performance immediately before saving
    y_pred = model.predict(X_test)
    print(f"\nImmediate Validation Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    # Save optimized production objects
    os.makedirs(data_dir, exist_ok=True)
    joblib.dump(model, os.path.join(data_dir, 'random_forest_model.pkl'))
    joblib.dump(scaler, os.path.join(data_dir, 'scaler.pkl'))
    joblib.dump(encoders, os.path.join(data_dir, 'encoders.pkl'))
    print("All synchronized models saved successfully.")

if __name__ == "__main__":
    main()