"""
ctPred-V2 Example Workflow

This script demonstrates the complete workflow for the enhanced ctPred-V2 model
that combines Enformer and HyenaDNA features for improved gene expression prediction.

Usage:
    python ctPred_V2_example.py [--real-data]
    
    --real-data: Use this flag when you have real genomic data instead of mock data
"""

import os
import sys
import argparse
from enformer_features import EnformerFeatureExtractor
from hyenadna_features import HyenaDNAFeatureExtractor  
from feature_fusion import FeatureFusion
from ctPred_V2_train import ctPred_V2_comparative_training, prepare_mock_expression_data
import json


def run_ctPred_V2_workflow(use_real_data=False):
    """
    Complete ctPred-V2 workflow demonstration.
    
    Args:
        use_real_data: If True, expects real genomic data files to be provided
    """
    
    print("=== ctPred-V2 Enhanced Gene Expression Prediction ===")
    print("This workflow demonstrates the improved ctPred-V2 model that combines")
    print("Enformer (proximal epigenomic features) and HyenaDNA (distal regulatory context)")
    print("for superior cell-type-specific gene expression prediction.\n")
    
    # Step 1: Feature Extraction
    print("STEP 1: ENFORMER FEATURE EXTRACTION")
    print("-" * 50)
    
    if use_real_data:
        # Real data workflow
        reference_genome = input("Enter path to reference genome (hg38.fa): ")
        gene_annotations = input("Enter path to gene annotations (gencode.v38.annotation.gtf): ")
        
        enformer_extractor = EnformerFeatureExtractor(reference_genome_path=reference_genome)
        enformer_features = enformer_extractor.extract_and_save(gene_annotations, "enformer_features.pkl")
    else:
        # Mock data workflow
        print("Using mock data for demonstration...")
        enformer_extractor = EnformerFeatureExtractor()
        enformer_features = enformer_extractor.extract_and_save("mock_annotations.gtf", "enformer_features.pkl")
    
    print(f"✓ Extracted Enformer features for {len(enformer_features)} genes")
    print(f"  - Sequence length: 196,608 bp (proximal regulatory region)")
    print(f"  - Feature dimension: {list(enformer_features.values())[0].shape[0]}")
    
    # Step 2: HyenaDNA Feature Extraction
    print("\nSTEP 2: HYENADNA FEATURE EXTRACTION")
    print("-" * 50)
    
    if use_real_data:
        hyenadna_extractor = HyenaDNAFeatureExtractor(reference_genome_path=reference_genome)
        hyenadna_features = hyenadna_extractor.extract_and_save(gene_annotations, "hyenadna_features.pkl")
    else:
        hyenadna_extractor = HyenaDNAFeatureExtractor()
        hyenadna_features = hyenadna_extractor.extract_and_save("mock_annotations.gtf", "hyenadna_features.pkl")
    
    print(f"✓ Extracted HyenaDNA features for {len(hyenadna_features)} genes")
    print(f"  - Sequence length: 1,000,000 bp (ultra-long distal context)")
    print(f"  - Feature dimension: {list(hyenadna_features.values())[0].shape[0]}")
    
    # Step 3: Feature Fusion
    print("\nSTEP 3: FEATURE FUSION")
    print("-" * 50)
    
    fusion = FeatureFusion()
    fused_features, fused_dim = fusion.fusion_workflow(
        "enformer_features.pkl", 
        "hyenadna_features.pkl", 
        "fused_features.pkl"
    )
    
    print(f"✓ Successfully fused features")
    print(f"  - Total genes: {len(fused_features)}")
    print(f"  - Fused dimension: {fused_dim}")
    print(f"  - Enformer contribution: 5,313 features (proximal)")  
    print(f"  - HyenaDNA contribution: {fused_dim - 5313} features (distal)")
    
    # Step 4: Model Training and Evaluation
    print("\nSTEP 4: MODEL TRAINING & EVALUATION")
    print("-" * 50)
    
    # Prepare expression data
    if use_real_data:
        expression_file = input("Enter path to expression percentiles CSV: ")
    else:
        print("Creating mock expression data...")
        expression_file = prepare_mock_expression_data(len(fused_features), "expression_data.csv")
    
    # Training parameters
    params = {
        "Model_path": "./models/",
        "fig_path": "./figures/",
        "training_set": ["chr1", "chr10", "chr13", "chr15", "chr16", "chr17", "chr18", "chr19", 
                        "chr2", "chr21", "chr22", "chr3", "chr4", "chr6", "chr8", "chr9", "chrX", "chrY"],
        "valid_set": ["chr11", "chr14", "chr7"],
        "test_set": ["chr12", "chr20", "chr5"]
    }
    
    # Run comparative training
    print("Training ctPred-V2 and baseline models...")
    results = ctPred_V2_comparative_training("fused_features.pkl", expression_file, params)
    
    # Step 5: Results Summary
    print("\nSTEP 5: RESULTS SUMMARY")
    print("=" * 50)
    
    print(f"Model Performance Comparison:")
    print(f"  Baseline ctPred (Enformer-only):     {results['baseline_correlation']:.4f}")
    print(f"  ctPred-V2 (Enformer + HyenaDNA):     {results['ctPred_V2_correlation']:.4f}")
    print(f"  Improvement:                         {results['improvement']:+.4f}")
    print(f"  Relative improvement:                {results['improvement']/results['baseline_correlation']*100:+.1f}%")
    
    if results['improvement'] > 0:
        print("\n🎉 SUCCESS: Hypothesis SUPPORTED!")
        print("   The combination of Enformer and HyenaDNA features")
        print("   leads to improved gene expression prediction.")
        print("   This suggests that distal regulatory elements captured")
        print("   by HyenaDNA provide valuable complementary information.")
    else:
        print("\n📊 Result: Hypothesis not supported in this experiment.")
        print("   This could be due to:")
        print("   - Limited mock data quality")
        print("   - Need for hyperparameter optimization") 
        print("   - Requirement for real genomic data")
        print("   - Different cell type specific patterns")
    
    print(f"\nOutput files created:")
    print(f"  - enformer_features.pkl: Proximal epigenomic features")
    print(f"  - hyenadna_features.pkl: Distal regulatory context features") 
    print(f"  - fused_features.pkl: Combined feature representation")
    print(f"  - models/: Trained ctPred and ctPred-V2 models")
    print(f"  - figures/: Performance comparison plots")
    print(f"  - {results['cell_type']}_comparison_results.json: Detailed results")
    
    return results


def main():
    """
    Main function with command line interface.
    """
    parser = argparse.ArgumentParser(description='ctPred-V2 Enhanced Gene Expression Prediction')
    parser.add_argument('--real-data', action='store_true', 
                       help='Use real genomic data instead of mock data')
    
    args = parser.parse_args()
    
    try:
        results = run_ctPred_V2_workflow(use_real_data=args.real_data)
        
        print("\n" + "="*60)
        print("ctPred-V2 workflow completed successfully!")
        print("See generated files for detailed results and trained models.")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during workflow execution: {str(e)}")
        print("Please check your input data and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()