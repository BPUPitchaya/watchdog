"""
Dataset Preparation for NSL-KDD
Extracts the ZIP file, loads the data, assigns column names, encodes categorical features, and saves processed CSVs.
"""

import zipfile
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Define paths
archive_dir = '/Users/bpu/Documents/archive/'
data_dir = 'data/'

# Create data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Check for extracted files directly
train_file_check = os.path.join(archive_dir, 'KDDTrain+.txt')
test_file_check = os.path.join(archive_dir, 'KDDTest+.txt')
if os.path.exists(train_file_check) and os.path.exists(test_file_check):
    print("Extracted files found. Using them directly.")
    data_dir = archive_dir  # Use the archive_dir as data_dir
else:
    # Find the ZIP file in archive_dir
    zip_files = [f for f in os.listdir(archive_dir) if f.endswith('.zip')]
    if not zip_files:
        raise FileNotFoundError(f"No ZIP file or extracted KDDTrain+.csv/KDDTest+.csv found in {archive_dir}")

    zip_filename = zip_files[0]  # Assume the first ZIP file
    zip_path = os.path.join(archive_dir, zip_filename)

    print(f"Extracting {zip_path} to {data_dir}...")

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)

    print("Extraction complete.")

# Define column names for NSL-KDD (41 features + label)
columns = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
    'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
    'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count',
    'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
    'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label'
]

# Load training data
train_file = os.path.join(data_dir, 'KDDTrain+.txt')
if os.path.exists(train_file):
    print("Loading training data...")
    train_df = pd.read_csv(train_file, header=None, names=columns + ['extra'])
    train_df = train_df.drop('extra', axis=1)
    print(f"Training data shape: {train_df.shape}")
else:
    raise FileNotFoundError(f"Training file not found: {train_file}")

# Load testing data
test_file = os.path.join(data_dir, 'KDDTest+.txt')
if os.path.exists(test_file):
    print("Loading testing data...")
    test_df = pd.read_csv(test_file, header=None, names=columns + ['extra'])
    test_df = test_df.drop('extra', axis=1)
    print(f"Testing data shape: {test_df.shape}")
else:
    raise FileNotFoundError(f"Testing file not found: {test_file}")

# Encode categorical features
categorical_features = ['protocol_type', 'service', 'flag']
label_encoders = {}

print("Encoding categorical features...")
for feature in categorical_features:
    # Combine unique values from train and test to handle unknown categories
    all_values = set(train_df[feature]).union(set(test_df[feature]))
    le = LabelEncoder()
    le.fit(list(all_values))
    train_df[feature] = le.transform(train_df[feature])
    test_df[feature] = le.transform(test_df[feature])
    label_encoders[feature] = le

# Encode labels (attack types)
all_labels = set(train_df['label']).union(set(test_df['label']))
le_label = LabelEncoder()
le_label.fit(list(all_labels))
train_df['label'] = le_label.transform(train_df['label'])
test_df['label'] = le_label.transform(test_df['label'])
label_encoders['label'] = le_label

print("Encoding complete.")

# Save processed data
train_processed_path = os.path.join(data_dir, 'train_processed.csv')
test_processed_path = os.path.join(data_dir, 'test_processed.csv')

print(f"Saving processed training data to {train_processed_path}...")
train_df.to_csv(train_processed_path, index=False)

print(f"Saving processed testing data to {test_processed_path}...")
test_df.to_csv(test_processed_path, index=False)

print("Dataset preparation complete!")
print(f"Training data: {train_df.shape}")
print(f"Testing data: {test_df.shape}")
print("Processed files saved in data/ directory.")
