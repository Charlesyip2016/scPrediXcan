"""
Enformer Feature Extraction Module for ctPred-V2

This module provides functionality to extract Enformer features from DNA sequences
for the enhanced ctPred-V2 model that combines Enformer and HyenaDNA features.
"""

import numpy as np
import pandas as pd
import torch
import pickle
import os
from typing import Dict, List, Tuple
import warnings

# Mock Enformer model for demonstration
class MockEnformerModel:
    """
    Mock Enformer model that simulates the real Enformer API.
    In production, this would be replaced with the actual Enformer model.
    """
    def __init__(self):
        self.feature_dim = 5313
        
    def predict_on_batch(self, sequences: List[str]) -> np.ndarray:
        """
        Mock prediction that returns random features with the correct dimensionality.
        
        Args:
            sequences: List of DNA sequences (196,608 bp each)
            
        Returns:
            Array of shape (n_sequences, 896, 5313) simulating Enformer output
        """
        n_sequences = len(sequences)
        # Simulate Enformer's 896 bins output with 5313 features each
        return np.random.randn(n_sequences, 896, self.feature_dim).astype(np.float32)

class EnformerFeatureExtractor:
    """
    Enformer feature extractor for gene expression prediction.
    
    Extracts 196,608 bp DNA sequences centered on TSS and processes them
    through Enformer to generate 5,313-dimensional feature vectors.
    """
    
    def __init__(self, reference_genome_path: str = None, model=None):
        """
        Initialize the Enformer feature extractor.
        
        Args:
            reference_genome_path: Path to reference genome FASTA file
            model: Pre-loaded Enformer model (if None, uses mock model)
        """
        self.reference_genome_path = reference_genome_path
        self.sequence_length = 196608  # Enformer input sequence length
        self.feature_dim = 5313
        
        # Initialize Enformer model (using mock for demonstration)
        if model is None:
            warnings.warn("Using mock Enformer model. Replace with actual Enformer API in production.")
            self.model = MockEnformerModel()
        else:
            self.model = model
    
    def load_gene_annotations(self, annotation_path: str) -> pd.DataFrame:
        """
        Load gene annotations from GTF file.
        
        Args:
            annotation_path: Path to GENCODE GTF annotation file
            
        Returns:
            DataFrame with gene_name, chromosome, and TSS coordinates
        """
        # Mock gene annotations for demonstration
        # In production, parse actual GTF file
        mock_genes = {
            'gene_name': [f'GENE_{i:05d}' for i in range(100)],
            'chromosome': [f'chr{(i % 22) + 1}' for i in range(100)],
            'tss': [1000000 + i * 10000 for i in range(100)],
            'strand': ['+' if i % 2 == 0 else '-' for i in range(100)]
        }
        
        return pd.DataFrame(mock_genes)
    
    def extract_sequence(self, chromosome: str, tss: int, strand: str) -> str:
        """
        Extract DNA sequence centered on TSS.
        
        Args:
            chromosome: Chromosome name (e.g., 'chr1')
            tss: Transcription start site coordinate
            strand: Gene strand ('+' or '-')
            
        Returns:
            DNA sequence of length 196,608 bp
        """
        # Mock sequence extraction
        # In production, extract from actual reference genome
        half_length = self.sequence_length // 2
        start_pos = max(0, tss - half_length)
        
        # Generate mock DNA sequence
        bases = ['A', 'T', 'G', 'C']
        sequence = ''.join(np.random.choice(bases, size=self.sequence_length))
        
        return sequence
    
    def process_with_enformer(self, sequences: List[str]) -> np.ndarray:
        """
        Process DNA sequences through Enformer model.
        
        Args:
            sequences: List of DNA sequences
            
        Returns:
            Enformer predictions of shape (n_sequences, 896, 5313)
        """
        return self.model.predict_on_batch(sequences)
    
    def compute_gene_features(self, enformer_output: np.ndarray) -> np.ndarray:
        """
        Compute final gene features from Enformer output.
        
        Following original ctPred approach: average central four bins.
        
        Args:
            enformer_output: Array of shape (n_sequences, 896, 5313)
            
        Returns:
            Gene features of shape (n_sequences, 5313)
        """
        # Average central four bins (bins 446-449, 0-indexed)
        central_bins = enformer_output[:, 446:450, :]  # Shape: (n_sequences, 4, 5313)
        gene_features = np.mean(central_bins, axis=1)  # Shape: (n_sequences, 5313)
        
        return gene_features
    
    def extract_features_for_genes(self, gene_annotations: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Extract Enformer features for all genes.
        
        Args:
            gene_annotations: DataFrame with gene information
            
        Returns:
            Dictionary mapping gene_name to feature vector
        """
        gene_features = {}
        
        # Process in batches for efficiency
        batch_size = 32
        n_genes = len(gene_annotations)
        
        for batch_start in range(0, n_genes, batch_size):
            batch_end = min(batch_start + batch_size, n_genes)
            batch_genes = gene_annotations.iloc[batch_start:batch_end]
            
            # Extract sequences for batch
            sequences = []
            gene_names = []
            
            for _, gene in batch_genes.iterrows():
                sequence = self.extract_sequence(
                    gene['chromosome'], 
                    gene['tss'], 
                    gene['strand']
                )
                sequences.append(sequence)
                gene_names.append(gene['gene_name'])
            
            # Process through Enformer
            enformer_output = self.process_with_enformer(sequences)
            
            # Compute final features
            batch_features = self.compute_gene_features(enformer_output)
            
            # Store features
            for gene_name, features in zip(gene_names, batch_features):
                gene_features[gene_name] = features
                
            print(f"Processed {batch_end}/{n_genes} genes...")
        
        return gene_features
    
    def save_features(self, gene_features: Dict[str, np.ndarray], output_path: str):
        """
        Save gene features to pickle file.
        
        Args:
            gene_features: Dictionary of gene features
            output_path: Output file path
        """
        with open(output_path, 'wb') as f:
            pickle.dump(gene_features, f)
        print(f"Saved Enformer features to {output_path}")
    
    def extract_and_save(self, annotation_path: str, output_path: str = "enformer_features.pkl") -> Dict[str, np.ndarray]:
        """
        Complete workflow: extract and save Enformer features.
        
        Args:
            annotation_path: Path to gene annotation file
            output_path: Output pickle file path
            
        Returns:
            Dictionary of gene features
        """
        print("Loading gene annotations...")
        gene_annotations = self.load_gene_annotations(annotation_path)
        
        print(f"Extracting Enformer features for {len(gene_annotations)} genes...")
        gene_features = self.extract_features_for_genes(gene_annotations)
        
        print("Saving features...")
        self.save_features(gene_features, output_path)
        
        return gene_features


def main():
    """
    Example usage of Enformer feature extraction.
    """
    # Initialize extractor
    extractor = EnformerFeatureExtractor()
    
    # Extract features (using mock data)
    mock_annotation_path = "mock_annotations.gtf"
    features = extractor.extract_and_save(mock_annotation_path, "enformer_features.pkl")
    
    print(f"Extracted features for {len(features)} genes")
    print(f"Feature dimensionality: {list(features.values())[0].shape}")


if __name__ == "__main__":
    main()