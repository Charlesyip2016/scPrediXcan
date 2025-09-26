"""
Feature Fusion Module for ctPred-V2

This module provides functionality to combine Enformer and HyenaDNA features
into a unified feature representation for enhanced gene expression prediction.
"""

import numpy as np
import pickle
import os
from typing import Dict, Tuple, Optional, List
import warnings

class FeatureFusion:
    """
    Feature fusion system for combining Enformer and HyenaDNA features.
    
    Combines proximal epigenomic features from Enformer with distal regulatory
    context from HyenaDNA to create a richer feature representation.
    """
    
    def __init__(self):
        """Initialize the feature fusion system."""
        self.enformer_dim = 5313  # Expected Enformer feature dimension
        self.hyenadna_dim = 256   # Expected HyenaDNA feature dimension
        self.fused_dim = self.enformer_dim + self.hyenadna_dim  # Total fused dimension
    
    def load_features(self, enformer_path: str, hyenadna_path: str) -> Tuple[Dict, Dict]:
        """
        Load both Enformer and HyenaDNA features from pickle files.
        
        Args:
            enformer_path: Path to Enformer features pickle file
            hyenadna_path: Path to HyenaDNA features pickle file
            
        Returns:
            Tuple of (enformer_features, hyenadna_features) dictionaries
        """
        print("Loading Enformer features...")
        with open(enformer_path, 'rb') as f:
            enformer_features = pickle.load(f)
        
        print("Loading HyenaDNA features...")
        with open(hyenadna_path, 'rb') as f:
            hyenadna_features = pickle.load(f)
        
        print(f"Loaded {len(enformer_features)} Enformer features")
        print(f"Loaded {len(hyenadna_features)} HyenaDNA features")
        
        return enformer_features, hyenadna_features
    
    def validate_features(self, enformer_features: Dict, hyenadna_features: Dict) -> List[str]:
        """
        Validate feature compatibility and return common gene names.
        
        Args:
            enformer_features: Dictionary of Enformer features
            hyenadna_features: Dictionary of HyenaDNA features
            
        Returns:
            List of gene names common to both feature sets
        """
        # Check feature dimensions
        sample_enformer = list(enformer_features.values())[0]
        sample_hyenadna = list(hyenadna_features.values())[0]
        
        if sample_enformer.shape[0] != self.enformer_dim:
            warnings.warn(f"Enformer features have dimension {sample_enformer.shape[0]}, expected {self.enformer_dim}")
        
        if sample_hyenadna.shape[0] != self.hyenadna_dim:
            warnings.warn(f"HyenaDNA features have dimension {sample_hyenadna.shape[0]}, expected {self.hyenadna_dim}")
        
        # Find common genes
        enformer_genes = set(enformer_features.keys())
        hyenadna_genes = set(hyenadna_features.keys())
        common_genes = enformer_genes.intersection(hyenadna_genes)
        
        print(f"Common genes between feature sets: {len(common_genes)}")
        print(f"Enformer-only genes: {len(enformer_genes - hyenadna_genes)}")
        print(f"HyenaDNA-only genes: {len(hyenadna_genes - enformer_genes)}")
        
        if len(common_genes) == 0:
            raise ValueError("No common genes found between Enformer and HyenaDNA features!")
        
        return list(common_genes)
    
    def fuse_features(self, 
                     enformer_features: Dict, 
                     hyenadna_features: Dict,
                     common_genes: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """
        Fuse Enformer and HyenaDNA features by concatenation.
        
        Args:
            enformer_features: Dictionary of Enformer features
            hyenadna_features: Dictionary of HyenaDNA features
            common_genes: List of genes to process (if None, uses all common genes)
            
        Returns:
            Dictionary of fused features
        """
        if common_genes is None:
            common_genes = self.validate_features(enformer_features, hyenadna_features)
        
        fused_features = {}
        
        print(f"Fusing features for {len(common_genes)} genes...")
        
        for gene_name in common_genes:
            # Get individual features
            enformer_vec = enformer_features[gene_name]
            hyenadna_vec = hyenadna_features[gene_name]
            
            # Ensure features are 1D arrays
            if len(enformer_vec.shape) > 1:
                enformer_vec = enformer_vec.flatten()
            if len(hyenadna_vec.shape) > 1:
                hyenadna_vec = hyenadna_vec.flatten()
            
            # Concatenate features
            fused_vec = np.concatenate([enformer_vec, hyenadna_vec])
            fused_features[gene_name] = fused_vec
        
        # Validate fused dimension
        sample_fused = list(fused_features.values())[0]
        expected_dim = self.enformer_dim + self.hyenadna_dim
        actual_dim = sample_fused.shape[0]
        
        if actual_dim != expected_dim:
            warnings.warn(f"Fused features have dimension {actual_dim}, expected {expected_dim}")
        
        print(f"Successfully fused features with dimension: {actual_dim}")
        
        return fused_features
    
    def save_fused_features(self, fused_features: Dict[str, np.ndarray], output_path: str):
        """
        Save fused features to pickle file.
        
        Args:
            fused_features: Dictionary of fused features
            output_path: Output file path
        """
        with open(output_path, 'wb') as f:
            pickle.dump(fused_features, f)
        print(f"Saved fused features to {output_path}")
    
    def get_feature_statistics(self, features: Dict[str, np.ndarray]) -> Dict:
        """
        Compute statistics for feature analysis.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Dictionary of feature statistics
        """
        feature_matrix = np.array(list(features.values()))
        
        stats = {
            'n_genes': len(features),
            'feature_dim': feature_matrix.shape[1],
            'mean': np.mean(feature_matrix, axis=0),
            'std': np.std(feature_matrix, axis=0),
            'min': np.min(feature_matrix, axis=0),
            'max': np.max(feature_matrix, axis=0)
        }
        
        return stats
    
    def fusion_workflow(self, 
                       enformer_path: str, 
                       hyenadna_path: str, 
                       output_path: str = "fused_features.pkl") -> Tuple[Dict[str, np.ndarray], int]:
        """
        Complete feature fusion workflow.
        
        Args:
            enformer_path: Path to Enformer features
            hyenadna_path: Path to HyenaDNA features
            output_path: Output path for fused features
            
        Returns:
            Tuple of (fused_features_dict, fused_dimension)
        """
        print("=== Feature Fusion Workflow ===")
        
        # Load features
        enformer_features, hyenadna_features = self.load_features(enformer_path, hyenadna_path)
        
        # Validate and find common genes
        common_genes = self.validate_features(enformer_features, hyenadna_features)
        
        # Fuse features
        fused_features = self.fuse_features(enformer_features, hyenadna_features, common_genes)
        
        # Save results
        self.save_fused_features(fused_features, output_path)
        
        # Report statistics
        stats = self.get_feature_statistics(fused_features)
        print(f"\nFusion Summary:")
        print(f"- Genes processed: {stats['n_genes']}")
        print(f"- Fused feature dimension: {stats['feature_dim']}")
        print(f"- Enformer contribution: {self.enformer_dim} features")
        print(f"- HyenaDNA contribution: {self.hyenadna_dim} features")
        
        return fused_features, stats['feature_dim']


def main():
    """
    Example usage of feature fusion.
    """
    # Initialize fusion system
    fusion = FeatureFusion()
    
    # Mock feature files (these would be created by the extraction modules)
    enformer_path = "enformer_features.pkl"
    hyenadna_path = "hyenadna_features.pkl"
    
    # Check if files exist, create mock data if needed
    if not os.path.exists(enformer_path) or not os.path.exists(hyenadna_path):
        print("Creating mock feature files for demonstration...")
        
        # Create mock Enformer features
        mock_enformer = {f'GENE_{i:05d}': np.random.randn(5313).astype(np.float32) for i in range(50)}
        with open(enformer_path, 'wb') as f:
            pickle.dump(mock_enformer, f)
        
        # Create mock HyenaDNA features
        mock_hyenadna = {f'GENE_{i:05d}': np.random.randn(256).astype(np.float32) for i in range(50)}
        with open(hyenadna_path, 'wb') as f:
            pickle.dump(mock_hyenadna, f)
    
    # Run fusion workflow
    fused_features, fused_dim = fusion.fusion_workflow(
        enformer_path, 
        hyenadna_path, 
        "fused_features.pkl"
    )
    
    print(f"\nFusion complete! Created features for {len(fused_features)} genes")
    print(f"Fused feature dimensionality: {fused_dim}")


if __name__ == "__main__":
    main()