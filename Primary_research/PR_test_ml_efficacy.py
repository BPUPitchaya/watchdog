import numpy as np
import pandas as pd
import joblib 
import os
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# Must match your training script exactly
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

def run_efficacy_test():
    # 1. Setup paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(os.path.dirname(script_dir), 'models')
    
    print(f"DEBUG: Looking for models in: {model_dir}")
    
    # 2. Load Models
    try:
        rf_model = joblib.load(os.path.join(model_dir, 'random_forest_model.pkl'))
        scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
        encoders = joblib.load(os.path.join(model_dir, 'encoders.pkl'))
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        return
    
    # 3. Load Data
    print("Loading NSL-KDD Test Data...")
    file_path = os.path.join(model_dir, 'KDDTest+.txt')
    df_test = pd.read_csv(file_path, header=None, names=COLUMN_NAMES, sep='\s+', engine='python')
    print(f"DEBUG: Data shape after load: {df_test.shape}")
    print(f"DEBUG: Available columns: {df_test.columns.tolist()}")
    
    # 4. Pre-processing
    print("Pre-processing test data...")
    df_test['label'] = df_test['label'].astype(str).str.replace('.', '', regex=False).str.strip().str.lower()
    
    # Check what the unique labels are before mapping them to 'attack'
    print(f"DEBUG: All unique labels before mapping: {df_test['label'].unique()}")
    
    # Map specifically to 'normal' or 'attack'
    df_test['label'] = df_test['label'].apply(lambda x: 'normal' if x == 'normal' else 'attack')
    y_test = df_test['label']
    
    print(f"DEBUG: Unique labels found: {np.unique(y_test)}")

    categorical_features = ['protocol_type', 'service', 'flag']
    for feature in categorical_features:
        le = encoders[feature]
        df_test[feature] = df_test[feature].astype(str).apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

    X_test = df_test[SELECTED_FEATURES].copy()
    X_test = X_test.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.fillna(0)
    X_test_scaled = scaler.transform(X_test)

    # 5. Execution
    print("Executing predictions...")
    predictions = rf_model.predict(X_test_scaled)

    # 6. Results
    print("\n=== SYSTEM BENCHMARKING RESULTS ===")
    acc = accuracy_score(y_test, predictions)
    print(f"Overall Accuracy: {acc * 100:.2f}%\n")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions, labels=['normal', 'attack']))
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, predictions, labels=['normal', 'attack']))

if __name__ == "__main__":
    run_efficacy_test()