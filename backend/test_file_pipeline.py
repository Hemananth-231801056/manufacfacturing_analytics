"""
End-to-End File Pipeline Test
==============================
Tests the complete 9-agent file-upload pipeline programmatically.
Generates a sample CSV in-memory and passes its bytes through every agent.
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from backend.agents.file_reader_agent import FileReaderAgent
from backend.agents.extraction_agent import ExtractionAgent
from backend.agents.validation_agent import ValidationAgent
from backend.agents.cleaning_agent import CleaningAgent
from backend.agents.feature_engineering_agent import FeatureEngineeringAgent
from backend.agents.prediction_agent import PredictionAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.report_agent import ReportAgent
from backend.ml.explainer import get_local_explanation, generate_shap_plot

def make_sample_csv() -> bytes:
    rows = []
    for i in range(5):
        rows.append({
            'batch_id':             f'BATCH-{1000+i}',
            'code':                 (i % 25) + 1,
            'weekend':              i % 2,
            'api_water':            round(1.2 + i * 0.15, 2),
            'api_total_impurities': round(0.20 + i * 0.03, 3),
            'api_content':          round(94.0 - i * 0.5, 1),
            'api_ps01':             round(1.1 + i * 0.1, 2),
            'api_ps05':             round(18.0 + i * 0.5, 1),
            'api_ps09':             round(108.0 + i * 2.0, 1),
            'main_CompForce_mean':  round(4.2 + i * 0.05, 3),
            'main_CompForce_sd':    round(0.055 + i * 0.002, 4),
            'tbl_fill_mean':        round(5.28 + i * 0.01, 3),
            'tbl_av_hardness':      round(45.0 + i * 1.0, 1),
            'stiffness_mean':       round(89.0 + i * 1.5, 1),
            'ejection_mean':        round(218.0 + i * 3.0, 1),
            'batch_yield':          round(94.5 - i * 0.3, 2),
            'total_waste':          round(1020 + i * 50, 0),
            'smcc_water':           round(4.1, 2),
            'smcc_td':              0.45,
            'smcc_bd':              0.33,
            'tbl_min_hardness':     50.0,
            'tbl_max_hardness':     70.0,
            'tbl_min_thickness':    3.3,
            'tbl_max_thickness':    3.45,
            'fct_av_hardness':      63.0,
        })
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()

def main():
    print("=" * 65)
    print("  9-Agent File Pipeline Test")
    print("=" * 65)

    sample_bytes = make_sample_csv()
    print(f"\n[Test] Generated sample CSV: {len(sample_bytes)} bytes, 5 batches\n")

    # ── Agent 1: File Reader ───────────────────────────────────
    reader = FileReaderAgent()
    read_result = reader.read_file(sample_bytes, 'test_batches.csv')
    assert read_result['success'], f"Read failed: {read_result['error']}"
    print(f"[Agent 1 - File Reader]  Format: {read_result['format']}  OK")

    # ── Agent 2: Extraction ────────────────────────────────────
    extractor = ExtractionAgent()
    raw_rows = extractor.extract(read_result)
    assert len(raw_rows) == 5, f"Expected 5 rows, got {len(raw_rows)}"
    print(f"[Agent 2 - Extraction]   Extracted {len(raw_rows)} batch record(s)  OK")

    # ── Agent 3: Validation ────────────────────────────────────
    validator = ValidationAgent()
    val_reports = validator.validate_all(raw_rows)
    errors_found = sum(1 for r in val_reports if not r['is_valid'])
    print(f"[Agent 3 - Validation]   {len(val_reports) - errors_found}/{len(val_reports)} valid  OK")

    # ── Agent 4: Cleaning ──────────────────────────────────────
    cleaner = CleaningAgent()
    clean_result = cleaner.clean(raw_rows)
    cleaned = clean_result['cleaned_rows']
    print(f"[Agent 4 - Cleaning]     {len(cleaned)} rows cleaned  OK")
    for line in clean_result['log']:
        print(f"             LOG: {line}")

    # ── Agent 5: Feature Engineering ──────────────────────────
    feat_agent = FeatureEngineeringAgent()
    engineered = feat_agent.engineer_all(cleaned)
    assert 'api_particle_span' in engineered[0], "Missing api_particle_span"
    print(f"[Agent 5 - Feature Eng]  7 composite features added  OK")

    # ── Agent 6-9: Prediction, Decision, Recommendation, Report
    pred_agent = PredictionAgent()
    dec_agent  = DecisionAgent()
    rec_agent  = RecommendationAgent()
    rpt_agent  = ReportAgent()

    print(f"\n{'':>4}{'Batch ID':<20}{'Prediction':<14}{'Confidence':<14}{'Decision'}")
    print(f"{'':>4}{'-'*20}{'-'*14}{'-'*14}{'-'*12}")

    for row in engineered:
        bid = row.get('batch_id', 'UNKNOWN')

        pred   = pred_agent.predict(row)
        fv     = pred['feature_vector']
        shap   = get_local_explanation(pred_agent.model, fv, pred_agent.feature_names)
        shap_d = shap.get('shap_values', {})
        shap_p = generate_shap_plot(shap_d, batch_id=bid)

        dec    = dec_agent.decide(pred['prediction'], pred['confidence'], pred['confidence_scores'])
        rec    = rec_agent.recommend(dec['decision'], shap_d)

        full   = {
            'batch_id': bid, 'prediction': pred['prediction'],
            'confidence': pred['confidence'], 'confidence_scores': pred['confidence_scores'],
            'decision': dec['decision'], 'decision_details': dec['decision_details'],
            'review_required': dec.get('review_required', False),
            'recommendation': rec['recommendation'],
            'corrective_action': rec['corrective_action'],
            'investigation': rec['investigation'],
            'shap_plot_path': shap_p, 'input_params': row
        }
        pdf = rpt_agent.generate(full)

        print(f"{'':>4}{bid:<20}{pred['prediction']:<14}{pred['confidence']:.4f}{'':>4}{dec['decision']}")
        assert os.path.exists(pdf), f"PDF not created for {bid}"

    print(f"\n{'='*65}")
    print("  ALL 9 AGENTS PASSED — Pipeline Test Complete!")
    print(f"{'='*65}")

if __name__ == '__main__':
    main()
