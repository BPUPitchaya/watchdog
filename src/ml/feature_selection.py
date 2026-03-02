"""
Feature Selection for NSL-KDD Dataset
Uses Random Forest to compute feature importances and select top features.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

# Load processed training data
data_dir = '/Users/bpu/Documents/archive'
train_path = os.path.join(data_dir, 'train_processed.csv')

print("Loading processed training data...")
df = pd.read_csv(train_path)

print(f"Data shape: {df.shape}")

# Separate features and target
X = df.drop('label', axis=1)
y = df['label']

print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Use a sample for faster computation
sample_size = min(50000, len(df))  # Sample up to 50k instances
print(f"Using sample of {sample_size} instances for feature selection...")

X_sample, _, y_sample, _ = train_test_split(X, y, train_size=sample_size, random_state=42, stratify=y)

print(f"Sample features shape: {X_sample.shape}")

# Train Random Forest for feature importance
print("Training Random Forest for feature importance...")

rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,  # Limit depth for speed
    random_state=42,
    n_jobs=-1  # Use all available cores
)

rf.fit(X_sample, y_sample)

# Get feature importances
feature_importances = rf.feature_importances_

# Create feature importance DataFrame
feature_names = X.columns
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importances
})

# Sort by importance
importance_df = importance_df.sort_values('importance', ascending=False)

print("\nTop 20 most important features:")
print(importance_df.head(20))

# Select top N features
top_n = 20  # Select top 20 features
selected_features = importance_df['feature'].head(top_n).tolist()

print(f"\nSelected top {top_n} features: {selected_features}")

# Save selected features
selected_features_path = os.path.join(data_dir, 'selected_features.txt')
with open(selected_features_path, 'w') as f:
    f.write('\n'.join(selected_features))

print(f"Selected features saved to {selected_features_path}")

# Save full importance ranking
importance_path = os.path.join(data_dir, 'feature_importances.csv')
importance_df.to_csv(importance_path, index=False)

print(f"Full feature importances saved to {importance_path}")

print("\n" + "="*50)
print("FEATURE SELECTION COMPLETE")
print("="*50)
print(f"Selected {top_n} features based on Random Forest importance")
print("Check selected_features.txt for the list")
print("Check feature_importances.csv for full ranking")
