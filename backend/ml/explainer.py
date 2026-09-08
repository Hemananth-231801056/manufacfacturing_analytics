"""
SHAP Explainer Module
======================
Provides global and local model explanations using SHAP
(SHapley Additive exPlanations).

Uses TreeExplainer for tree-based models (Random Forest, XGBoost)
which provides exact, fast SHAP value computation.
"""

import numpy as np
import os
import joblib
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("[Explainer] Warning: SHAP not installed.")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
PLOTS_DIR = os.path.join(BASE_DIR, 'notebooks', 'eda_plots')


def get_global_explanation(model, X, feature_names=None, save_plot=True):
    """
    Generate global SHAP feature importance across all samples.
    
    Creates a SHAP summary plot showing:
    - Which features have the most impact on predictions overall
    - The direction of impact (positive/negative) for each feature
    
    Args:
        model: Trained tree-based model
        X: Feature matrix (numpy array or DataFrame)
        feature_names: List of feature names
        save_plot: Whether to save the summary plot as PNG
    
    Returns:
        dict: {feature_name: mean_abs_shap_value} sorted by importance
    """
    if not HAS_SHAP:
        return {}
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    # For multiclass, shap_values is a list of arrays (one per class)
    # Compute mean absolute SHAP across all classes
    if isinstance(shap_values, list):
        # Average across classes
        mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
    else:
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
    
    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(len(mean_abs_shap))]
    
    # Create importance dict
    importance = dict(zip(feature_names, mean_abs_shap.tolist()))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    # Save summary plot
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        top_n = min(20, len(importance))
        top_features = list(importance.keys())[:top_n]
        top_values = [importance[f] for f in top_features]
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, top_n))
        ax.barh(range(top_n), top_values[::-1], color=colors)
        ax.set_yticks(range(top_n))
        ax.set_yticklabels(top_features[::-1], fontsize=9)
        ax.set_xlabel('Mean |SHAP Value|', fontsize=11)
        ax.set_title('Global Feature Importance (SHAP)', fontsize=13, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plot_path = os.path.join(PLOTS_DIR, 'shap_global_importance.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"[Explainer] Saved global SHAP plot to {plot_path}")
    
    return importance


def get_local_explanation(model, X_single, feature_names=None):
    """
    Generate local SHAP explanation for a single prediction.
    
    Shows which features pushed this specific batch's prediction
    toward or away from each class.
    
    Args:
        model: Trained tree-based model
        X_single: Feature values for one sample (1D array or 2D with 1 row)
        feature_names: List of feature names
    
    Returns:
        dict: {
            'shap_values': {feature_name: shap_value} for the predicted class,
            'base_value': float,
            'prediction': int (class index)
        }
    """
    if not HAS_SHAP:
        return {'shap_values': {}, 'base_value': 0, 'prediction': 0}
    
    X_input = np.array(X_single).reshape(1, -1)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_input)
    
    # Get model prediction index
    prediction = model.predict(X_input)[0]
    
    # Get SHAP values for the predicted class
    shap_arr = np.array(shap_values)
    
    if isinstance(shap_values, list):
        sv = np.array(shap_values[prediction]).flatten()
        base = explainer.expected_value[prediction] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
    elif shap_arr.ndim == 3:
        if shap_arr.shape[0] == 1:
            sv = shap_arr[0, :, prediction].flatten()
        else:
            sv = shap_arr[prediction, 0, :].flatten()
        base = explainer.expected_value[prediction] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
    else:
        sv = shap_arr.flatten()
        base = explainer.expected_value
    
    # Ensure base is scalar float
    if isinstance(base, (list, np.ndarray)):
        base = float(base[0])
    else:
        base = float(base)
    
    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(len(sv))]
    
    # Create feature -> SHAP value mapping
    shap_dict = {f: float(v) for f, v in zip(feature_names, sv)}
    
    # Sort by absolute value
    shap_dict = dict(sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True))
    
    return {
        'shap_values': shap_dict,
        'base_value': base,
        'prediction': int(prediction)
    }


def generate_shap_plot(shap_values_dict, batch_id="batch", save_dir=None):
    """
    Generate a waterfall-style horizontal bar chart for local SHAP values.
    
    Args:
        shap_values_dict: {feature_name: shap_value} dict
        batch_id: Batch identifier for the plot title
        save_dir: Directory to save the plot (defaults to PLOTS_DIR)
    
    Returns:
        str: Path to the saved plot
    """
    if save_dir is None:
        save_dir = os.path.join(BASE_DIR, 'reports', 'generated')
    os.makedirs(save_dir, exist_ok=True)
    
    # Get top 15 features by absolute SHAP value
    top_n = min(15, len(shap_values_dict))
    sorted_features = sorted(shap_values_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    
    features = [f[0] for f in sorted_features]
    values = [f[1] for f in sorted_features]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#06D6A0' if v >= 0 else '#EF476F' for v in values]
    
    ax.barh(range(top_n), values[::-1], color=colors[::-1], height=0.6)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(features[::-1], fontsize=9)
    ax.set_xlabel('SHAP Value (impact on prediction)', fontsize=11)
    ax.set_title(f'Feature Impact — Batch {batch_id}', fontsize=13, fontweight='bold')
    ax.axvline(x=0, color='gray', linewidth=0.8, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plot_path = os.path.join(save_dir, f'shap_{batch_id}.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return plot_path


if __name__ == '__main__':
    # Test with saved model
    model = joblib.load(os.path.join(MODELS_DIR, 'best_model.joblib'))
    feature_names = joblib.load(os.path.join(MODELS_DIR, 'feature_names.joblib'))
    print(f"Loaded model with {len(feature_names)} features")
    print("Explainer module ready.")
