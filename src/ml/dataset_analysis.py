"""
Exploratory Data Analysis for NSL-KDD Dataset
Loads processed data, computes statistics, distributions, and correlations.
Saves plots to eda_plots/ directory.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create plots directory
plots_dir = 'eda_plots'
os.makedirs(plots_dir, exist_ok=True)

# Load processed data
data_dir = '/Users/bpu/Documents/archive'
train_path = os.path.join(data_dir, 'train_processed.csv')
test_path = os.path.join(data_dir, 'test_processed.csv')

print("Loading processed data...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

print(f"Training data shape: {train_df.shape}")
print(f"Testing data shape: {test_df.shape}")

# Basic statistics
print("\n" + "="*50)
print("EXPLORATORY DATA ANALYSIS")
print("="*50)

print("\nTraining Data Statistics:")
print(train_df.describe())

print("\nTesting Data Statistics:")
print(test_df.describe())

# Categorical features analysis
categorical_features = ['protocol_type', 'service', 'flag', 'label']

print("\n" + "="*50)
print("CATEGORICAL FEATURES ANALYSIS")
print("="*50)

for feature in categorical_features:
    print(f"\n{feature.upper()} - Training Data:")
    print(train_df[feature].value_counts())
    print(f"\n{feature.upper()} - Testing Data:")
    print(test_df[feature].value_counts())

# Numerical features analysis
numerical_features = [col for col in train_df.columns if col not in categorical_features]

print("\n" + "="*50)
print("NUMERICAL FEATURES ANALYSIS")
print("="*50)

print(f"\nNumber of numerical features: {len(numerical_features)}")
print("First 10 numerical features:", numerical_features[:10])

# Distribution plots for first 10 numerical features
print("\nGenerating distribution plots...")

for i, feature in enumerate(numerical_features[:10]):
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(train_df[feature], kde=True, bins=50)
    plt.title(f'Training Data: {feature} Distribution')
    plt.xlabel(feature)
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    sns.histplot(test_df[feature], kde=True, bins=50)
    plt.title(f'Testing Data: {feature} Distribution')
    plt.xlabel(feature)
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'{feature}_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()

    if (i+1) % 5 == 0:
        print(f"Generated plots for {i+1} features...")

print(f"Generated distribution plots for first 10 numerical features. Saved in {plots_dir}/")

# Correlation analysis
print("\nGenerating correlation matrix...")

# Sample for correlation to avoid memory issues
sample_size = min(10000, len(train_df))
train_sample = train_df.sample(n=sample_size, random_state=42)

correlation_matrix = train_sample[numerical_features].corr()

plt.figure(figsize=(16, 12))
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', square=True, cbar_kws={'shrink': 0.8})
plt.title(f'Correlation Matrix (Sample of {sample_size} training instances)', fontsize=16)
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'correlation_matrix.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f"Correlation matrix saved as {plots_dir}/correlation_matrix.png")

# Label distribution
print("\nAnalyzing label distribution...")

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
train_df['label'].value_counts().plot(kind='bar')
plt.title('Training Data: Label Distribution')
plt.xlabel('Attack Type')
plt.ylabel('Count')
plt.xticks(rotation=45)

plt.subplot(1, 2, 2)
test_df['label'].value_counts().plot(kind='bar')
plt.title('Testing Data: Label Distribution')
plt.xlabel('Attack Type')
plt.ylabel('Count')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'label_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f"Label distribution plot saved as {plots_dir}/label_distribution.png")

print("\n" + "="*50)
print("EDA COMPLETE")
print("="*50)
print(f"All plots and analysis saved in {plots_dir}/ directory")
print("Key insights:")
print(f"- Training data: {train_df.shape[0]} samples, {len(numerical_features)} numerical features, {len(categorical_features)} categorical features")
print(f"- Testing data: {test_df.shape[0]} samples")
print(f"- Label classes: {train_df['label'].nunique()} unique classes")
print("- Check the plots for distributions and correlations.")
