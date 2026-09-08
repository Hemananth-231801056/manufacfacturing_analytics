"""
Model Training Script
======================
Entry point to run the full ML pipeline:
    Load Data → Clean → Engineer Features → Label → Train → Evaluate → Save

Usage:
    python scripts/train_model.py
"""

import sys
import os

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.ml.data_pipeline import load_and_clean
from backend.ml.feature_engineering import engineer_features
from backend.ml.labeling import create_labels, get_features_and_target
from backend.ml.training import train_models
from backend.ml.explainer import get_global_explanation

import joblib
import numpy as np


def main():
    """Run the complete training pipeline."""
    
    print("=" * 70)
    print("  Pharmaceutical Batch Quality Prediction — Training Pipeline")
    print("=" * 70)
    
    # Step 1: Load and clean data
    print("\n[Step 1] Loading and cleaning data...")
    df = load_and_clean()
    
    # Step 2: Engineer features
    print("\n[Step 2] Engineering features...")
    df = engineer_features(df)
    
    # Step 3: Create quality labels
    print("\n[Step 3] Creating quality labels...")
    df = create_labels(df)
    
    # Step 4: Prepare features and target
    print("\n[Step 4] Preparing features and target...")
    X, y = get_features_and_target(df)
    
    # Print dataset summary
    print("\n" + "=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)
    print(f"  Total batches: {len(df)}")
    print(f"  Features: {X.shape[1]}")
    print(f"  Feature names: {list(X.columns)}")
    print(f"\n  Class distribution:")
    for label in ['Approved', 'Rework', 'Rejected']:
        count = (y == label).sum()
        pct = count / len(y) * 100
        print(f"    {label}: {count} ({pct:.1f}%)")
    
    # Step 5: Train models
    print("\n[Step 5] Training models...")
    results = train_models(X, y)
    
    # Step 6: Generate global SHAP explanation
    print("\n[Step 6] Generating SHAP explanations...")
    models_dir = os.path.join(PROJECT_ROOT, 'models')
    try:
        model = joblib.load(os.path.join(models_dir, 'best_model.joblib'))
        scaler = joblib.load(os.path.join(models_dir, 'scaler.joblib'))
        feature_names = joblib.load(os.path.join(models_dir, 'feature_names.joblib'))
        
        X_scaled = scaler.transform(X)
        # Use a sample for SHAP (full dataset can be slow)
        sample_size = min(200, len(X))
        np.random.seed(42)
        sample_idx = np.random.choice(len(X), sample_size, replace=False)
        
        importance = get_global_explanation(
            model, X_scaled[sample_idx], feature_names, save_plot=True
        )
        
        print("\nTop 10 Most Important Features (Global SHAP):")
        for i, (feat, val) in enumerate(list(importance.items())[:10]):
            print(f"  {i+1}. {feat}: {val:.4f}")
    except Exception as e:
        print(f"  Warning: SHAP generation failed: {e}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("  Training Pipeline Complete!")
    print("=" * 70)
    print(f"\n  Best Model: {results.get('best_model', 'Unknown')}")
    print(f"  Best F1 (weighted): {results.get('best_f1_weighted', 0):.4f}")
    print(f"  Model artifacts saved to: {models_dir}")
    
    return results


if __name__ == '__main__':
    main()
