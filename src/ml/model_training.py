"""
NSL-KDD Model Training Script
Trains a Random Forest classifier on the NSL-KDD dataset for network intrusion detection.
"""

import os
import urllib.request

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Selected features (must match feature_extractor.py)
SELECTED_FEATURES = [
    "src_bytes",
    "same_srv_rate",
    "flag",
    "dst_host_serror_rate",
    "serror_rate",
    "diff_srv_rate",
    "dst_host_same_srv_rate",
    "srv_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_same_src_port_rate",
    "dst_host_diff_srv_rate",
    "count",
    "dst_bytes",
    "dst_host_srv_diff_host_rate",
    "protocol_type",
    "srv_count",
    "dst_host_srv_count",
    "service",
    "dst_host_rerror_rate",
    "dst_host_count",
]

# NSL-KDD dataset URLs (from UNB repository)
KDD_TRAIN_URL = "https://unb.ca/cic/datasets/nsl-kdd.zip"
KDD_TEST_URL = "https://unb.ca/cic/datasets/nsl-kdd.zip"

# Column names for NSL-KDD dataset
COLUMN_NAMES = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
]


def download_dataset(url, filename):
    """Download NSL-KDD dataset from URL."""
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False


def generate_synthetic_data(n_samples=10000):
    """Generate synthetic network traffic data for demonstration.

    This creates data that mimics NSL-KDD structure when the real dataset
    is unavailable. For production use, download the actual NSL-KDD dataset.
    """
    print(f"Generating {n_samples} synthetic samples...")

    np.random.seed(42)

    data = {}

    # Generate features similar to NSL-KDD
    data["duration"] = np.random.exponential(1, n_samples)
    data["protocol_type"] = np.random.choice(
        [0, 1, 2], n_samples, p=[0.8, 0.15, 0.05]
    )  # tcp, udp, icmp
    data["service"] = np.random.randint(0, 70, n_samples)
    data["flag"] = np.random.randint(0, 11, n_samples)
    data["src_bytes"] = np.random.lognormal(7, 2, n_samples).astype(int)
    data["dst_bytes"] = np.random.lognormal(6, 2, n_samples).astype(int)
    data["land"] = np.random.choice([0, 1], n_samples, p=[0.99, 0.01])
    data["wrong_fragment"] = np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
    data["urgent"] = np.random.choice([0, 1], n_samples, p=[0.98, 0.02])
    data["hot"] = np.random.poisson(0.5, n_samples)
    data["num_failed_logins"] = np.random.poisson(0.1, n_samples)
    data["logged_in"] = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    data["num_compromised"] = np.random.poisson(0.2, n_samples)
    data["root_shell"] = np.random.choice([0, 1], n_samples, p=[0.99, 0.01])
    data["su_attempted"] = np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
    data["num_root"] = np.random.poisson(0.1, n_samples)
    data["num_file_creations"] = np.random.poisson(0.3, n_samples)
    data["num_shells"] = np.random.poisson(0.2, n_samples)
    data["num_access_files"] = np.random.poisson(0.5, n_samples)
    data["num_outbound_cmds"] = np.zeros(n_samples)
    data["is_host_login"] = np.random.choice([0, 1], n_samples, p=[0.999, 0.001])
    data["is_guest_login"] = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    data["count"] = np.random.poisson(5, n_samples)
    data["srv_count"] = np.random.poisson(3, n_samples)
    data["serror_rate"] = np.random.beta(0.5, 5, n_samples)
    data["srv_serror_rate"] = np.random.beta(0.5, 5, n_samples)
    data["rerror_rate"] = np.random.beta(0.3, 5, n_samples)
    data["srv_rerror_rate"] = np.random.beta(0.3, 5, n_samples)
    data["same_srv_rate"] = np.random.beta(5, 2, n_samples)
    data["diff_srv_rate"] = np.random.beta(2, 5, n_samples)
    data["srv_diff_host_rate"] = np.random.beta(1, 10, n_samples)
    data["dst_host_count"] = np.random.poisson(10, n_samples)
    data["dst_host_srv_count"] = np.random.poisson(5, n_samples)
    data["dst_host_same_srv_rate"] = np.random.beta(5, 2, n_samples)
    data["dst_host_diff_srv_rate"] = np.random.beta(2, 5, n_samples)
    data["dst_host_same_src_port_rate"] = np.random.beta(3, 3, n_samples)
    data["dst_host_srv_diff_host_rate"] = np.random.beta(1, 10, n_samples)
    data["dst_host_serror_rate"] = np.random.beta(0.5, 5, n_samples)
    data["dst_host_srv_serror_rate"] = np.random.beta(0.5, 5, n_samples)
    data["dst_host_rerror_rate"] = np.random.beta(0.3, 5, n_samples)
    data["dst_host_srv_rerror_rate"] = np.random.beta(0.3, 5, n_samples)

    # Generate labels (normal vs attack)
    # Create patterns: attacks have different feature distributions
    is_attack = np.random.random(n_samples) < 0.3  # 30% attacks

    # Modify attack samples to have different patterns
    data["serror_rate"][is_attack] = np.random.beta(2, 1, np.sum(is_attack))
    data["dst_host_serror_rate"][is_attack] = np.random.beta(2, 1, np.sum(is_attack))
    data["src_bytes"][is_attack] = np.random.lognormal(9, 1, np.sum(is_attack)).astype(int)
    data["count"][is_attack] = np.random.poisson(20, np.sum(is_attack))

    labels = np.where(is_attack, "attack", "normal")
    data["label"] = labels

    df = pd.DataFrame(data)
    print(f"Generated synthetic dataset: {df.shape[0]} samples, {df.shape[1]} features")
    print(
        f"Class distribution: Normal={np.sum(labels=='normal')}, Attack={np.sum(labels=='attack')}"
    )

    return df


def load_dataset(filepath):
    """Load NSL-KDD dataset from file."""
    print(f"Loading dataset from {filepath}...")
    try:
        df = pd.read_csv(filepath, names=COLUMN_NAMES)
        print(f"Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


def preprocess_data(df, encoders=None, scaler=None, fit=True):
    """
    Preprocess NSL-KDD dataset.

    Args:
        df: DataFrame with raw data
        encoders: Dictionary of fitted LabelEncoders (for test data)
        scaler: Fitted StandardScaler (for test data)
        fit: Whether to fit encoders and scaler (True for train, False for test)

    Returns:
        Preprocessed DataFrame, encoders, scaler
    """
    print("Preprocessing data...")

    # Create copies to avoid modifying original
    df = df.copy()

    # Binary classification: normal vs attack
    df["label"] = df["label"].apply(lambda x: "normal" if x == "normal" else "attack")

    # Encode categorical features
    categorical_features = ["protocol_type", "service", "flag"]

    if encoders is None:
        encoders = {}

    for feature in categorical_features:
        if fit:
            # Fit and transform for training data
            le = LabelEncoder()
            df[feature] = le.fit_transform(df[feature].astype(str))
            encoders[feature] = le
        else:
            # Transform only for test data
            if feature in encoders:
                # Handle unseen labels by mapping to a default value
                le = encoders[feature]
                df[feature] = (
                    df[feature]
                    .astype(str)
                    .apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
                )

    # Select only the features we need
    available_features = [f for f in SELECTED_FEATURES if f in df.columns]

    if len(available_features) != len(SELECTED_FEATURES):
        missing = set(SELECTED_FEATURES) - set(available_features)
        print(f"Warning: Missing features: {missing}")

    X = df[available_features].copy()
    y = df["label"]

    # Handle missing values and infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)

    # Scale numerical features
    if fit:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        if scaler is not None:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X.values

    return X_scaled, y, encoders, scaler


def train_model(X_train, y_train):
    """Train Random Forest classifier."""
    print("Training Random Forest classifier...")

    # Use parameters optimized for NSL-KDD
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)
    print("Model training completed")

    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    print("\nEvaluating model...")

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    return accuracy


def save_model(model, scaler, encoders, output_dir="models"):
    """Save trained model and preprocessing objects."""
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, "random_forest_model.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    encoders_path = os.path.join(output_dir, "encoders.pkl")

    print(f"\nSaving model to {model_path}...")
    joblib.dump(model, model_path)

    print(f"Saving scaler to {scaler_path}...")
    joblib.dump(scaler, scaler_path)

    print(f"Saving encoders to {encoders_path}...")
    joblib.dump(encoders, encoders_path)

    print("Model and preprocessing objects saved successfully")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("NSL-KDD Model Training Pipeline")
    print("=" * 60)

    # Create data directory
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # Try to download datasets
    train_file = os.path.join(data_dir, "KDDTrain+_20Percent.txt")
    test_file = os.path.join(data_dir, "KDDTest+.txt")

    use_synthetic = False

    if not os.path.exists(train_file):
        print("Training dataset not found locally.")
        print("Attempting to download from:", KDD_TRAIN_URL)
        if not download_dataset(KDD_TRAIN_URL, train_file):
            print("Failed to download training dataset.")
            print("Using synthetic data for demonstration...")
            use_synthetic = True

    if not use_synthetic and not os.path.exists(test_file):
        print("Test dataset not found locally.")
        print("Attempting to download from:", KDD_TEST_URL)
        if not download_dataset(KDD_TEST_URL, test_file):
            print("Failed to download test dataset.")
            print("Using synthetic data for demonstration...")
            use_synthetic = True

    if use_synthetic:
        # Generate synthetic data
        print("\nGenerating synthetic training data...")
        train_df = generate_synthetic_data(n_samples=15000)
        print("Generating synthetic test data...")
        test_df = generate_synthetic_data(n_samples=5000)
    else:
        # Load datasets
        train_df = load_dataset(train_file)
        test_df = load_dataset(test_file)

        if train_df is None or test_df is None:
            print("Failed to load datasets. Falling back to synthetic data...")
            print("\nGenerating synthetic training data...")
            train_df = generate_synthetic_data(n_samples=15000)
            print("Generating synthetic test data...")
            test_df = generate_synthetic_data(n_samples=5000)

    # Preprocess training data
    X_train, y_train, encoders, scaler = preprocess_data(train_df, fit=True)

    # Preprocess test data using fitted encoders and scaler
    X_test, y_test, _, _ = preprocess_data(test_df, encoders=encoders, scaler=scaler, fit=False)

    # Train model
    model = train_model(X_train, y_train)

    # Evaluate model
    evaluate_model(model, X_test, y_test)

    # Save model
    save_model(model, scaler, encoders)

    print("\n" + "=" * 60)
    print("Training pipeline completed successfully!")
    if use_synthetic:
        print("NOTE: Model trained on synthetic data.")
        print("For production use, download the actual NSL-KDD dataset.")
    print("=" * 60)


if __name__ == "__main__":
    main()
