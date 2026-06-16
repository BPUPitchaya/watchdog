"""
Accuracy testing script for WATCHDOG ML model
Tests the trained model's detection accuracy on synthetic data
"""

import os
import sys

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ml.feature_extractor import FeatureExtractor


def generate_test_data(n_samples=1000):
    """Generate synthetic test data that matches training distribution."""
    print(f"Generating {n_samples} synthetic test samples...")

    np.random.seed(42)

    data = []
    labels = []

    for _i in range(n_samples):
        # Generate packet data with distributions matching training data
        is_attack = np.random.random() < 0.3  # 30% attacks (matches training)

        if is_attack:
            # Attack patterns: higher error rates, unusual ports, larger packets
            packet = {
                "src_ip": f"192.168.1.{np.random.randint(1, 255)}",
                "dst_ip": f"10.0.0.{np.random.randint(1, 255)}",
                "protocol": np.random.choice([6, 17], p=[0.9, 0.1]),  # Mostly TCP
                "length": int(np.random.lognormal(9, 1)),  # Larger packets
                "flags": np.random.choice(["S", "R", "SF"], p=[0.5, 0.3, 0.2]),  # SYN, RST, SYN+FIN
                "dst_port": np.random.choice(
                    [1234, 4444, 8080, 9999, 21, 23], p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.1]
                ),
                "direction": np.random.choice(["outbound", "inbound"], p=[0.5, 0.5]),
            }
            labels.append(1)  # 1 = attack
        else:
            # Normal patterns: standard ports, normal packet sizes
            packet = {
                "src_ip": f"192.168.1.{np.random.randint(1, 255)}",
                "dst_ip": f"10.0.0.{np.random.randint(1, 255)}",
                "protocol": np.random.choice([6, 17, 1], p=[0.8, 0.15, 0.05]),
                "length": int(np.random.lognormal(7, 2)),  # Normal packet sizes
                "flags": np.random.choice(
                    ["A", "PA", "FA"], p=[0.5, 0.3, 0.2]
                ),  # ACK, PUSH+ACK, FIN+ACK
                "dst_port": np.random.choice([80, 443, 22, 53, 21], p=[0.4, 0.3, 0.15, 0.1, 0.05]),
                "direction": np.random.choice(["outbound", "inbound"], p=[0.7, 0.3]),
            }
            labels.append(0)  # 0 = normal

        data.append(packet)

    print(f"Generated {len(data)} samples (Normal: {labels.count(0)}, Attack: {labels.count(1)})")
    return data, labels


def test_model_accuracy():
    """Test the trained model's accuracy."""
    print("=" * 60)
    print("WATCHDOG ML Model Accuracy Test")
    print("=" * 60)

    # Load model
    model_path = "models/random_forest_model.pkl"
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return False

    print(f"Loading model from {model_path}...")
    try:
        model = joblib.load(model_path)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

    # Initialize feature extractor
    extractor = FeatureExtractor()

    # Generate test data
    test_packets, true_labels = generate_test_data(n_samples=1000)

    # Extract features and make predictions
    print("\nExtracting features and making predictions...")
    predicted_labels = []

    for packet in test_packets:
        try:
            features = extractor.extract_packet_features(packet)
            selected_features, _ = extractor.get_selected_features(features)

            # Reshape for prediction
            features_array = np.array(selected_features).reshape(1, -1)
            prediction = model.predict(features_array)[0]
            predicted_labels.append(prediction)
        except Exception as e:
            print(f"Error processing packet: {e}")
            predicted_labels.append(0)  # Default to normal (0) on error

    # Calculate metrics
    print("\nCalculating accuracy metrics...")

    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, pos_label=1, average="binary")
    recall = recall_score(true_labels, predicted_labels, pos_label=1, average="binary")
    f1 = f1_score(true_labels, predicted_labels, pos_label=1, average="binary")

    print("\n" + "=" * 60)
    print("ACCURACY RESULTS")
    print("=" * 60)
    print(f"Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision (Attack): {precision:.4f} ({precision*100:.2f}%)")
    print(f"Recall (Attack): {recall:.4f} ({recall*100:.2f}%)")
    print(f"F1 Score (Attack): {f1:.4f} ({f1*100:.2f}%)")

    print("\nClassification Report:")
    print(classification_report(true_labels, predicted_labels, target_names=["normal", "attack"]))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(true_labels, predicted_labels, labels=[0, 1])
    print("                Predicted")
    print("                Normal  Attack")
    print(f"Actual Normal    {cm[0][0]:4d}   {cm[0][1]:4d}")
    print(f"Actual Attack    {cm[1][0]:4d}   {cm[1][1]:4d}")

    # Calculate true positive rate, false positive rate
    tn, fp, fn, tp = cm.ravel()
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

    print(f"\nTrue Positive Rate (TPR): {tpr:.4f} ({tpr*100:.2f}%)")
    print(f"False Positive Rate (FPR): {fpr:.4f} ({fpr*100:.2f}%)")

    # Performance criteria
    print("\n" + "=" * 60)
    print("PERFORMANCE CRITERIA")
    print("=" * 60)

    criteria_passed = True

    if accuracy >= 0.85:
        print(f"PASS: Accuracy >= 85% (actual: {accuracy*100:.2f}%)")
    else:
        print(f"WARNING: Accuracy < 85% (actual: {accuracy*100:.2f}%)")
        criteria_passed = False

    if precision >= 0.80:
        print(f"PASS: Precision >= 80% (actual: {precision*100:.2f}%)")
    else:
        print(f"WARNING: Precision < 80% (actual: {precision*100:.2f}%)")
        criteria_passed = False

    if recall >= 0.75:
        print(f"PASS: Recall >= 75% (actual: {recall*100:.2f}%)")
    else:
        print(f"WARNING: Recall < 75% (actual: {recall*100:.2f}%)")
        criteria_passed = False

    if fpr <= 0.10:
        print(f"PASS: False Positive Rate <= 10% (actual: {fpr*100:.2f}%)")
    else:
        print(f"WARNING: False Positive Rate > 10% (actual: {fpr*100:.2f}%)")
        criteria_passed = False

    print("\n" + "=" * 60)
    if criteria_passed:
        print("All accuracy criteria passed!")
        return True
    else:
        print("Some accuracy criteria not met")
        return False


if __name__ == "__main__":
    success = test_model_accuracy()
    sys.exit(0 if success else 1)
