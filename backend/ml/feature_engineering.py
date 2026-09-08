"""
Feature Engineering Module
===========================
Creates pharmaceutically meaningful derived features from raw process
and material data.

Every engineered feature has a clear manufacturing rationale documented
in the function docstrings. No unrealistic or domain-inappropriate 
features are created.
"""

import pandas as pd
import numpy as np


def engineer_features(df):
    """
    Create derived features with pharmaceutical manufacturing significance.
    
    Engineered features:
    
    1. api_particle_span: Particle size distribution breadth of the API.
       Formula: (api_ps09 - api_ps01) / api_ps05
       Rationale: A wider span indicates non-uniform particle sizes, 
       affecting dissolution rate and content uniformity of tablets.
    
    2. smcc_compressibility: Carr's Compressibility Index for SMCC excipient.
       Formula: (smcc_td - smcc_bd) / smcc_td × 100
       Rationale: Indicates powder flow and compressibility behavior.
       Values >25% suggest poor flow, impacting tablet weight uniformity.
    
    3. hardness_range: Range of tablet breaking force measurements.
       Formula: tbl_max_hardness - tbl_min_hardness
       Rationale: Wider range suggests process instability during compression,
       leading to variable dissolution and friability.
    
    4. thickness_uniformity: Variation in tablet thickness.
       Formula: tbl_max_thickness - tbl_min_thickness
       Rationale: Dimensional inconsistency indicates compression force or
       fill depth problems, affecting packaging and patient acceptability.
    
    5. compression_variability: Coefficient of variation of main compression force.
       Formula: main_CompForce_sd / main_CompForce_mean
       Rationale: High CV indicates inconsistent compression, leading to 
       variable hardness and dissolution profiles.
    
    6. coating_impact: Film coating contribution to tablet hardness.
       Formula: fct_av_hardness - tbl_av_hardness
       Rationale: Coating should increase hardness. Negative or excessive values
       suggest coating process issues (over-wetting, spray rate problems).
    
    7. waste_ratio: Production waste relative to batch output.
       Formula: total_waste / (total_waste + tbl_yield_proxy)
       Rationale: Higher waste ratios indicate process efficiency problems,
       startup issues, or material quality problems.
    
    Args:
        df: DataFrame with process and material columns
    
    Returns:
        pd.DataFrame: DataFrame with additional engineered features
    """
    df_eng = df.copy()
    
    # 1. API Particle Size Span
    if all(c in df_eng.columns for c in ['api_ps09', 'api_ps01', 'api_ps05']):
        df_eng['api_particle_span'] = np.where(
            df_eng['api_ps05'] != 0,
            (df_eng['api_ps09'] - df_eng['api_ps01']) / df_eng['api_ps05'],
            0
        )
        print("[Feature Eng] Created: api_particle_span (API particle size distribution breadth)")
    
    # 2. SMCC Compressibility Index (Carr's Index)
    if all(c in df_eng.columns for c in ['smcc_td', 'smcc_bd']):
        df_eng['smcc_compressibility'] = np.where(
            df_eng['smcc_td'] != 0,
            (df_eng['smcc_td'] - df_eng['smcc_bd']) / df_eng['smcc_td'] * 100,
            0
        )
        print("[Feature Eng] Created: smcc_compressibility (SMCC Carr's Index)")
    
    # 3. Hardness Range (process stability indicator)
    if all(c in df_eng.columns for c in ['tbl_max_hardness', 'tbl_min_hardness']):
        df_eng['hardness_range'] = df_eng['tbl_max_hardness'] - df_eng['tbl_min_hardness']
        print("[Feature Eng] Created: hardness_range (tablet breaking force variability)")
    
    # 4. Thickness Uniformity
    if all(c in df_eng.columns for c in ['tbl_max_thickness', 'tbl_min_thickness']):
        df_eng['thickness_uniformity'] = df_eng['tbl_max_thickness'] - df_eng['tbl_min_thickness']
        print("[Feature Eng] Created: thickness_uniformity (dimensional consistency)")
    
    # 5. Compression Force CV
    if all(c in df_eng.columns for c in ['main_CompForce_sd', 'main_CompForce_mean']):
        df_eng['compression_variability'] = np.where(
            df_eng['main_CompForce_mean'] != 0,
            df_eng['main_CompForce_sd'] / df_eng['main_CompForce_mean'],
            0
        )
        print("[Feature Eng] Created: compression_variability (compression force CV)")
    
    # 6. Coating Impact on Hardness
    if all(c in df_eng.columns for c in ['fct_av_hardness', 'tbl_av_hardness']):
        df_eng['coating_impact'] = df_eng['fct_av_hardness'] - df_eng['tbl_av_hardness']
        print("[Feature Eng] Created: coating_impact (film coating hardness contribution)")
    
    # 7. Waste Ratio
    if 'total_waste' in df_eng.columns:
        # Normalize waste by adding a small constant to avoid division by zero
        waste_total = df_eng['total_waste']
        df_eng['waste_ratio'] = waste_total / (waste_total.max() + 1)  # Normalized 0-1
        print("[Feature Eng] Created: waste_ratio (normalized production waste)")
    
    n_new = len([c for c in df_eng.columns if c not in df.columns])
    print(f"[Feature Eng] Total new features created: {n_new}")
    
    return df_eng


def engineer_single_input(input_dict):
    """
    Apply the same feature engineering to a single batch input (for prediction).
    
    Args:
        input_dict: Dictionary of feature values for one batch
    
    Returns:
        dict: Input dict augmented with engineered features
    """
    d = input_dict.copy()
    
    # API Particle Span
    if all(k in d for k in ['api_ps09', 'api_ps01', 'api_ps05']):
        d['api_particle_span'] = (
            (d['api_ps09'] - d['api_ps01']) / d['api_ps05'] 
            if d['api_ps05'] != 0 else 0
        )
    
    # SMCC Compressibility
    if all(k in d for k in ['smcc_td', 'smcc_bd']):
        d['smcc_compressibility'] = (
            (d['smcc_td'] - d['smcc_bd']) / d['smcc_td'] * 100
            if d['smcc_td'] != 0 else 0
        )
    
    # Hardness Range
    if all(k in d for k in ['tbl_max_hardness', 'tbl_min_hardness']):
        d['hardness_range'] = d['tbl_max_hardness'] - d['tbl_min_hardness']
    
    # Thickness Uniformity
    if all(k in d for k in ['tbl_max_thickness', 'tbl_min_thickness']):
        d['thickness_uniformity'] = d['tbl_max_thickness'] - d['tbl_min_thickness']
    
    # Compression Variability
    if all(k in d for k in ['main_CompForce_sd', 'main_CompForce_mean']):
        d['compression_variability'] = (
            d['main_CompForce_sd'] / d['main_CompForce_mean']
            if d['main_CompForce_mean'] != 0 else 0
        )
    
    # Coating Impact
    if all(k in d for k in ['fct_av_hardness', 'tbl_av_hardness']):
        d['coating_impact'] = d['fct_av_hardness'] - d['tbl_av_hardness']
    
    # Waste Ratio (normalized - use a fixed max from training data)
    if 'total_waste' in d:
        d['waste_ratio'] = d['total_waste'] / 50000  # Approximate normalization
    
    return d


if __name__ == '__main__':
    from data_pipeline import load_and_clean
    df = load_and_clean()
    df_eng = engineer_features(df)
    print(f"\nEngineered dataset shape: {df_eng.shape}")
    new_cols = [c for c in df_eng.columns if c not in df.columns]
    print(f"New columns: {new_cols}")
