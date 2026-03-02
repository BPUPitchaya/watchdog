"""
Model Training Pipeline for NSL-KDD
Trains Random Forest classifier on selected features and evaluates performance.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os

# Directories
data_dir = '/Users/bpu/Documents/archive'
models_dir = 'models'

# Create models directory
os.makedirs(models_dir, exist_ok=True)

# Load processed data
print("Loading processed data...")
train_df = pd.read_csv(os.path.join(data_dir, 'train_processed.csv'))
test_df = pd.read_csv(os.path.join(data_dir, 'test_processed.csv'))

print(f"Training data shape: {train_df.shape}")
print(f"Testing data shape: {test_df.shape}")

# Load selected features
selected_features_path = os.path.join(data_dir, 'selected_features.txt')
with open(selected_features_path, 'r') as f:
    selected_features = [line.strip() for line in f.readlines()]

print(f"Selected features: {selected_features}")

# Filter data to selected features
X_train = train_df[selected_features]
y_train = train_df['label']

X_test = test_df[selected_features]
y_test = test_df['label']

print(f"Training features shape: {X_train.shape}")
print(f"Testing features shape: {X_test.shape}")

# Train Random Forest
print("Training Random Forest classifier...")

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,  # Allow deeper trees
    random_state=42,
    n_jobs=-1,
    verbose=1
)

rf_model.fit(X_train, y_train)

print("Training complete.")

# Save the model
model_path = os.path.join(models_dir, 'random_forest_model.pkl')
joblib.dump(rf_model, model_path)
print(f"Model saved to {model_path}")

# Evaluate on test data
print("Evaluating on test data...")

y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print("\n" + "="*50)
print("MODEL EVALUATION RESULTS")
print("="*50)
print(".4f")
print(".4f")
print(".4f")
print(".4f")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\n" + "="*50)
print("MODEL TRAINING COMPLETE")
print("="*50)
print(f"Model saved as {model_path}")
print("Evaluation metrics computed on test data")
