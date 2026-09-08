"""
Data Validation Agent
=====================
Agent 3 of 9 in the Agentic AI Pipeline.

Validates extracted batch records:
- Standardizes column aliases prior to validation
- Checks for required columns presence
- Validates data types and numeric ranges
- Reports field-level validation errors per batch
- Does NOT crash — always returns a structured validation report
"""

import re
from typing import List, Dict, Any

# Map common aliases to standard feature names for validation check
COLUMN_ALIASES = {
    'product_code':             'code',
    'product':                  'code',
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
    'ejection_force':           'ejection_mean',
    'ejection_force_n':         'ejection_mean',
    'ejection':                 'ejection_mean',
    'tensile':                  'tbl_tensile',
    'tensile_strength':         'tbl_tensile',
    'tensile_strength_mpa':     'tbl_tensile',
    'weekend_shift':            'weekend',
    'shift':                    'weekend',
    'api_particle_size_microns':'api_ps05',
    'api_particle_size_d50':    'api_ps05',
    'excipient_moisture_percent':'smcc_water',
}

# Columns expected in a valid batch record with their (min, max, required)
SCHEMA = {
    'code':                     (1,     999,   True),
    'main_CompForce_mean':       (0.1,   50.0,  False),
    'tbl_fill_mean':             (1.0,   25.0,  False),
    'tbl_speed_mean':            (10.0,  300.0, False),
    'batch_yield':               (10.0,  105.0, False),
    'api_water':                 (0.0,   20.0,  False),
    'api_content':               (10.0,  110.0, False),
    'api_total_impurities':      (0.0,   25.0,  False),
    'tbl_av_hardness':           (1.0,   350.0, False),
    'ejection_mean':             (10.0,  2000.0,False),
    'weekend':                   (0,     1,     False),
}


class ValidationAgent:
    """Agent that validates extracted batch records field-by-field."""

    def _normalize_row_keys(self, row: dict) -> dict:
        """Helper to resolve column aliases before checking schema."""
        norm_row = {}
        for col, val in row.items():
            s = str(col).strip().lower()
            s = re.sub(r'[\s\-/\\]+', '_', s)
            s = re.sub(r'[^a-z0-9_]', '', s)
            mapped = COLUMN_ALIASES.get(s, col)
            norm_row[mapped] = val
        return norm_row

    def validate_batch(self, raw_row: dict) -> Dict[str, Any]:
        """
        Validate a single batch row dictionary.
        """
        errors = []
        warnings = []
        
        row = self._normalize_row_keys(raw_row)

        # Check for required columns
        for col, (lo, hi, required) in SCHEMA.items():
            if required and col not in row:
                errors.append(f"Missing required column: '{col}'")

        # Check numeric ranges for columns that are present
        for col, (lo, hi, _) in SCHEMA.items():
            if col in row and row[col] is not None:
                try:
                    val = float(row[col])
                    if not (lo <= val <= hi):
                        warnings.append(
                            f"'{col}' = {val} is outside expected range [{lo}, {hi}]"
                        )
                except (TypeError, ValueError):
                    errors.append(f"'{col}' has non-numeric value: '{row[col]}'")

        # weekend must be 0 or 1 if present
        if 'weekend' in row and row['weekend'] is not None:
            try:
                w = int(float(row['weekend']))
                if w not in (0, 1):
                    errors.append(f"'weekend' must be 0 or 1, got {w}")
            except (TypeError, ValueError):
                val = str(row['weekend']).lower()
                if val in ('yes', 'true', '1'):
                    row['weekend'] = 1
                elif val in ('no', 'false', '0'):
                    row['weekend'] = 0
                else:
                    errors.append(f"'weekend' has unrecognised value: '{row['weekend']}'")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def validate_all(self, rows: List[dict]) -> List[Dict[str, Any]]:
        if not rows:
            return [{
                "is_valid": False,
                "errors": ["No batch records were extracted from the uploaded file."],
                "warnings": []
            }]
        return [self.validate_batch(row) for row in rows]

    def validate(self, batch_dict: dict) -> tuple:
        result = self.validate_batch(batch_dict)
        return result["is_valid"], result["errors"]
