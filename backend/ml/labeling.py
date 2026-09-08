"""
Quality Label Engineering Module
=================================
Creates Approved / Rework / Rejected quality labels based on transparent,
documented, pharmaceutically-informed rules.

WHY LABELS ARE ABSENT:
    Public pharmaceutical datasets do not contain proprietary batch release
    decisions. In real manufacturing, these are confidential QA determinations
    governed by site-specific SOPs, regulatory filings (NDA/ANDA specifications),
    and GMP requirements. Public datasets never contain proprietary release
    decisions.

IMPORTANT:
    The labels created here are PROJECT ASSUMPTIONS designed to demonstrate
    the decision-support system. They are NOT real industrial release decisions.

LABELING RULES:
    Based on pharmacopeial standards (USP, ICH) and observed data distributions:
    
    | Parameter          | Approved       | Rework          | Rejected      |
    |--------------------|----------------|-----------------|---------------|
    | dissolution_av     | >= 90%         | 80% - 89.99%    | < 80%         |
    | dissolution_min    | >= 80%         | 70% - 79.99%    | < 70%         |
    | impurities_total   | <= 0.5%        | 0.5% - 1.0%     | > 1.0%        |
    | residual_solvent   | <= 0.08        | 0.08 - 0.15     | > 0.15        |
    
    Decision Logic:
    1. If ANY parameter is in Rejected range -> Rejected
    2. If no parameter is Rejected but ANY is in Rework range -> Rework
    3. If ALL parameters are in Approved range -> Approved
    
    Thresholds were calibrated to achieve approximately:
    - 55-65% Approved, 25-30% Rework, 10-15% Rejected
"""

import pandas as pd
import numpy as np


# ============================================================
# LABELING THRESHOLD CONFIGURATION
# ============================================================
# These thresholds are documented project assumptions.
# They are based on:
#   - USP dissolution Q criteria (≥80% for immediate-release tablets)
#   - ICH Q3A/Q3B impurity limits for drug substances/products
#   - ICH Q3C residual solvent guidelines
#   - Observed data distributions in the dataset
# ============================================================

LABELING_RULES = {
    'dissolution_av': {
        'approved_min': 90.0,      # Average dissolution >= 90%
        'rework_min': 80.0,        # Between 80-90% = borderline
        'description': 'Average dissolution rate (%)'
    },
    'dissolution_min': {
        'approved_min': 80.0,      # Minimum dissolution >= 80% (USP Q criterion)
        'rework_min': 70.0,        # Between 70-80% = borderline
        'description': 'Minimum dissolution rate (%)'
    },
    'impurities_total': {
        'approved_max': 0.50,      # Total impurities <= 0.5%
        'rework_max': 1.00,        # Between 0.5-1.0% = borderline
        'description': 'Total impurities (%)'
    },
    'residual_solvent': {
        'approved_max': 0.08,      # Residual solvent <= 0.08
        'rework_max': 0.15,        # Between 0.08-0.15 = borderline
        'description': 'Residual organic solvent level'
    }
}


def classify_batch(row):
    """
    Classify a single batch row as Approved, Rework, or Rejected.
    
    Decision hierarchy:
    1. If ANY critical parameter falls in Rejected range -> Rejected
    2. If ANY parameter falls in Rework range (but none Rejected) -> Rework
    3. If ALL parameters pass Approved thresholds -> Approved
    
    Args:
        row: pandas Series containing CQA column values
    
    Returns:
        str: 'Approved', 'Rework', or 'Rejected'
    """
    has_rejected = False
    has_rework = False
    
    # Check dissolution_av (higher is better)
    if 'dissolution_av' in row.index and pd.notna(row['dissolution_av']):
        val = row['dissolution_av']
        rules = LABELING_RULES['dissolution_av']
        if val < rules['rework_min']:
            has_rejected = True
        elif val < rules['approved_min']:
            has_rework = True
    
    # Check dissolution_min (higher is better)
    if 'dissolution_min' in row.index and pd.notna(row['dissolution_min']):
        val = row['dissolution_min']
        rules = LABELING_RULES['dissolution_min']
        if val < rules['rework_min']:
            has_rejected = True
        elif val < rules['approved_min']:
            has_rework = True
    
    # Check impurities_total (lower is better)
    if 'impurities_total' in row.index and pd.notna(row['impurities_total']):
        val = row['impurities_total']
        rules = LABELING_RULES['impurities_total']
        if val > rules['rework_max']:
            has_rejected = True
        elif val > rules['approved_max']:
            has_rework = True
    
    # Check residual_solvent (lower is better)
    if 'residual_solvent' in row.index and pd.notna(row['residual_solvent']):
        val = row['residual_solvent']
        rules = LABELING_RULES['residual_solvent']
        if val > rules['rework_max']:
            has_rejected = True
        elif val > rules['approved_max']:
            has_rework = True
    
    if has_rejected:
        return 'Rejected'
    elif has_rework:
        return 'Rework'
    else:
        return 'Approved'


def create_labels(df):
    """
    Create quality labels for all batches in the dataset.
    
    Applies the rule-based labeling criteria to each batch and adds
    a 'quality_label' column.
    
    Args:
        df: DataFrame containing CQA columns
    
    Returns:
        pd.DataFrame: DataFrame with 'quality_label' column added
    """
    import os
    
    df_labeled = df.copy()
    
    print("\n" + "=" * 70)
    print("QUALITY LABEL ENGINEERING")
    print("=" * 70)
    print("\nLabeling Rules Applied:")
    for param, rules in LABELING_RULES.items():
        print(f"  {param} ({rules['description']}):")
        if 'approved_min' in rules:
            print(f"    Approved: >= {rules['approved_min']}")
            print(f"    Rework:   {rules['rework_min']} - {rules['approved_min']}")
            print(f"    Rejected: < {rules['rework_min']}")
        elif 'approved_max' in rules:
            print(f"    Approved: <= {rules['approved_max']}")
            print(f"    Rework:   {rules['approved_max']} - {rules['rework_max']}")
            print(f"    Rejected: > {rules['rework_max']}")
    
    # Apply classification
    df_labeled['quality_label'] = df_labeled.apply(classify_batch, axis=1)
    
    # Print class distribution
    dist = df_labeled['quality_label'].value_counts()
    print(f"\nClass Distribution:")
    for label in ['Approved', 'Rework', 'Rejected']:
        count = dist.get(label, 0)
        pct = count / len(df_labeled) * 100
        print(f"  {label}: {count} batches ({pct:.1f}%)")
    
    # Save labeled dataset
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    labeled_dir = os.path.join(BASE_DIR, 'data', 'labeled')
    os.makedirs(labeled_dir, exist_ok=True)
    output_path = os.path.join(labeled_dir, 'labeled_dataset.csv')
    df_labeled.to_csv(output_path, index=False)
    print(f"\nSaved labeled dataset to {output_path}")
    
    return df_labeled


# CQA columns that are used to DERIVE labels and must NOT be used as features
CQA_LABEL_COLUMNS = [
    'dissolution_av', 'dissolution_min', 'residual_solvent',
    'impurities_total', 'impurity_o', 'impurity_l'
]


def get_features_and_target(df):
    """
    Split dataset into features (X) and target (y), carefully excluding:
    - CQA columns (these generate the labels — using them would be data leakage)
    - The quality_label column itself
    - The batch identifier
    - The batch size (used only for feature engineering)
    
    DATA LEAKAGE PREVENTION:
        Quality labels are derived FROM CQA columns (dissolution, impurities,
        residual solvent). Including these columns as features would create
        circular prediction with artificially inflated accuracy.
        
        The model predicts quality from UPSTREAM parameters (process settings,
        raw materials, in-process measurements) — this is the real industrial
        use case: predicting final quality before lab results are available.
    
    Args:
        df: DataFrame with quality_label column
    
    Returns:
        tuple: (X, y) - Features DataFrame and target Series
    """
    # Columns to exclude from features
    exclude_cols = CQA_LABEL_COLUMNS + ['quality_label', 'batch', 'size']
    
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df['quality_label'].copy()
    
    # Ensure all features are numeric
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce')
    
    # Fill any remaining NaN with 0
    X.fillna(0, inplace=True)
    
    print(f"\n[Labeling] Feature matrix: {X.shape[0]} samples × {X.shape[1]} features")
    print(f"[Labeling] Target: {y.nunique()} classes")
    print(f"[Labeling] Excluded CQA columns (data leakage prevention): {CQA_LABEL_COLUMNS}")
    
    return X, y


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.ml.data_pipeline import load_and_clean
    from backend.ml.feature_engineering import engineer_features
    
    df = load_and_clean()
    df = engineer_features(df)
    df = create_labels(df)
    X, y = get_features_and_target(df)
    print(f"\nFeatures: {list(X.columns)}")
