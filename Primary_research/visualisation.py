"""
VISUALIZATION HELPER
---------------------
This module handles the generation of all academic-grade charts and graphics
for the R&D report, keeping visual rendering libraries (matplotlib, seaborn)
decoupled from the core execution and evaluation pipelines.
"""

import os
import seaborn as sns
import matplotlib.pyplot as plt

def save_confusion_matrix_heatmap(cm, save_directory):
    """
    Generates and saves a high-resolution heatmap for a 2x2 confusion matrix.
    """
    labels = ['Normal Traffic', 'Attack Traffic']

    plt.figure(figsize=(8, 6), dpi=300)
    
    # Generate the heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels,
                annot_kws={"size": 14, "weight": "bold"})

    # Apply academic formatting
    plt.title('Figure 3: Confusion Matrix Heatmap (Version 1.1)', fontsize=14, pad=15, fontweight='bold')
    plt.ylabel('Actual Label', fontsize=12, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')

    plt.tight_layout()

    # Save the file
    save_path = os.path.join(save_directory, 'figure3_confusion_matrix.png')
    plt.savefig(save_path)
    plt.close()
    
    print(f"\n[SUCCESS] Heatmap graphic successfully saved to: {save_path}")