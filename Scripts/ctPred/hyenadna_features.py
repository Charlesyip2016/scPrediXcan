"""
HyenaDNA Feature Extraction Module for ctPred-V2

This module provides functionality to extract HyenaDNA features from ultra-long DNA sequences
for the enhanced ctPred-V2 model that combines Enformer and HyenaDNA features.
"""

import numpy as np
import pandas as pd
import torch
import pickle
import os
from typing import Dict, List, Tuple
import warnings

# Mock HyenaDNA model for demonstration
class MockHyenaDNAModel:
    """
    Mock HyenaDNA model that simulates the real HyenaDNA API.
    In production, this would be replaced with the actual HyenaDNA model.
    """
    def __init__(self):
        self.feature_dim = 256  # Typical embedding dimension for HyenaDNA
        
    def encode_sequences(self, sequences: List[str]) -> np.ndarray:
        """
        Mock encoding that returns random features with the correct dimensionality.
        
        Args:
            sequences: List of ultra-long DNA sequences (1,000,000 bp each)
            
        Returns:
            Array of shape (n_sequences, feature_dim) simulating HyenaDNA global embeddings
        """
        n_sequences = len(sequences)
        # Simulate HyenaDNA's global embedding output
        return np.random.randn(n_sequences, self.feature_dim).astype(np.float32)

class HyenaDNAFeatureExtractor:
    """
    HyenaDNA feature extractor for capturing distal regulatory elements.
    
    Extracts 1,000,000 bp DNA sequences centered on TSS and processes them
    through HyenaDNA to generate global embedding vectors for distal context.
    """
    
    def __init__(self, reference_genome_path: str = None, model=None):
        """
        Initialize the HyenaDNA feature extractor.
        
        Args:
            reference_genome_path: Path to reference genome FASTA file
            model: Pre-loaded HyenaDNA model (if None, uses mock model)
        """
        self.reference_genome_path = reference_genome_path
        self.sequence_length = 1000000  # Ultra-long context for distal elements
        self.feature_dim = 256  # HyenaDNA embedding dimension
        
        # Initialize HyenaDNA model (using mock for demonstration)
        if model is None:
            warnings.warn("Using mock HyenaDNA model. Replace with actual HyenaDNA API in production.")
            self.model = MockHyenaDNAModel()
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
        # In production, parse actual GTF file or reuse from Enformer extractor
        mock_genes = {
            'gene_name': [f'GENE_{i:05d}' for i in range(100)],
            'chromosome': [f'chr{(i % 22) + 1}' for i in range(100)],
            'tss': [1000000 + i * 10000 for i in range(100)],
            'strand': ['+' if i % 2 == 0 else '-' for i in range(100)]
        }
        
        return pd.DataFrame(mock_genes)
    
    def extract_ultralong_sequence(self, chromosome: str, tss: int, strand: str) -> str:
        """
        Extract ultra-long DNA sequence centered on TSS for distal regulatory elements.
        
        Args:
            chromosome: Chromosome name (e.g., 'chr1')
            tss: Transcription start site coordinate
            strand: Gene strand ('+' or '-')
            
        Returns:
            DNA sequence of length 1,000,000 bp
        """
        # Mock sequence extraction
        # In production, extract from actual reference genome
        half_length = self.sequence_length // 2
        start_pos = max(0, tss - half_length)
        
        # Generate mock DNA sequence
        bases = ['A', 'T', 'G', 'C']
        sequence = ''.join(np.random.choice(bases, size=self.sequence_length))
        
        return sequence
    
    def process_with_hyenadna(self, sequences: List[str]) -> np.ndarray:
        """
        Process ultra-long DNA sequences through HyenaDNA model.
        
        Args:
            sequences: List of ultra-long DNA sequences
            
        Returns:
            HyenaDNA global embeddings of shape (n_sequences, feature_dim)
        """
        return self.model.encode_sequences(sequences)
    
    def extract_features_for_genes(self, gene_annotations: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Extract HyenaDNA features for all genes.
        
        Args:
            gene_annotations: DataFrame with gene information
            
        Returns:
            Dictionary mapping gene_name to feature vector
        """
        gene_features = {}
        
        # Process in smaller batches due to large sequence length
        batch_size = 8  # Smaller batches for ultra-long sequences
        n_genes = len(gene_annotations)
        
        for batch_start in range(0, n_genes, batch_size):
            batch_end = min(batch_start + batch_size, n_genes)
            batch_genes = gene_annotations.iloc[batch_start:batch_end]
            
            # Extract ultra-long sequences for batch
            sequences = []
            gene_names = []
            
            for _, gene in batch_genes.iterrows():
                sequence = self.extract_ultralong_sequence(
                    gene['chromosome'], 
                    gene['tss'], 
                    gene['strand']
                )
                sequences.append(sequence)
                gene_names.append(gene['gene_name'])
            
            # Process through HyenaDNA
            hyena_features = self.process_with_hyenadna(sequences)
            
            # Store features
            for gene_name, features in zip(gene_names, hyena_features):
                gene_features[gene_name] = features
                
            print(f"Processed {batch_end}/{n_genes} genes with HyenaDNA...")
        
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
        print(f"Saved HyenaDNA features to {output_path}")
    
    def extract_and_save(self, annotation_path: str, output_path: str = "hyenadna_features.pkl") -> Dict[str, np.ndarray]:
        """
        Complete workflow: extract and save HyenaDNA features.
        
        Args:
            annotation_path: Path to gene annotation file
            output_path: Output pickle file path
            
        Returns:
            Dictionary of gene features
        """
        print("Loading gene annotations for HyenaDNA...")
        gene_annotations = self.load_gene_annotations(annotation_path)
        
        print(f"Extracting HyenaDNA features for {len(gene_annotations)} genes...")
        print("Note: Processing ultra-long sequences (1M bp) for distal regulatory elements...")
        gene_features = self.extract_features_for_genes(gene_annotations)
        
        print("Saving HyenaDNA features...")
        self.save_features(gene_features, output_path)
        
        return gene_features


def main():
    """
    Example usage of HyenaDNA feature extraction.
    """
    # Initialize extractor
    extractor = HyenaDNAFeatureExtractor()
    
    # Extract features (using mock data)
    mock_annotation_path = "mock_annotations.gtf"
    features = extractor.extract_and_save(mock_annotation_path, "hyenadna_features.pkl")
    
    print(f"Extracted HyenaDNA features for {len(features)} genes")
    print(f"Feature dimensionality: {list(features.values())[0].shape}")


if __name__ == "__main__":
    main()