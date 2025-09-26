# ctPred-V2: Enhanced Gene Expression Prediction with Fused Enformer + HyenaDNA Features

This directory contains the implementation of **ctPred-V2**, an enhanced version of the original ctPred model that combines Enformer and HyenaDNA features for improved cell-type-specific gene expression prediction.

## Overview

ctPred-V2 addresses a key limitation of the original ctPred model by incorporating both:
- **Enformer features**: Proximal epigenomic features from 196kb sequences (5,313 dimensions)
- **HyenaDNA features**: Distal regulatory context from 1Mb sequences (256 dimensions)

The hypothesis is that Enformer excels at predicting proximal epigenomic features, while HyenaDNA's strength lies in capturing long-range dependencies from distal regulatory elements due to its ability to process million-base-pair contexts.

## Key Features

- ✅ **Same Architecture**: Uses proven 4-layer MLP design, only input dimension changes
- ✅ **Backward Compatible**: Original ctPred functionality remains unchanged
- ✅ **Modular Design**: Clear separation between feature extraction, fusion, and modeling
- ✅ **Comprehensive Evaluation**: Built-in comparison with baseline ctPred
- ✅ **Easy to Use**: Single command workflow with example scripts

## Quick Start

### Option 1: Run the complete example workflow
```bash
python ctPred_V2_example.py
```

### Option 2: Step-by-step execution
```bash
# Step 1: Extract Enformer features
python enformer_features.py

# Step 2: Extract HyenaDNA features  
python hyenadna_features.py

# Step 3: Fuse features
python feature_fusion.py

# Step 4: Train and evaluate
python ctPred_V2_train.py
```

## File Structure

### Core Modules
- **`enformer_features.py`**: Enformer feature extraction (196kb sequences → 5,313 features)
- **`hyenadna_features.py`**: HyenaDNA feature extraction (1Mb sequences → 256 features)
- **`feature_fusion.py`**: Feature fusion system (5,313 + 256 → 5,569 features)
- **`ctPred_utils.py`**: Enhanced utilities with ctPred_V2 class and data handling
- **`ctPred_V2_train.py`**: Complete training and evaluation pipeline

### User Interface
- **`ctPred_V2_example.py`**: User-friendly workflow demonstration
- **`ctPred_V2_config.json`**: Configuration file with all parameters
- **`.gitignore`**: Excludes generated files from version control

### Generated Files (excluded from git)
- **`*.pkl`**: Feature files (enformer_features.pkl, hyenadna_features.pkl, fused_features.pkl)
- **`models/`**: Trained model files and results
- **`figures/`**: Performance comparison plots

## Detailed Workflow

### Step 1: Enformer Feature Extraction
```python
from enformer_features import EnformerFeatureExtractor

extractor = EnformerFeatureExtractor()
features = extractor.extract_and_save("annotations.gtf", "enformer_features.pkl")
```
- Extracts 196,608 bp sequences centered on TSS
- Processes through Enformer model to get 5,313-dimensional features
- Averages central four bins following original ctPred methodology

### Step 2: HyenaDNA Feature Extraction
```python
from hyenadna_features import HyenaDNAFeatureExtractor

extractor = HyenaDNAFeatureExtractor()
features = extractor.extract_and_save("annotations.gtf", "hyenadna_features.pkl")
```
- Extracts 1,000,000 bp sequences centered on TSS for distal context
- Processes through HyenaDNA model to get global embedding vectors
- Captures long-range regulatory dependencies

### Step 3: Feature Fusion
```python
from feature_fusion import FeatureFusion

fusion = FeatureFusion()
fused_features, dim = fusion.fusion_workflow(
    "enformer_features.pkl", 
    "hyenadna_features.pkl", 
    "fused_features.pkl"
)
```
- Validates feature compatibility
- Concatenates Enformer and HyenaDNA features
- Creates unified 5,569-dimensional representation

### Step 4: Model Training and Evaluation
```python
from ctPred_utils import ctPred_V2

# Create ctPred-V2 model with fused features
model = ctPred_V2(input_dim=5569)

# Training happens automatically with comparison to baseline
```

## Model Architecture

### ctPred-V2 Architecture
```
Input Layer (5,569 features)
    ↓
Linear + ReLU + Dropout (64 hidden units)
    ↓
Linear + ReLU + Dropout (64 hidden units) 
    ↓
Linear + ReLU + Dropout (64 hidden units)
    ↓
Linear + ReLU + Dropout (64 hidden units)
    ↓
Output Layer (1 unit - gene expression)
```

### Key Parameters
- **Layers**: 4 hidden layers
- **Hidden units**: 64 per layer
- **Dropout**: 0.05
- **Learning rate**: 9e-5
- **Regularization**: L2 with λ=5e-4
- **Batch size**: 1,000
- **Epochs**: 100

## Feature Specifications

| Feature Set | Sequence Length | Dimension | Context | Purpose |
|-------------|----------------|-----------|---------|---------|
| Enformer | 196,608 bp | 5,313 | Proximal TSS region | Epigenomic features |
| HyenaDNA | 1,000,000 bp | 256 | Extended regulatory region | Distal dependencies |
| **Fused** | **Both** | **5,569** | **Complete regulatory context** | **Enhanced prediction** |

## Expected Results

The ctPred-V2 model is expected to outperform the baseline ctPred model by incorporating both proximal and distal regulatory information:

- **Baseline ctPred**: Uses only Enformer features (5,313-dim)
- **ctPred-V2**: Uses fused features (5,569-dim) 
- **Metric**: Pearson correlation on test set
- **Success Criteria**: Positive improvement over baseline

## Configuration

All parameters can be customized via `ctPred_V2_config.json`:

```json
{
  "model_config": {
    "ctPred_V2": {
      "input_dim": 5569,
      "num_layers": 4,
      "hidden_dim": 64,
      "learning_rate": 9e-5
    }
  },
  "training_config": {
    "chromosome_splits": {
      "training_set": ["chr1", "chr10", ...],
      "valid_set": ["chr11", "chr14", "chr7"],
      "test_set": ["chr12", "chr20", "chr5"]
    }
  }
}
```

## Real Data Usage

For real genomic data, provide the required files:

```bash
python ctPred_V2_example.py --real-data
```

Required inputs:
- **Reference Genome**: `path/to/hg38.fa`  
- **Gene Annotations**: `path/to/gencode.v38.annotation.gtf`
- **Expression Data**: `path/to/pseudobulk_expression_percentiles.csv`

## Technical Notes

### Mock vs Real Models
The current implementation uses mock models for Enformer and HyenaDNA to demonstrate the workflow. For production use:

1. Replace `MockEnformerModel` with actual Enformer API
2. Replace `MockHyenaDNAModel` with actual HyenaDNA API
3. Update sequence extraction to use real reference genome

### Computational Requirements
- **Memory**: ~2-4 GB for mock data, more for real genomic sequences
- **Processing**: CPU-based, GPU support available
- **Storage**: Feature files can be large (100MB-1GB depending on gene count)

### Customization
The modular design allows easy customization:
- **Different architectures**: Modify `ctPred_V2` class
- **Alternative fusion methods**: Update `FeatureFusion` class
- **Additional feature sets**: Extend the extraction modules

## Troubleshooting

**Issue**: Import errors
```bash
# Make sure you're in the correct directory
cd Scripts/ctPred
source $(conda info --base)/etc/profile.d/conda.sh
conda activate scPrediXcan
```

**Issue**: CUDA errors
- The code automatically detects available hardware (CPU/GPU)
- All operations work on both CPU and GPU

**Issue**: Memory issues
- Reduce batch size in configuration
- Process genes in smaller batches
- Use CPU instead of GPU if needed

## Citation

If you use ctPred-V2 in your research, please cite the original scPrediXcan paper and mention the enhanced ctPred-V2 implementation.

## Contributing

This implementation extends the original scPrediXcan framework. For contributions:
1. Maintain backward compatibility
2. Follow the modular design pattern
3. Include appropriate tests and documentation
4. Ensure minimal changes to existing functionality