"""
ctPred-V2 Training and Evaluation Script

This script implements the complete workflow for training and evaluating ctPred-V2
with fused Enformer + HyenaDNA features, and comparing it against the baseline ctPred model.
"""

import torch
from torch.utils import data
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from ctPred_utils import *
import os
import argparse
import json
import numpy as np
from scipy.stats import pearsonr
import pickle
from typing import Dict, Tuple
mpl.rcParams['pdf.fonttype'] = 42

# specify the device that you'll use cpu or gpu
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


def prepare_mock_expression_data(n_genes: int = 100, output_path: str = "mock_expression_data.csv"):
    """
    Create mock expression data for testing ctPred-V2.
    
    Args:
        n_genes: Number of genes to create
        output_path: Output CSV file path
    """
    # Create mock expression data matching fused features
    mock_data = {
        'gene_name': [f'GENE_{i:05d}' for i in range(n_genes)],
        'chromo': [f'chr{(i % 22) + 1}' for i in range(n_genes)],
        'mean_expression': np.random.beta(2, 5, n_genes)  # Realistic expression distribution
    }
    
    df = pd.DataFrame(mock_data)
    # Add index column to match the expected format
    df.index.name = 'index'
    df.to_csv(output_path)
    print(f"Created mock expression data: {output_path}")
    return output_path


def ctPred_V2_comparative_training(fused_features_path: str, exp_matrix_path: str, params: dict):
    """
    Train both ctPred (baseline) and ctPred-V2 (fused features) for comparison.
    
    Args:
        fused_features_path: Path to fused features pickle file
        exp_matrix_path: Path to expression matrix CSV
        params: Training parameters
    """
    
    print("=== ctPred-V2 Comparative Training ===")
    
    # Extract parameters
    Model_path = params.get("Model_path", "./models/")
    fig_path = params.get("fig_path", "./figures/")
    train_set = params.get("training_set")
    val_set = params.get("valid_set") 
    test_set = params.get("test_set")
    
    # Ensure output directories exist
    os.makedirs(Model_path, exist_ok=True)
    os.makedirs(fig_path, exist_ok=True)
    
    cell_type = os.path.basename(exp_matrix_path).split('.csv')[0]
    
    # === Prepare data for ctPred-V2 ===
    print("\n1. Preparing data for ctPred-V2 (fused features)...")
    data_v2 = input_prep_fused(fused_features_path, exp_matrix_path)
    print(f"Data loaded: {data_v2.shape[0]} genes, {data_v2.shape[1]-3} features")
    
    # Get feature dimension for ctPred-V2
    feature_cols = [col for col in data_v2.columns if col not in ['gene_name', 'chromo', 'mean_expression']]
    fused_feature_dim = len(feature_cols)
    print(f"Fused feature dimension: {fused_feature_dim}")
    
    train_epi_v2, train_exp_v2, val_epi_v2, _, val_exp_v2, test_epi_v2, test_exp_v2 = data_prepare_v2(
        data_v2, train_set, val_set, test_set
    )
    train_data_iter_v2 = dataloader(train_epi_v2, train_exp_v2, batch_size=1000)
    
    # === Train ctPred-V2 ===
    print("\n2. Training ctPred-V2...")
    ctPred_V2_model = ctPred_V2(input_dim=fused_feature_dim).to(device)
    
    saved_path_v2 = os.path.join(Model_path, f'{cell_type}_ctPred_V2.pt')
    ctPred_training(ctPred_V2_model, train_data_iter_v2, train_epi_v2, train_exp_v2, 
                   val_epi_v2, val_exp_v2, f"{cell_type}_V2", fig_path, 
                   epochs=100, model_path=saved_path_v2)
    
    # === Evaluate ctPred-V2 ===
    print("\n3. Evaluating ctPred-V2...")
    correlation_v2, predictions_v2 = evaluate_model(ctPred_V2_model, test_epi_v2, test_exp_v2)
    print(f"ctPred-V2 Test Correlation: {correlation_v2:.4f}")
    
    # === Create and evaluate baseline ctPred with Enformer-only features ===
    print("\n4. Creating baseline comparison with Enformer-only features...")
    
    # Load original Enformer features for comparison
    enformer_features_path = "enformer_features.pkl"
    if not os.path.exists(enformer_features_path):
        print("Enformer features not found, creating them...")
        from enformer_features import EnformerFeatureExtractor
        extractor = EnformerFeatureExtractor()
        extractor.extract_and_save("mock_annotations.gtf", enformer_features_path)
    
    # Create baseline data with Enformer-only features
    baseline_data = create_enformer_only_data(enformer_features_path, exp_matrix_path)
    train_epi_baseline, train_exp_baseline, val_epi_baseline, _, val_exp_baseline, test_epi_baseline, test_exp_baseline = data_prepare_v2(
        baseline_data, train_set, val_set, test_set
    )
    train_data_iter_baseline = dataloader(train_epi_baseline, train_exp_baseline, batch_size=1000)
    
    # Get actual baseline feature dimension
    baseline_feature_cols = [col for col in baseline_data.columns if col not in ['gene_name', 'chromo', 'mean_expression']]
    baseline_feature_dim = len(baseline_feature_cols)
    print(f"Baseline feature dimension: {baseline_feature_dim}")
    
    # Train baseline ctPred
    print("Training baseline ctPred...")
    ctPred_baseline = ctPred(input_dim=baseline_feature_dim).to(device)
    
    saved_path_baseline = os.path.join(Model_path, f'{cell_type}_ctPred_baseline.pt')
    ctPred_training(ctPred_baseline, train_data_iter_baseline, train_epi_baseline, train_exp_baseline,
                   val_epi_baseline, val_exp_baseline, f"{cell_type}_baseline", fig_path,
                   epochs=100, model_path=saved_path_baseline)
    
    # Evaluate baseline
    print("Evaluating baseline ctPred...")
    correlation_baseline, predictions_baseline = evaluate_model(ctPred_baseline, test_epi_baseline, test_exp_baseline)
    print(f"Baseline ctPred Test Correlation: {correlation_baseline:.4f}")
    
    # === Comparison and Results ===
    print("\n=== COMPARATIVE RESULTS ===")
    print(f"Baseline ctPred (Enformer-only):  {correlation_baseline:.4f}")
    print(f"ctPred-V2 (Enformer + HyenaDNA):  {correlation_v2:.4f}")
    
    improvement = correlation_v2 - correlation_baseline
    print(f"Improvement: {improvement:.4f} ({improvement/correlation_baseline*100:.1f}%)")
    
    if improvement > 0:
        print("✓ HYPOTHESIS SUPPORTED: ctPred-V2 outperforms baseline!")
    else:
        print("✗ Hypothesis not supported: ctPred-V2 did not improve over baseline.")
    
    # Generate comparison visualization
    create_comparison_plot(test_exp_v2.cpu().numpy(), 
                         predictions_v2, 
                         predictions_baseline, 
                         correlation_v2, 
                         correlation_baseline, 
                         cell_type, 
                         fig_path)
    
    # Save results
    results = {
        'cell_type': cell_type,
        'baseline_correlation': float(correlation_baseline),
        'ctPred_V2_correlation': float(correlation_v2),
        'improvement': float(improvement),
        'feature_dimensions': {
            'baseline': 5313,
            'ctPred_V2': fused_feature_dim,
            'enformer_contribution': 5313,
            'hyenadna_contribution': fused_feature_dim - 5313
        }
    }
    
    results_path = os.path.join(Model_path, f'{cell_type}_comparison_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")
    
    return results


def create_enformer_only_data(enformer_features_path: str, exp_matrix_path: str) -> pd.DataFrame:
    """
    Create dataset with Enformer-only features for baseline comparison.
    
    Args:
        enformer_features_path: Path to Enformer features
        exp_matrix_path: Path to expression data
        
    Returns:
        DataFrame with Enformer features and expression data
    """
    # Load expression data
    exp_data = pd.read_csv(exp_matrix_path, index_col=0)
    
    # Load Enformer features
    with open(enformer_features_path, 'rb') as f:
        enformer_features = pickle.load(f)
    
    # Convert to DataFrame format
    feature_data = []
    for gene_name, features in enformer_features.items():
        row = {'gene_name': gene_name}
        for i, feature_val in enumerate(features):
            row[f'enformer_{i}'] = feature_val
        feature_data.append(row)
    
    enformer_df = pd.DataFrame(feature_data)
    
    # Merge with expression data
    merged_data = exp_data.merge(enformer_df, on='gene_name', how='inner')
    
    # Add chromosome info if missing
    if 'chromo' not in merged_data.columns:
        merged_data['chromo'] = [f'chr{hash(gene) % 22 + 1}' for gene in merged_data['gene_name']]
    
    return merged_data


def evaluate_model(model, test_features, test_labels):
    """
    Evaluate model and return correlation and predictions.
    
    Args:
        model: Trained model
        test_features: Test features
        test_labels: Test labels
        
    Returns:
        Tuple of (correlation, predictions)
    """
    model.eval()
    with torch.no_grad():
        predictions = model(test_features).detach()
    
    predictions_np = predictions.cpu().numpy().flatten()
    test_labels_np = test_labels.cpu().numpy().flatten()
    
    correlation, _ = pearsonr(test_labels_np, predictions_np)
    
    return correlation, predictions_np


def create_comparison_plot(true_values, pred_v2, pred_baseline, corr_v2, corr_baseline, cell_type, fig_path):
    """
    Create scatter plot comparing ctPred-V2 vs baseline predictions.
    
    Args:
        true_values: True expression values
        pred_v2: ctPred-V2 predictions
        pred_baseline: Baseline predictions
        corr_v2: ctPred-V2 correlation
        corr_baseline: Baseline correlation
        cell_type: Cell type name
        fig_path: Figure output directory
    """
    plt.figure(figsize=(15, 5))
    
    # Baseline plot
    plt.subplot(1, 3, 1)
    plt.scatter(true_values, pred_baseline, alpha=0.6, s=10, color='skyblue')
    plt.plot([true_values.min(), true_values.max()], [true_values.min(), true_values.max()], 'r--', alpha=0.8)
    plt.xlabel('Observed Expression')
    plt.ylabel('Predicted Expression')
    plt.title(f'Baseline ctPred\nPearson r = {corr_baseline:.4f}')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # ctPred-V2 plot
    plt.subplot(1, 3, 2)
    plt.scatter(true_values, pred_v2, alpha=0.6, s=10, color='lightcoral')
    plt.plot([true_values.min(), true_values.max()], [true_values.min(), true_values.max()], 'r--', alpha=0.8)
    plt.xlabel('Observed Expression')
    plt.ylabel('Predicted Expression')
    plt.title(f'ctPred-V2 (Fused Features)\nPearson r = {corr_v2:.4f}')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Comparison plot
    plt.subplot(1, 3, 3)
    improvement = corr_v2 - corr_baseline
    colors = ['skyblue', 'lightcoral']
    correlations = [corr_baseline, corr_v2]
    labels = ['Baseline\n(Enformer only)', 'ctPred-V2\n(Enformer + HyenaDNA)']
    
    bars = plt.bar(labels, correlations, color=colors, alpha=0.7)
    plt.ylabel('Pearson Correlation')
    plt.title(f'Performance Comparison\nImprovement: {improvement:+.4f}')
    plt.ylim([0, max(correlations) * 1.1])
    
    # Add value labels on bars
    for bar, corr in zip(bars, correlations):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.005, f'{corr:.4f}', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(fig_path, f'{cell_type}_ctPred_V2_comparison.pdf'), bbox_inches='tight', dpi=300)
    plt.savefig(os.path.join(fig_path, f'{cell_type}_ctPred_V2_comparison.png'), bbox_inches='tight', dpi=300)
    print(f"Comparison plot saved to {fig_path}")


def main():
    """
    Main function for ctPred-V2 training and evaluation.
    """
    # Set up mock data for demonstration
    print("Setting up demonstration data...")
    
    # Create mock expression data if it doesn't exist
    exp_data_path = "mock_expression_data.csv"
    if not os.path.exists(exp_data_path):
        exp_data_path = prepare_mock_expression_data()
    
    # Ensure fused features exist
    fused_features_path = "fused_features.pkl"
    if not os.path.exists(fused_features_path):
        print("Fused features not found, creating them...")
        from feature_fusion import FeatureFusion
        fusion = FeatureFusion()
        fusion.fusion_workflow("enformer_features.pkl", "hyenadna_features.pkl", fused_features_path)
    
    # Training parameters (using same chromosome splits as original ctPred)
    params = {
        "Model_path": "./models/",
        "fig_path": "./figures/",
        "training_set": ["chr1", "chr10", "chr13", "chr15", "chr16", "chr17", "chr18", "chr19", 
                        "chr2", "chr21", "chr22", "chr3", "chr4", "chr6", "chr8", "chr9", "chrX", "chrY"],
        "valid_set": ["chr11", "chr14", "chr7"],
        "test_set": ["chr12", "chr20", "chr5"]
    }
    
    # Run comparative training
    results = ctPred_V2_comparative_training(fused_features_path, exp_data_path, params)
    
    print("\n=== EXPERIMENT COMPLETE ===")
    print("Summary:")
    print(f"- Baseline (Enformer-only): {results['baseline_correlation']:.4f}")
    print(f"- ctPred-V2 (Fused features): {results['ctPred_V2_correlation']:.4f}")
    print(f"- Improvement: {results['improvement']:+.4f}")
    
    if results['improvement'] > 0:
        print("\n🎉 SUCCESS: ctPred-V2 demonstrates improved performance!")
        print("The hypothesis that combining Enformer and HyenaDNA features")
        print("leads to better gene expression prediction is SUPPORTED.")
    else:
        print("\n❌ The hypothesis was not supported in this experiment.")


if __name__ == "__main__":
    main()