"""
Data Pipeline Module
====================
Handles loading, merging, and cleaning of pharmaceutical manufacturing data.

Files processed:
- Laboratory.csv: 55 columns of raw material quality, in-process tablet measurements, final lab release tests
- Process.csv: 35 columns of compression machine sensor data, startup metrics
- Both files share 'batch' and 'code' as merge keys

Manufacturing Context:
    This pipeline processes real industrial pharmaceutical tableting data from
    Žagar & Mihelič (Scientific Data, 2022). The data covers 1,005 production
    batches across 25 product formulations.
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

# Base path for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')


def load_raw_data():
    """
    Load Laboratory.csv and Process.csv with proper delimiter and NA handling.
    
    Both files use semicolon (;) as delimiter.
    Missing values are encoded as '#N/A' in Process.csv and whitespace in Laboratory.csv.
    
    Returns:
        tuple: (lab_df, process_df) - Raw DataFrames
    """
    lab_path = os.path.join(RAW_DATA_DIR, 'Laboratory.csv')
    process_path = os.path.join(RAW_DATA_DIR, 'Process.csv')
    
    # Load with semicolon delimiter and proper NA handling
    lab_df = pd.read_csv(lab_path, sep=';', na_values=['#N/A', ''])
    process_df = pd.read_csv(process_path, sep=';', na_values=['#N/A', ''])
    
    print(f"[Data Pipeline] Laboratory.csv loaded: {lab_df.shape[0]} rows, {lab_df.shape[1]} columns")
    print(f"[Data Pipeline] Process.csv loaded: {process_df.shape[0]} rows, {process_df.shape[1]} columns")
    
    return lab_df, process_df


def clean_laboratory_data(lab_df):
    """
    Clean Laboratory.csv:
    - Fix whitespace-padded api_l_impurity column (convert to numeric)
    - Fix column name typo: resodual_solvent -> residual_solvent
    - Convert all numeric columns to float64
    
    Args:
        lab_df: Raw laboratory DataFrame
    
    Returns:
        pd.DataFrame: Cleaned laboratory data
    """
    df = lab_df.copy()
    
    # Fix column name typo
    df.rename(columns={'resodual_solvent': 'residual_solvent'}, inplace=True)
    
    # Non-numeric columns
    non_numeric = ['batch', 'code', 'strength', 'start', 'api_code', 
                    'api_batch', 'smcc_batch', 'lactose_batch', 'starch_batch']
    
    for col in df.columns:
        if col not in non_numeric:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.strip().str.replace(',', '.'), 
                errors='coerce'
            ).astype(float)
    
    print(f"[Data Pipeline] Laboratory data cleaned. Missing values per column:")
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if len(missing_cols) > 0:
        for col, count in missing_cols.items():
            print(f"  - {col}: {count} missing ({count/len(df)*100:.1f}%)")
    else:
        print("  - No missing values detected")
    
    return df


def clean_process_data(process_df):
    """
    Clean Process.csv:
    - Fix column name with space: 'main_CompForce mean' -> 'main_CompForce_mean'
    - Encode weekend (yes/no -> 1/0)
    - Convert process numerical columns to float64
    
    Args:
        process_df: Raw process DataFrame
    
    Returns:
        pd.DataFrame: Cleaned process data
    """
    df = process_df.copy()
    
    # Fix column name with space
    df.rename(columns={'main_CompForce mean': 'main_CompForce_mean'}, inplace=True)
    
    # Encode weekend: yes -> 1, no -> 0
    if 'weekend' in df.columns:
        df['weekend'] = df['weekend'].map({'yes': 1, 'no': 0}).fillna(0).astype(int)
    
    non_numeric = ['batch', 'code', 'weekend']
    for col in df.columns:
        if col not in non_numeric:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.strip().str.replace(',', '.'), 
                errors='coerce'
            ).astype(float)
    
    print(f"[Data Pipeline] Process data cleaned. Missing values per column:")
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if len(missing_cols) > 0:
        for col, count in missing_cols.items():
            print(f"  - {col}: {count} missing ({count/len(df)*100:.1f}%)")
    else:
        print("  - No missing values detected")
    
    return df


def merge_datasets(lab_df, process_df):
    """
    Merge Laboratory and Process data on batch + code (inner join).
    
    Drop duplicate CQA columns from Process.csv (keep Lab versions as authoritative):
    - 'Drug release average (%)' duplicates 'dissolution_av'
    - 'Drug release min (%)' duplicates 'dissolution_min'  
    - 'Residual solvent' duplicates 'residual_solvent'
    - 'Total impurities' duplicates 'impurities_total'
    - 'Impurity O' duplicates 'impurity_o'
    - 'Impurity L' duplicates 'impurity_l'
    
    Args:
        lab_df: Cleaned laboratory DataFrame
        process_df: Cleaned process DataFrame
    
    Returns:
        pd.DataFrame: Merged dataset
    """
    # Drop duplicate CQA columns from process data before merge
    process_cqa_cols = [
        'Drug release average (%)', 'Drug release min (%)',
        'Residual solvent', 'Total impurities', 'Impurity O', 'Impurity L'
    ]
    process_clean = process_df.drop(columns=[c for c in process_cqa_cols if c in process_df.columns])
    
    # Merge on batch + code
    merged = pd.merge(lab_df, process_clean, on=['batch', 'code'], how='inner')
    
    print(f"[Data Pipeline] Merged dataset: {merged.shape[0]} rows, {merged.shape[1]} columns")
    print(f"[Data Pipeline] Unique product codes: {merged['code'].nunique()}")
    
    return merged


def drop_identifiers(df):
    """
    Drop identifier and tracking columns that are not predictive features.
    
    Dropped columns:
    - batch: Batch sequence number (identifier, not a feature)
    - api_code: API supplier code (lot tracking, not predictive)
    - api_batch: API lot number (lot tracking)
    - smcc_batch: SMCC lot number (lot tracking)
    - lactose_batch: Lactose lot number (lot tracking)
    - starch_batch: Starch lot number (lot tracking)
    - start: Production start date (temporal identifier)
    - strength: Dosage strength (redundant with code)
    - size: Batch size in tablets (redundant with code, but preserved for feature engineering)
    
    Args:
        df: Merged DataFrame
    
    Returns:
        pd.DataFrame: DataFrame without identifier columns
    """
    # Columns to drop (identifiers and lot tracking)
    id_cols = ['api_code', 'api_batch', 'smcc_batch', 'lactose_batch', 
               'starch_batch', 'start', 'strength']
    
    cols_to_drop = [c for c in id_cols if c in df.columns]
    df_clean = df.drop(columns=cols_to_drop)
    
    print(f"[Data Pipeline] Dropped {len(cols_to_drop)} identifier columns: {cols_to_drop}")
    print(f"[Data Pipeline] Remaining: {df_clean.shape[1]} columns")
    
    return df_clean


def impute_missing_values(df):
    """
    Impute remaining missing values:
    - First, ensure all non-string columns are cast to float
    - Numeric columns: median imputation per product code group
    - If group median is NaN, use overall median
    
    Args:
        df: DataFrame with potential missing values
    
    Returns:
        pd.DataFrame: DataFrame with missing values imputed
    """
    df_imputed = df.copy()
    
    # Non-numeric columns to exclude from forced numeric conversion
    string_cols = ['batch', 'start', 'strength', 'weekend', 'code']
    
    for col in df_imputed.columns:
        if col not in string_cols and df_imputed[col].dtype == 'object':
            df_imputed[col] = pd.to_numeric(
                df_imputed[col].astype(str).str.strip().str.replace(',', '.'),
                errors='coerce'
            )
            
    numeric_cols = df_imputed.select_dtypes(include=[np.number]).columns.tolist()
    
    total_imputed = 0
    for col in numeric_cols:
        if df_imputed[col].isnull().any():
            n_missing = df_imputed[col].isnull().sum()
            # Try group median first
            if 'code' in df_imputed.columns:
                df_imputed[col] = df_imputed.groupby('code')[col].transform(
                    lambda x: x.fillna(x.median())
                )
            # Fill any remaining with overall median
            if df_imputed[col].isnull().any():
                df_imputed[col].fillna(df_imputed[col].median(), inplace=True)
            total_imputed += n_missing
    
    print(f"[Data Pipeline] Imputed {total_imputed} missing values across numeric columns")
    
    return df_imputed


def drop_rows_missing_cqa(df):
    """
    Drop rows where ALL Critical Quality Attribute columns are missing.
    These batches (typically the last ~18) have no lab results and cannot be labeled.
    
    CQA columns: dissolution_av, dissolution_min, residual_solvent, 
                 impurities_total, impurity_o, impurity_l
    
    Args:
        df: DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with CQA-missing rows removed
    """
    cqa_cols = ['dissolution_av', 'dissolution_min', 'residual_solvent',
                'impurities_total', 'impurity_o', 'impurity_l']
    
    existing_cqa = [c for c in cqa_cols if c in df.columns]
    
    if existing_cqa:
        # Drop rows where ALL CQA columns are NaN
        all_cqa_missing = df[existing_cqa].isnull().all(axis=1)
        n_dropped = all_cqa_missing.sum()
        df_clean = df[~all_cqa_missing].copy()
        print(f"[Data Pipeline] Dropped {n_dropped} rows with all CQA values missing")
    else:
        df_clean = df.copy()
        print("[Data Pipeline] Warning: No CQA columns found")
    
    return df_clean


def load_and_clean():
    """
    Complete data pipeline: Load -> Clean -> Merge -> Drop identifiers -> Impute -> Save.
    
    Returns:
        pd.DataFrame: Fully cleaned and merged dataset ready for feature engineering
    """
    print("=" * 70)
    print("PHARMACEUTICAL DATA PIPELINE")
    print("=" * 70)
    
    # Step 1: Load raw data
    lab_df, process_df = load_raw_data()
    
    # Step 2: Clean individual datasets
    lab_clean = clean_laboratory_data(lab_df)
    process_clean = clean_process_data(process_df)
    
    # Step 3: Merge datasets
    merged = merge_datasets(lab_clean, process_clean)
    
    # Step 4: Drop rows with all CQAs missing (cannot be labeled)
    merged = drop_rows_missing_cqa(merged)
    
    # Step 5: Drop identifier columns
    merged = drop_identifiers(merged)
    
    # Step 6: Impute remaining missing values
    merged = impute_missing_values(merged)
    
    # Step 7: Save processed dataset
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DATA_DIR, 'merged_dataset.csv')
    merged.to_csv(output_path, index=False)
    print(f"\n[Data Pipeline] Saved merged dataset to {output_path}")
    print(f"[Data Pipeline] Final shape: {merged.shape[0]} rows × {merged.shape[1]} columns")
    print("=" * 70)
    
    return merged


if __name__ == '__main__':
    df = load_and_clean()
    print("\nColumn dtypes:")
    print(df.dtypes)
    print(f"\nDataset head:\n{df.head()}")
