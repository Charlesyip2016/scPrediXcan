#!/usr/bin/env python
"""
Simple script to display the ctPred-V2 comparison results
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def show_results():
    """Display the comparison plot"""
    img_path = "figures/expression_data_ctPred_V2_comparison.png"
    
    if os.path.exists(img_path):
        img = mpimg.imread(img_path)
        plt.figure(figsize=(15, 5))
        plt.imshow(img)
        plt.axis('off')
        plt.title('ctPred-V2 vs Baseline Comparison Results', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('ctPred_V2_results_display.png', dpi=150, bbox_inches='tight')
        print("✅ Results visualization saved as 'ctPred_V2_results_display.png'")
        
        # Also print the numerical results
        import json
        results_path = "models/expression_data_comparison_results.json"
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            print("\n" + "="*60)
            print("🎉 CTPRED-V2 PERFORMANCE RESULTS")
            print("="*60)
            print(f"Baseline ctPred (Enformer-only):      {results['baseline_correlation']:.4f}")
            print(f"ctPred-V2 (Enformer + HyenaDNA):      {results['ctPred_V2_correlation']:.4f}")
            print(f"Improvement:                          {results['improvement']:+.4f}")
            
            if results['improvement'] > 0:
                print("\n✅ SUCCESS: ctPred-V2 outperforms the baseline!")
                print("   The hypothesis is SUPPORTED - combining features improves prediction.")
            else:
                print("\n📊 The improvement was not achieved in this run.")
                
            print(f"\nFeature Composition:")
            print(f"  - Enformer (proximal):    {results['feature_dimensions']['enformer_contribution']} features")
            print(f"  - HyenaDNA (distal):      {results['feature_dimensions']['hyenadna_contribution']} features") 
            print(f"  - Total fused features:   {results['feature_dimensions']['ctPred_V2']} features")
            print("="*60)
    else:
        print("❌ Results plot not found. Please run the workflow first:")
        print("   python ctPred_V2_example.py")

if __name__ == "__main__":
    show_results()