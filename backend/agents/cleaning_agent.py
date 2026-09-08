"""
Cleaning Agent
==============
Agent 4 of 9 in the Agentic AI Pipeline.

Applies column standardization, duplicate removal, data-type fixing,
and group-median imputation for missing numeric values.
"""

import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any


# Map common aliases/synonyms to standard feature column names
COLUMN_ALIASES = {
    'purity':                   'api_content',
    'api_purity':               'api_content',
    'impurities':               'api_total_impurities',
    'api_impurities':           'api_total_impurities',
    'api_impurities_percent':   'api_total_impurities',
    'water':                    'api_water',
    'moisture':                 'api_water',
    'api_water_content_percent':'api_water',
    'compression_force':        'main_CompForce_mean',
    'compression_force_kn':     'main_CompForce_mean',
    'comp_force':               'main_CompForce_mean',
    'average_hardness':         'tbl_av_hardness',
    'hardness':                 'tbl_av_hardness',
    'avg_hardness':             'tbl_av_hardness',
    'tablet_hardness_kp':       'tbl_av_hardness',
    'fill_depth':               'tbl_fill_mean',
    'fill_depth_mm':            'tbl_fill_mean',
    'fill':                     'tbl_fill_mean',
    'speed':                    'tbl_speed_mean',
    'turret_speed':             'tbl_speed_mean',
    'turret_speed_rpm':         'tbl_speed_mean',
    'tablet_speed':             'tbl_speed_mean',
    'yield':                    'batch_yield',
    'batch_yield_pct':          'batch_yield',
    'waste':                    'total_waste',
    'waste_percentage':         'total_waste',
    'product_code':             'code',
    'product':                  'code',
    'ejection_force':           'ejection_mean',
    'ejection_force_n':         'ejection_mean',
    'ejection':                 'ejection_mean',
    'tensile':                  'tbl_tensile',
    'tensile_strength':         'tbl_tensile',
    'tensile_strength_mpa':     'tbl_tensile',
    'min_thickness':            'tbl_min_thickness',
    'max_thickness':            'tbl_max_thickness',
    'tablet_thickness_mm':      'tbl_min_thickness',
    'min_hardness':             'tbl_min_hardness',
    'max_hardness':             'tbl_max_hardness',
    'min_weight':               'tbl_min_weight',
    'max_weight':               'tbl_max_weight',
    'tablet_weight_mg':         'tbl_min_weight',
    'coating_thickness':        'coating_impact',
    'coating_thickness_microns':'coating_impact',
    'rsd_weight':               'tbl_rsd_weight',
    'compression_force_sd':     'main_CompForce_sd',
    'comp_force_sd':            'main_CompForce_sd',
    'stiffness':                'stiffness_mean',
    'pre_compression':          'pre_CompForce_mean',
    'pre_comp_force':           'pre_CompForce_mean',
    'weekend_shift':            'weekend',
    'shift':                    'weekend',
    'api_particle_size_microns':'api_ps05',
    'api_particle_size_d50':    'api_ps05',
    'api_particle_size_d10':    'api_ps01',
    'api_particle_size_d90':    'api_ps09',
    'particle_size':            'api_ps05',
    'excipient_moisture_percent':'smcc_water',
    'lactose_moisture':         'lactose_water',
    'smcc_moisture':            'smcc_water',
}

# Default median fill values derived from the training dataset
GLOBAL_MEDIANS = {
    'code': 13,
    'api_water': 1.5, 'api_total_impurities': 0.25, 'api_l_impurity': 0.13,
    'api_content': 94.8, 'api_ps01': 1.3, 'api_ps05': 18.5, 'api_ps09': 110.0,
    'lactose_water': 0.05, 'lactose_sieve0045': 12.0, 'lactose_sieve015': 40.0,
    'lactose_sieve025': 70.0, 'smcc_water': 4.0, 'smcc_td': 0.45, 'smcc_bd': 0.33,
    'smcc_ps01': 30.0, 'smcc_ps05': 100.0, 'smcc_ps09': 250.0, 'starch_ph': 4.5,
    'starch_water': 3.0, 'tbl_min_thickness': 3.3, 'tbl_max_thickness': 3.45,
    'fct_min_thickness': 3.45, 'fct_max_thickness': 3.58, 'tbl_min_weight': 112.0,
    'tbl_max_weight': 115.0, 'tbl_rsd_weight': 0.85, 'fct_rsd_weight': 0.8,
    'tbl_min_hardness': 55.0, 'tbl_max_hardness': 70.0, 'tbl_av_hardness': 46.0,
    'fct_min_hardness': 38.0, 'fct_max_hardness': 56.0, 'fct_av_hardness': 63.0,
    'tbl_max_diameter': 6.1, 'fct_max_diameter': 6.1, 'tbl_tensile': 1.4,
    'fct_tensile': 1.9, 'tbl_yield': 97.0, 'batch_yield': 95.5,
    'tbl_speed_mean': 100.0, 'tbl_speed_change': 3.0, 'tbl_speed_0_duration': 90.0,
    'total_waste': 1000.0, 'startup_waste': 1500.0, 'weekend': 0, 'fom_mean': 50.0,
    'fom_change': 8.0, 'SREL_startup_mean': 5.0, 'SREL_production_mean': 3.5,
    'SREL_production_max': 8.0, 'main_CompForce_mean': 4.3, 'main_CompForce_sd': 0.06,
    'main_CompForce_median': 4.3, 'pre_CompForce_mean': 0.1, 'tbl_fill_mean': 5.3,
    'tbl_fill_sd': 0.1, 'cyl_height_mean': 2.1, 'stiffness_mean': 90.0,
    'stiffness_max': 110.0, 'stiffness_min': 70.0, 'ejection_mean': 220.0,
    'ejection_max': 250.0, 'ejection_min': 190.0, 'Startup_tbl_fill_maxDifference': 0.2,
    'Startup_main_CompForce_mean': 4.5, 'Startup_tbl_fill_mean': 5.3,
}


class CleaningAgent:
    """Agent that standardizes, deduplicates, and imputes uploaded batch data."""

    def clean(self, rows: List[dict]) -> Dict[str, Any]:
        if not rows:
            return {"cleaned_rows": [], "log": ["No rows to clean."], "column_map": {}}

        df = pd.DataFrame(rows)
        log = []
        col_map = {}

        # 1. Normalise column names
        new_cols = {}
        for col in df.columns:
            normalised = self._normalise_col(col)
            mapped = COLUMN_ALIASES.get(normalised, normalised)
            new_cols[col] = mapped
            if col != mapped:
                col_map[col] = mapped
        df.rename(columns=new_cols, inplace=True)
        if col_map:
            log.append(f"Column aliases resolved: {col_map}")

        # 2. Remove full duplicates
        before = len(df)
        df.drop_duplicates(inplace=True)
        removed = before - len(df)
        if removed:
            log.append(f"Removed {removed} duplicate row(s).")

        # 3. Force numeric types
        non_numeric = {'batch_id', 'batch', 'code', 'date', 'quality_label'}
        for col in df.columns:
            if col in non_numeric:
                continue
            df[col] = pd.to_numeric(
                df[col].astype(str).str.strip().str.replace(',', '.'),
                errors='coerce'
            )

        # 4. Impute missing values
        imputed_cols = []
        for col, default in GLOBAL_MEDIANS.items():
            if col in df.columns:
                n_missing = df[col].isnull().sum()
                if n_missing > 0:
                    df[col].fillna(default, inplace=True)
                    imputed_cols.append(f"{col} ({n_missing} value(s))")
        # For columns NOT in GLOBAL_MEDIANS, use column median
        for col in df.select_dtypes(include=[np.number]).columns:
            n_missing = df[col].isnull().sum()
            if n_missing > 0:
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                imputed_cols.append(f"{col} ({n_missing} value(s)) [col median]")
        if imputed_cols:
            log.append(f"Imputed missing values: {', '.join(imputed_cols)}")

        # 5. Generate a batch_id if missing
        if 'batch_id' not in df.columns:
            df['batch_id'] = [f"BATCH-{str(i+1).zfill(3)}" for i in range(len(df))]
            log.append("Auto-generated batch_id column.")
        else:
            df['batch_id'] = df['batch_id'].fillna(
                pd.Series([f"BATCH-{str(i+1).zfill(3)}" for i in range(len(df))])
            )

        log.append(f"Cleaning complete: {len(df)} batch record(s) ready for prediction.")

        cleaned_rows = df.where(pd.notnull(df), None).to_dict(orient='records')
        return {
            "cleaned_rows": cleaned_rows,
            "log": log,
            "column_map": col_map
        }

    def _normalise_col(self, name: str) -> str:
        s = str(name).strip().lower()
        s = re.sub(r'[\s\-/\\]+', '_', s)
        s = re.sub(r'[^a-z0-9_]', '', s)
        return s
