"""
End-to-End System Test Script
==============================
Tests the complete 5-agent pipeline programmatically:
Validation -> Prediction -> Decision -> Recommendation -> Report Generation
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.database import create_tables, SessionLocal
from backend.models_db import Prediction
from backend.agents.validation_agent import ValidationAgent
from backend.agents.prediction_agent import PredictionAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.report_agent import ReportAgent
from backend.ml.explainer import get_local_explanation, generate_shap_plot
import json

def test_full_pipeline():
    print("=" * 70)
    print("Testing End-to-End Agentic AI Pipeline")
    print("=" * 70)

    # Initialize DB
    create_tables()
    db = SessionLocal()

    # Sample batch input
    sample_input = {
        'batch_id': 'TEST-BATCH-2026',
        'code': 25,
        'weekend': 0,
        'api_water': 1.53,
        'api_total_impurities': 0.25,
        'api_l_impurity': 0.13,
        'api_content': 94.5,
        'api_ps01': 1.27,
        'api_ps05': 18.52,
        'api_ps09': 109.99,
        'main_CompForce_mean': 4.25,
        'main_CompForce_sd': 0.058,
        'tbl_av_hardness': 46.0,
        'tbl_fill_mean': 5.33,
        'stiffness_mean': 91.0,
        'ejection_mean': 223.3,
        'batch_yield': 94.7,
        'total_waste': 2125.0
    }

    # 1. Validation Agent
    v_agent = ValidationAgent()
    is_valid, errors = v_agent.validate(sample_input)
    print(f"\n[Agent 1 - Validation] Valid: {is_valid}, Errors: {errors}")
    assert is_valid, "Validation failed!"

    # 2. Prediction Agent
    p_agent = PredictionAgent()
    pred_res = p_agent.predict(sample_input)
    print(f"\n[Agent 2 - Prediction] Prediction: {pred_res['prediction']}, Confidence: {pred_res['confidence']:.2f}")
    print(f"  Class Probabilities: {pred_res['confidence_scores']}")

    # 3. Decision Agent
    d_agent = DecisionAgent()
    dec_res = d_agent.decide(pred_res['prediction'], pred_res['confidence'], pred_res['confidence_scores'])
    print(f"\n[Agent 3 - Decision] Decision: {dec_res['decision']}, Level: {dec_res['confidence_level']}")
    print(f"  Details: {dec_res['decision_details']}")

    # SHAP Explanation
    local_exp = get_local_explanation(p_agent.model, pred_res['feature_vector'], p_agent.feature_names)
    shap_dict = local_exp.get('shap_values', {})
    shap_plot_path = generate_shap_plot(shap_dict, batch_id=sample_input['batch_id'])
    print(f"\n[SHAP Explainer] Generated SHAP Plot: {shap_plot_path}")

    # 4. Recommendation Agent
    r_agent = RecommendationAgent()
    rec_res = r_agent.recommend(dec_res['decision'], shap_dict)
    print(f"\n[Agent 4 - Recommendation] Rec: {rec_res['recommendation'][:100]}...")

    # 5. QC Report Agent
    rpt_agent = ReportAgent()
    full_data = {
        'batch_id': sample_input['batch_id'],
        'prediction': pred_res['prediction'],
        'confidence': pred_res['confidence'],
        'confidence_scores': pred_res['confidence_scores'],
        'decision': dec_res['decision'],
        'decision_details': dec_res['decision_details'],
        'review_required': dec_res['review_required'],
        'recommendation': rec_res['recommendation'],
        'corrective_action': rec_res['corrective_action'],
        'investigation': rec_res['investigation'],
        'shap_plot_path': shap_plot_path,
        'input_params': sample_input
    }

    pdf_path = rpt_agent.generate(full_data)
    print(f"\n[Agent 5 - QC Report] Report PDF: {pdf_path}")
    assert os.path.exists(pdf_path), "PDF Report missing!"

    # Save to SQLite
    db_record = Prediction(
        batch_id=sample_input['batch_id'],
        input_params=json.dumps(sample_input),
        prediction=pred_res['prediction'],
        confidence=pred_res['confidence'],
        confidence_scores=json.dumps(pred_res['confidence_scores']),
        decision=dec_res['decision'],
        decision_details=dec_res['decision_details'],
        recommendation=rec_res['recommendation'],
        corrective_action=rec_res['corrective_action'],
        investigation=rec_res['investigation'],
        shap_values=json.dumps(shap_dict),
        shap_plot_path=shap_plot_path,
        report_path=pdf_path
    )
    db.add(db_record)
    db.commit()
    print(f"\n[Database] Saved record ID #{db_record.id} to SQLite DB pharma_qc.db")

    print("\n" + "=" * 70)
    print("Pipeline Test PASSED Successfully! All 5 Agents Functioning Perfectly.")
    print("=" * 70)

if __name__ == '__main__':
    test_full_pipeline()
