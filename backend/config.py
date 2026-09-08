"""
Application Configuration
==========================
Central configuration for paths, database URL, and CORS settings.
"""

import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data paths
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
LABELED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'labeled')

# Model paths
MODELS_DIR = os.path.join(BASE_DIR, 'models')
BEST_MODEL_PATH = os.path.join(MODELS_DIR, 'best_model.joblib')
SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.joblib')
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.joblib')
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, 'feature_names.joblib')
MODEL_COMPARISON_PATH = os.path.join(MODELS_DIR, 'model_comparison.json')

# Reports
REPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'generated')
PLOTS_DIR = os.path.join(BASE_DIR, 'notebooks', 'eda_plots')

# Database
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'pharma_qc2.db')}"

# CORS
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Ensure directories exist
for d in [REPORTS_DIR, PLOTS_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)
