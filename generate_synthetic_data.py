"""
Realistic Synthetic Pharmaceutical Batch Data Generator (55-Column Schema)
===========================================================================
Generates 10 CSV files (Day_01.csv ... Day_10.csv) with 10 batches each (100 total batches).
Uses the full 55-column schema from Laboratory.csv to guarantee that model predictions
accurately produce a mixed, realistic distribution of Approved, Rework, and Rejected batches.

Output:
  x:/manufactoring/synthetic_batch_test_data/Day_01.csv ... Day_10.csv
"""

import csv, os, sys, random, joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.agents.cleaning_agent import CleaningAgent
from backend.ml.feature_engineering import engineer_single_input

# ─── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "synthetic_batch_test_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Load Model & Real Dataset ─────────────────────────────────────────────
model         = joblib.load(os.path.join(MODELS_DIR, 'best_model.joblib'))
scaler        = joblib.load(os.path.join(MODELS_DIR, 'scaler.joblib'))
label_encoder = joblib.load(os.path.join(MODELS_DIR, 'label_encoder.joblib'))
feature_names = joblib.load(os.path.join(MODELS_DIR, 'feature_names.joblib'))
cleaner       = CleaningAgent()

lab_df = pd.read_csv(os.path.join(BASE_DIR, 'figshare_dataset', 'Laboratory.csv'), sep=';')

# Convert string numbers with commas to numeric floats
for col in lab_df.columns:
    try:
        lab_df[col] = pd.to_numeric(lab_df[col].astype(str).str.replace(',', '.'), errors='coerce')
    except:
        pass

def predict_row(d):
    cl = cleaner.clean([d])['cleaned_rows'][0]
    aug = engineer_single_input(cl)
    fv = [float(aug.get(f, 0.0) or 0.0) for f in feature_names]
    X_sc = scaler.transform([fv])
    idx = model.predict(X_sc)[0]
    probs = model.predict_proba(X_sc)[0]
    label = str(label_encoder.inverse_transform([idx])[0])
    conf = float(np.max(probs))
    return label, conf

# Classify all rows in Laboratory.csv
approved_pools = []
rework_pools   = []
rejected_pools = []

print("Categorising real dataset profiles...")
for i, row in lab_df.iterrows():
    d = row.to_dict()
    label, conf = predict_row(d)
    if label == 'Approved':
        approved_pools.append(d)
    elif label == 'Rework':
        rework_pools.append(d)
    elif label == 'Rejected':
        rejected_pools.append(d)

print("Found real baseline profiles:")
print("  Approved : %d profiles" % len(approved_pools))
print("  Rework   : %d profiles" % len(rework_pools))
print("  Rejected : %d profiles" % len(rejected_pools))
print()

# Full 55-column list matching Laboratory.csv (replacing 'batch' with 'batch_id')
HEADER = ['batch_id'] + [c for c in lab_df.columns if c != 'batch']

def mutate_row(base_dict, target_class):
    """Slightly perturb numeric values while preserving the target prediction class."""
    for attempt in range(25):
        d = dict(base_dict)
        for k, v in d.items():
            if k in ('batch', 'batch_id', 'code', 'strength', 'size', 'start', 'api_code'):
                continue
            if isinstance(v, (int, float)) and not np.isnan(v):
                factor = 1.0 + random.uniform(-0.015, 0.015)
                d[k] = round(float(v) * factor, 3)
        
        pred, conf = predict_row(d)
        if pred == target_class:
            return d
    return base_dict

# 10-Day Production Schedule (Varied & Mixed per day for demo)
DAY_SCHEDULE = [
    {'Approved': 7, 'Rework': 2, 'Rejected': 1},  # Day 1: Normal operational mix
    {'Approved': 8, 'Rework': 1, 'Rejected': 1},  # Day 2: High quality day
    {'Approved': 4, 'Rework': 4, 'Rejected': 2},  # Day 3: Process deviation day
    {'Approved': 6, 'Rework': 3, 'Rejected': 1},  # Day 4: Standard day
    {'Approved': 3, 'Rework': 3, 'Rejected': 4},  # Day 5: Critical quality issues
    {'Approved': 7, 'Rework': 2, 'Rejected': 1},  # Day 6: Post-maintenance day
    {'Approved': 5, 'Rework': 3, 'Rejected': 2},  # Day 7: Weekend shift
    {'Approved': 8, 'Rework': 2, 'Rejected': 0},  # Day 8: Smooth run
    {'Approved': 6, 'Rework': 2, 'Rejected': 2},  # Day 9: Mixed quality
    {'Approved': 9, 'Rework': 1, 'Rejected': 0},  # Day 10: Excellent final run
]

pool_map = {
    'Approved': approved_pools,
    'Rework': rework_pools,
    'Rejected': rejected_pools
}

print("Generating 10 CSV files for 10-day pharmaceutical manufacturing validation...")
print()

grand_counts = {'Approved': 0, 'Rework': 0, 'Rejected': 0}

for day_idx, schedule in enumerate(DAY_SCHEDULE):
    day_num = day_idx + 1

    target_labels = []
    for label, count in schedule.items():
        target_labels.extend([label] * count)
    random.shuffle(target_labels)

    rows = []
    actual_preds = []

    for batch_idx, target_class in enumerate(target_labels, start=1):
        batch_id = "B%02d%02d" % (day_num, batch_idx)
        pool = pool_map[target_class]
        base_dict = random.choice(pool)
        
        mutated = mutate_row(base_dict, target_class)
        mutated['batch_id'] = batch_id

        # Format values cleanly for CSV
        row_values = []
        for col in HEADER:
            v = mutated.get(col, '')
            if pd.isna(v) or v is None:
                v = ''
            elif isinstance(v, float):
                v = round(v, 4)
            row_values.append(v)
        
        rows.append(row_values)

        pred, _ = predict_row(mutated)
        actual_preds.append(pred)
        grand_counts[pred] = grand_counts.get(pred, 0) + 1

    file_path = os.path.join(OUTPUT_DIR, "Day_%02d.csv" % day_num)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    c = {cls: actual_preds.count(cls) for cls in ['Approved', 'Rework', 'Rejected']}
    print("  [OK] Day %02d written (%d batches) -> Approved: %d | Rework: %d | Rejected: %d" % (
        day_num, len(rows), c['Approved'], c['Rework'], c['Rejected']
    ))

print()
print("==================================================")
print("TOTAL GENERATED BATCHES (100 total across 10 days):")
print("  Approved : %d batches" % grand_counts['Approved'])
print("  Rework   : %d batches" % grand_counts['Rework'])
print("  Rejected : %d batches" % grand_counts['Rejected'])
print("==================================================")
print("Output directory: %s" % OUTPUT_DIR)
