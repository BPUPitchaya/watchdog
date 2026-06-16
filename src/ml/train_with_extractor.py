"""
Train ML model using the actual feature extractor
This ensures the model learns from the same feature distributions it will see in production
"""

import os
import sys

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.ml.feature_extractor import FeatureExtractor


def generate_training_data(n_samples=10000):
    """Generate training data using the feature extractor."""
    print(f"Generating {n_samples} training samples using feature extractor...")

    extractor = FeatureExtractor()
    data = []
    labels = []

    np.random.seed(42)

    for _i in range(n_samples):
        # Generate packet data
        is_attack = np.random.random() < 0.3  # 30% attacks

        if is_attack:
            # Attack patterns
            packet = {
                "src_ip": f"192.168.1.{np.random.randint(1, 255)}",
                "dst_ip": f"10.0.0.{np.random.randint(1, 255)}",
                "protocol": np.random.choice([6, 17], p=[0.9, 0.1]),
                "length": int(np.random.lognormal(9, 1)),
                "flags": np.random.choice(["S", "R", "SF"], p=[0.5, 0.3, 0.2]),
                "dst_port": np.random.choice(
                    [1234, 4444, 8080, 9999, 21, 23], p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.1]
                ),
                "direction": np.random.choice(["outbound", "inbound"], p=[0.5, 0.5]),
            }
            labels.append(1)  # 1 = attack
        else:
            # Normal patterns
            packet = {
                "src_ip": f"192.168.1.{np.random.randint(1, 255)}",
                "dst_ip": f"10.0.0.{np.random.randint(1, 255)}",
                "protocol": np.random.choice([6, 17, 1], p=[0.8, 0.15, 0.05]),
                "length": int(np.random.lognormal(7, 2)),
                "flags": np.random.choice(["A", "PA", "FA"], p=[0.5, 0.3, 0.2]),
                "dst_port": np.random.choice([80, 443, 22, 53, 21], p=[0.4, 0.3, 0.15, 0.1, 0.05]),
                "direction": np.random.choice(["outbound", "inbound"], p=[0.7, 0.3]),
            }
            labels.append(0)  # 0 = normal

        # Extract features using the actual feature extractor
        features = extractor.extract_packet_features(packet)
        selected_features, _ = extractor.get_selected_features(features)
        data.append(selected_features)

    print(f"Generated {len(data)} samples (Normal: {labels.count(0)}, Attack: {labels.count(1)})")
    return np.array(data), np.array(labels)


def train_model(X_train, y_train):
    """Train Random Forest classifier with parameters optimized for balanced performance."""
    print("Training Random Forest classifier...")

    # Use balanced class weights for better precision/recall balance
    model = RandomForestClassifier(
        n_estimators=200,  # More trees for better performance
        max_depth=20,  # Controlled depth to prevent overfitting
        min_samples_split=10,  # Higher threshold for better generalization
        min_samples_leaf=5,  # Higher threshold for better generalization
        random_state=42,
        n_jobs=1,  # Single-threaded to avoid multiprocessing semaphore leaks
        class_weight="balanced",  # Balanced weights for both classes
    )

    model.fit(X_train, y_train)
    print("Model training completed")

    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    print("\nEvaluating model...")

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="binary")
    recall = recall_score(y_test, y_pred, average="binary")
    f1 = f1_score(y_test, y_pred, average="binary")

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["normal", "attack"]))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("                Predicted")
    print("                Normal  Attack")
    print(f"Actual Normal    {cm[0][0]:4d}   {cm[0][1]:4d}")
    print(f"Actual Attack    {cm[1][0]:4d}   {cm[1][1]:4d}")

    return accuracy, precision, recall, f1


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("ML Model Training with Feature Extractor")
    print("=" * 60)

    # Generate training data
    X, y = generate_training_data(n_samples=15000)

    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")

    # Train model
    model = train_model(X_train, y_train)

    # Evaluate model
    accuracy, precision, recall, f1 = evaluate_model(model, X_test, y_test)

    # Save model
    os.makedirs("models", exist_ok=True)
    model_path = "models/random_forest_model.pkl"
    print(f"\nSaving model to {model_path}...")
    joblib.dump(model, model_path)
    print("Model saved successfully")

    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"Accuracy: {accuracy*100:.2f}%")
    print(f"Precision: {precision*100:.2f}%")
    print(f"Recall: {recall*100:.2f}%")
    print(f"F1 Score: {f1*100:.2f}%")

    if accuracy >= 0.85 and precision >= 0.80 and recall >= 0.75:
        print("\nModel meets accuracy criteria for presentation")
    else:
        print("\nModel does not meet all accuracy criteria")

    print("=" * 60)


if __name__ == "__main__":
    main()
