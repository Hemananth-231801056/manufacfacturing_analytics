"""
Model Training Module
======================
Trains Random Forest and XGBoost classifiers on pharmaceutical batch data
to predict quality outcomes (Approved / Rework / Rejected).

Methodology:
- 80/20 stratified train/test split
- StandardScaler fitted on training data only
- 5-fold Stratified K-Fold cross-validation
- Hyperparameter tuning via RandomizedSearchCV
- Class imbalance handled via class_weight='balanced'
- Best model saved for deployment

Evaluation Metrics:
- Accuracy, Precision, Recall, F1 (macro + weighted)
- ROC-AUC (One-vs-Rest)
- Confusion Matrix
"""

import pandas as pd
import numpy as np
import json
import os
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
from imblearn.over_sampling import SMOTE

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("[Training] Warning: XGBoost not installed. Using only Random Forest.")


# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')


def evaluate_model(model, X_test, y_test, label_encoder, model_name="Model"):
    """
    Comprehensive model evaluation with multiple metrics.
    
    Args:
        model: Trained classifier
        X_test: Test features (scaled)
        y_test: True labels (encoded)
        label_encoder: LabelEncoder for class name mapping
        model_name: Name for display
    
    Returns:
        dict: Dictionary of evaluation metrics
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Decode labels for display
    class_names = label_encoder.classes_
    
    # Core metrics
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    prec_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    rec_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC (One-vs-Rest)
    try:
        roc_auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
    except Exception:
        roc_auc = None
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Classification Report
    report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
    
    print(f"\n{'='*60}")
    print(f"  {model_name} — Evaluation Results")
    print(f"{'='*60}")
    print(f"  Accuracy:           {acc:.4f}")
    print(f"  Precision (macro):  {prec_macro:.4f}")
    print(f"  Precision (wt):     {prec_weighted:.4f}")
    print(f"  Recall (macro):     {rec_macro:.4f}")
    print(f"  Recall (wt):        {rec_weighted:.4f}")
    print(f"  F1 Score (macro):   {f1_macro:.4f}")
    print(f"  F1 Score (wt):      {f1_weighted:.4f}")
    if roc_auc is not None:
        print(f"  ROC-AUC (wt, OVR):  {roc_auc:.4f}")
    print(f"\n  Confusion Matrix:")
    print(f"  Classes: {list(class_names)}")
    for i, row in enumerate(cm):
        print(f"    {class_names[i]:>10}: {row}")
    print(f"\n  Classification Report:\n{report}")
    
    metrics = {
        'model_name': model_name,
        'accuracy': float(acc),
        'precision_macro': float(prec_macro),
        'precision_weighted': float(prec_weighted),
        'recall_macro': float(rec_macro),
        'recall_weighted': float(rec_weighted),
        'f1_macro': float(f1_macro),
        'f1_weighted': float(f1_weighted),
        'roc_auc_weighted': float(roc_auc) if roc_auc is not None else None,
        'confusion_matrix': cm.tolist(),
        'class_names': list(class_names)
    }
    
    return metrics


def train_models(X, y):
    """
    Train Random Forest and XGBoost models with hyperparameter tuning.
    
    Pipeline:
    1. Encode labels
    2. Stratified train/test split (80/20)
    3. Scale features (StandardScaler on training data only)
    4. Train both models with RandomizedSearchCV
    5. Evaluate and compare
    6. Save best model and artifacts
    
    Args:
        X: Feature DataFrame
        y: Target Series (quality labels)
    
    Returns:
        dict: Training results including best model info and metrics
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("MODEL TRAINING PIPELINE")
    print("=" * 70)
    
    # ---- Step 1: Encode Labels ----
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"\nLabel encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    
    # ---- Step 2: Train/Test Split ----
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"Train set (before SMOTE): {X_train.shape[0]} samples")
    print(f"Test set:  {X_test.shape[0]} samples")
    
    # ---- Step 2.5: Handle Class Imbalance via SMOTE ----
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)
    print(f"Train set (after SMOTE): {X_train.shape[0]} samples")
    print(f"SMOTE class distribution: {np.bincount(y_train)}")
    
    # ---- Step 3: Feature Scaling ----
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save feature names
    feature_names = list(X.columns)
    
    # ---- Step 4: Train Random Forest ----
    print("\n" + "-" * 50)
    print("Training Random Forest...")
    print("-" * 50)
    
    rf_param_dist = {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [5, 10, 15, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2'],
        'class_weight': ['balanced']
    }
    
    rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)
    rf_search = RandomizedSearchCV(
        rf_base, rf_param_dist, n_iter=30, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='f1_weighted', random_state=42, n_jobs=-1, verbose=0
    )
    rf_search.fit(X_train_scaled, y_train)
    rf_model = rf_search.best_estimator_
    
    print(f"Best RF params: {rf_search.best_params_}")
    rf_cv_score = rf_search.best_score_
    print(f"RF CV F1 (weighted): {rf_cv_score:.4f}")
    
    rf_metrics = evaluate_model(rf_model, X_test_scaled, y_test, le, "Random Forest")
    rf_metrics['cv_f1_weighted'] = float(rf_cv_score)
    
    # ---- Step 5: Train XGBoost ----
    xgb_metrics = None
    xgb_model = None
    
    if HAS_XGBOOST:
        print("\n" + "-" * 50)
        print("Training XGBoost...")
        print("-" * 50)
        
        # Compute sample weights for class imbalance
        n_classes = len(le.classes_)
        class_counts = np.bincount(y_train)
        total = len(y_train)
        
        xgb_param_dist = {
            'n_estimators': [100, 200, 300, 500],
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.7, 0.8, 0.9, 1.0],
            'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
            'min_child_weight': [1, 3, 5],
            'gamma': [0, 0.1, 0.2]
        }
        
        # Compute scale_pos_weight equivalent for multiclass
        sample_weights = np.array([total / (n_classes * class_counts[c]) for c in y_train])
        
        xgb_base = XGBClassifier(
            random_state=42, use_label_encoder=False,
            eval_metric='mlogloss', n_jobs=-1, verbosity=0
        )
        
        xgb_search = RandomizedSearchCV(
            xgb_base, xgb_param_dist, n_iter=30,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring='f1_weighted', random_state=42, n_jobs=-1, verbose=0
        )
        xgb_search.fit(X_train_scaled, y_train, sample_weight=sample_weights)
        xgb_model = xgb_search.best_estimator_
        
        print(f"Best XGB params: {xgb_search.best_params_}")
        xgb_cv_score = xgb_search.best_score_
        print(f"XGB CV F1 (weighted): {xgb_cv_score:.4f}")
        
        xgb_metrics = evaluate_model(xgb_model, X_test_scaled, y_test, le, "XGBoost")
        xgb_metrics['cv_f1_weighted'] = float(xgb_cv_score)
    
    # ---- Step 6: Compare and Select Best ----
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    
    comparison = {'random_forest': rf_metrics}
    if xgb_metrics:
        comparison['xgboost'] = xgb_metrics
    
    # Select best model based on weighted F1
    best_model = rf_model
    best_name = "Random Forest"
    best_f1 = rf_metrics['f1_weighted']
    
    if xgb_metrics and xgb_metrics['f1_weighted'] > rf_metrics['f1_weighted']:
        best_model = xgb_model
        best_name = "XGBoost"
        best_f1 = xgb_metrics['f1_weighted']
    
    print(f"\n  Best Model: {best_name}")
    print(f"  Best F1 (weighted): {best_f1:.4f}")
    
    # ---- Step 7: Save Artifacts ----
    print("\n" + "-" * 50)
    print("Saving model artifacts...")
    print("-" * 50)
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'best_model.joblib'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.joblib'))
    joblib.dump(le, os.path.join(MODELS_DIR, 'label_encoder.joblib'))
    joblib.dump(feature_names, os.path.join(MODELS_DIR, 'feature_names.joblib'))
    
    # Save comparison metrics
    comparison['best_model'] = best_name
    comparison['best_f1_weighted'] = float(best_f1)
    comparison['training_samples'] = int(X_train.shape[0])
    comparison['test_samples'] = int(X_test.shape[0])
    comparison['n_features'] = int(X.shape[1])
    comparison['feature_names'] = feature_names
    comparison['class_distribution'] = {
        str(label): int(count) 
        for label, count in zip(le.classes_, np.bincount(y_encoded))
    }
    
    with open(os.path.join(MODELS_DIR, 'model_comparison.json'), 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"  Saved: best_model.joblib ({best_name})")
    print(f"  Saved: scaler.joblib")
    print(f"  Saved: label_encoder.joblib")
    print(f"  Saved: feature_names.joblib")
    print(f"  Saved: model_comparison.json")
    print("=" * 70)
    
    return comparison


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.ml.data_pipeline import load_and_clean
    from backend.ml.feature_engineering import engineer_features
    from backend.ml.labeling import create_labels, get_features_and_target
    
    df = load_and_clean()
    df = engineer_features(df)
    df = create_labels(df)
    X, y = get_features_and_target(df)
    results = train_models(X, y)
