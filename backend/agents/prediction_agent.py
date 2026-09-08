"""
Prediction Agent
================
Agent 2 of 5 in the Agentic AI Pipeline.

Loads saved trained ML model, scaler, and label encoder to predict
batch quality outcome (Approved / Rework / Rejected) with class probabilities.
"""

import os
import joblib
import numpy as np
import pandas as pd
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import BEST_MODEL_PATH, SCALER_PATH, LABEL_ENCODER_PATH, FEATURE_NAMES_PATH
from backend.ml.feature_engineering import engineer_single_input


class PredictionAgent:
    """Agent responsible for running model inference and extracting probabilities."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None
        self.load_artifacts()

    def load_artifacts(self):
        """Load trained model artifacts if present."""
        try:
            if os.path.exists(BEST_MODEL_PATH):
                self.model = joblib.load(BEST_MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
                self.feature_names = joblib.load(FEATURE_NAMES_PATH)
                print("[Prediction Agent] Loaded model and scaler successfully.")
            else:
                print("[Prediction Agent] Warning: Model artifacts not found. Train model first.")
        except Exception as e:
            print(f"[Prediction Agent] Error loading artifacts: {e}")

    def predict(self, input_dict: dict) -> dict:
        """
        Predict quality outcome for a single batch input.
        
        Args:
            input_dict: Dictionary of feature values
            
        Returns:
            dict: {prediction: str, confidence: float, confidence_scores: dict}
        """
        if self.model is None:
            self.load_artifacts()
            if self.model is None:
                raise RuntimeError("ML Model artifacts are missing. Run train_model.py first.")

        # 1. Apply feature engineering
        augmented = engineer_single_input(input_dict)

        # 2. Build feature vector in exact order expected by scaler/model
        feature_vector = []
        for feat in self.feature_names:
            val = augmented.get(feat, 0.0)
            try:
                feature_vector.append(float(val) if val is not None else 0.0)
            except (ValueError, TypeError):
                feature_vector.append(0.0)

        X_input = np.array(feature_vector).reshape(1, -1)

        # 3. Scale features
        X_scaled = self.scaler.transform(X_input)

        # 4. Model inference
        pred_idx = self.model.predict(X_scaled)[0]
        probs = self.model.predict_proba(X_scaled)[0]

        prediction_label = str(self.label_encoder.inverse_transform([pred_idx])[0])
        confidence = float(np.max(probs))

        classes = [str(c) for c in self.label_encoder.classes_]
        confidence_scores = {cls: float(prob) for cls, prob in zip(classes, probs)}

        return {
            'prediction': prediction_label,
            'confidence': confidence,
            'confidence_scores': confidence_scores,
            'feature_vector': X_scaled[0]
        }
