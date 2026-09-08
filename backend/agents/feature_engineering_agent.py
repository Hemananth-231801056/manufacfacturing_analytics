"""
Feature Engineering Agent
==========================
Agent 5 of 9 in the Agentic AI Pipeline.

Creates 7 pharma-domain composite features then aligns the row to
the exact ordered feature list expected by the trained scaler/model.
"""

import numpy as np
from typing import List, Dict, Any
import joblib, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, 'models', 'feature_names.joblib')


class FeatureEngineeringAgent:
    """Agent that adds derived features and aligns columns to model schema."""

    def __init__(self):
        try:
            self.feature_names: List[str] = joblib.load(FEATURE_NAMES_PATH)
        except Exception:
            self.feature_names = []

    def engineer(self, row: dict) -> Dict[str, Any]:
        """
        Engineer derived features for a single cleaned batch dict.

        Returns:
            dict: Row extended with engineered features
        """
        row = dict(row)  # copy

        def safe(key, default=0.0):
            try:
                v = row.get(key)
                return float(v) if v is not None else default
            except (TypeError, ValueError):
                return default

        # 1. API particle size span
        ps01 = safe('api_ps01', 1.3)
        ps05 = safe('api_ps05', 18.5)
        ps09 = safe('api_ps09', 110.0)
        row['api_particle_span'] = (ps09 - ps01) / ps05 if ps05 != 0 else 0.0

        # 2. SMCC Carr's Compressibility Index
        td = safe('smcc_td', 0.45)
        bd = safe('smcc_bd', 0.33)
        row['smcc_compressibility'] = ((td - bd) / td * 100) if td != 0 else 0.0

        # 3. Tablet hardness range
        row['hardness_range'] = safe('tbl_max_hardness', 70.0) - safe('tbl_min_hardness', 55.0)

        # 4. Thickness uniformity
        row['thickness_uniformity'] = safe('tbl_max_thickness', 3.45) - safe('tbl_min_thickness', 3.3)

        # 5. Compression force CV (%)
        cf_mean = safe('main_CompForce_mean', 4.3)
        cf_sd   = safe('main_CompForce_sd', 0.06)
        row['compression_variability'] = (cf_sd / cf_mean * 100) if cf_mean != 0 else 0.0

        # 6. Coating impact ratio
        fct_h = safe('fct_av_hardness', 63.0)
        tbl_h = safe('tbl_av_hardness', 46.0)
        row['coating_impact'] = (fct_h - tbl_h) / tbl_h if tbl_h != 0 else 0.0

        # 7. Waste ratio (waste / yield)
        waste = safe('total_waste', 1000.0)
        yield_ = safe('batch_yield', 95.5)
        row['waste_ratio'] = waste / yield_ if yield_ != 0 else 0.0

        return row

    def engineer_all(self, rows: List[dict]) -> List[dict]:
        return [self.engineer(r) for r in rows]

    def to_feature_vector(self, row: dict) -> List[float]:
        """
        Convert a row dict to an ordered feature vector aligned to model schema.
        Missing features default to 0.0.
        """
        if not self.feature_names:
            self.feature_names = joblib.load(FEATURE_NAMES_PATH)
        vector = []
        for feat in self.feature_names:
            val = row.get(feat, 0.0)
            try:
                vector.append(float(val) if val is not None else 0.0)
            except (TypeError, ValueError):
                vector.append(0.0)
        return vector
