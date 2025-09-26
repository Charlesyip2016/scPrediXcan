#!/usr/bin/env python
"""
Simple script to display one of the key validation figures.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def display_key_figure():
    """Display a key validation figure."""
    
    # Show the SHH-ZRS mechanism diagram as it's the most illustrative
    fig_path = "scpredixcan_v2_final_report/figures/task2_shh_zrs_mechanism.png"
    
    if os.path.exists(fig_path):
        print("📊 Displaying key validation figure...")
        
        img = mpimg.imread(fig_path)
        plt.figure(figsize=(16, 8))
        plt.imshow(img)
        plt.axis('off')
        plt.title('scPrediXcan-V2 Breakthrough: SHH Gene Regulation by Distal ZRS Enhancer', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        # Save display version
        plt.savefig('validation_showcase.png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print("✅ Key figure saved as 'validation_showcase.png'")
        print("🔬 This diagram illustrates why context window size is critical")
        print("   for capturing distal regulatory relationships like SHH-ZRS")
        
        return 'validation_showcase.png'
    else:
        print(f"❌ Figure not found: {fig_path}")
        return None

if __name__ == "__main__":
    display_key_figure()