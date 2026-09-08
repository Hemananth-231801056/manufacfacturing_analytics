"""
Upload & Prediction Route
=========================
Implements the two-phase file-upload pipeline:

Phase 1  POST /api/upload
  - Read file bytes from multipart upload
  - Run Agents 1-4 (FileReader, Extraction, Validation, Cleaning)
  - Return data preview + validation report to frontend

Phase 2  POST /api/process/{document_id}
  - Load cleaned rows stored in DB for the document
  - Run Agents 5-9 (FeatureEng, Prediction, Decision, Recommendation, Report)
  - Persist results and return full batch predictions
"""

import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models_db import Document, Prediction
from backend.schemas import (
    UploadPreviewResponse, ValidationReport, CleanedPreview,
    ProcessBatchesResponse, PredictionResponse
)
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

router = APIRouter(prefix="/api", tags=["Upload & Prediction"])

# Singleton agent instances (loaded once at startup)
file_reader = FileReaderAgent()
extractor   = ExtractionAgent()
validator   = ValidationAgent()
cleaner     = CleaningAgent()
feat_eng    = FeatureEngineeringAgent()
predictor   = PredictionAgent()
decider     = DecisionAgent()
recommender = RecommendationAgent()
reporter    = ReportAgent()


# ─── PHASE 1: Upload + Preview ────────────────────────────────────────────

@router.post("/upload", response_model=UploadPreviewResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accept an uploaded batch file, run Agents 1-4, and return
    a data preview with validation results — no prediction yet.
    """
    file_bytes = await file.read()
    filename   = file.filename or "upload"

    # Agent 1: Read
    read_result = file_reader.read_file(file_bytes, filename)
    if not read_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File read failed: {read_result['error']}"
        )

    # Agent 2: Extract
    raw_rows = extractor.extract(read_result)
    if not raw_rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No batch records could be extracted from the uploaded file."
        )

    # Agent 3: Validate
    val_reports = validator.validate_all(raw_rows)

    # Agent 4: Clean (cleans all rows regardless of validation outcome)
    clean_result = cleaner.clean(raw_rows)
    cleaned_rows = clean_result["cleaned_rows"]
    cleaning_log = clean_result["log"]

    # Persist document record + cleaned rows (stored as JSON in cleaning_log field)
    has_errors   = any(r["is_valid"] is False for r in val_reports)
    valid_count  = sum(1 for r in val_reports if r["is_valid"])
    failed_count = len(val_reports) - valid_count

    doc = Document(
        filename      = filename,
        file_format   = read_result["format"],
        status        = "warning" if has_errors else "ready",
        total_batches = len(cleaned_rows),
        valid_batches = valid_count,
        failed_batches= failed_count,
        cleaning_log  = json.dumps({
            "log": cleaning_log,
            "cleaned_rows": cleaned_rows   # store for phase 2
        })
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Build response
    val_response = [
        ValidationReport(
            batch_index = i,
            batch_id    = cleaned_rows[i].get("batch_id") if i < len(cleaned_rows) else None,
            is_valid    = r["is_valid"],
            errors      = r["errors"],
            warnings    = r["warnings"]
        )
        for i, r in enumerate(val_reports)
    ]

    preview = [
        CleanedPreview(
            batch_id = row.get("batch_id", f"BATCH-{i+1}"),
            data     = {k: v for k, v in row.items() if k != "batch_id"}
        )
        for i, row in enumerate(cleaned_rows[:50])  # cap preview at 50 rows
    ]

    return UploadPreviewResponse(
        document_id        = doc.id,
        filename           = filename,
        file_format        = read_result["format"],
        total_extracted    = len(cleaned_rows),
        validation_reports = val_response,
        cleaning_log       = cleaning_log,
        cleaned_preview    = preview,
        has_errors         = has_errors
    )


# ─── PHASE 2: Process + Predict ───────────────────────────────────────────

@router.post("/process/{document_id}", response_model=ProcessBatchesResponse)
def process_document(document_id: int, db: Session = Depends(get_db)):
    """
    Run Agents 5-9 (FeatureEng, Prediction, Decision, Recommendation, Report)
    on the cleaned rows stored for a previously uploaded document.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    stored = json.loads(doc.cleaning_log or "{}")
    cleaned_rows = stored.get("cleaned_rows", [])
    if not cleaned_rows:
        raise HTTPException(status_code=422, detail="No cleaned rows available for processing.")

    results = []
    for row in cleaned_rows:
        batch_id = str(row.get("batch_id", "BATCH-UNK"))

        try:
            # Agent 5: Feature Engineering
            engineered_row = feat_eng.engineer(row)
            feature_vector = feat_eng.to_feature_vector(engineered_row)

            # Agent 6: Prediction
            pred_res = predictor.predict(engineered_row)
            prediction        = pred_res["prediction"]
            confidence        = pred_res["confidence"]
            confidence_scores = pred_res["confidence_scores"]
            fv                = pred_res["feature_vector"]

            # SHAP explanation
            shap_dict      = {}
            shap_plot_path = None
            try:
                local_exp = get_local_explanation(
                    predictor.model, fv, predictor.feature_names
                )
                shap_dict = local_exp.get("shap_values", {})
                shap_plot_path = generate_shap_plot(shap_dict, batch_id=batch_id)
            except Exception as e:
                print(f"[Process Route] SHAP failed for {batch_id}: {e}")

            # Agent 7: Decision
            dec_res         = decider.decide(prediction, confidence, confidence_scores)
            decision        = dec_res["decision"]
            decision_details= dec_res["decision_details"]

            # Agent 8: Recommendation
            rec_res           = recommender.recommend(decision, shap_dict)
            recommendation    = rec_res["recommendation"]
            corrective_action = rec_res["corrective_action"]
            investigation     = rec_res["investigation"]

            # Agent 9: QC Report
            full_data = {
                "batch_id": batch_id, "prediction": prediction,
                "confidence": confidence, "confidence_scores": confidence_scores,
                "decision": decision, "decision_details": decision_details,
                "review_required": dec_res.get("review_required", False),
                "recommendation": recommendation,
                "corrective_action": corrective_action,
                "investigation": investigation,
                "shap_plot_path": shap_plot_path, "input_params": row
            }
            report_path = reporter.generate(full_data)

            # Persist prediction
            db_rec = Prediction(
                document_id       = document_id,
                batch_id          = batch_id,
                input_params      = json.dumps({k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                                                for k, v in row.items()}),
                prediction        = prediction,
                confidence        = confidence,
                confidence_scores = json.dumps(confidence_scores),
                decision          = decision,
                decision_details  = decision_details,
                recommendation    = recommendation,
                corrective_action = corrective_action,
                investigation     = investigation,
                shap_values       = json.dumps(shap_dict),
                shap_plot_path    = shap_plot_path,
                report_path       = report_path,
                validation_errors = "[]",
                validation_warnings = "[]"
            )
            db.add(db_rec)
            db.commit()
            db.refresh(db_rec)

            report_url     = f"/api/reports/{db_rec.id}/download" if report_path else None
            shap_plot_url  = f"/plots/shap_{batch_id}.png" if shap_plot_path else None

            results.append(PredictionResponse(
                id=db_rec.id, document_id=document_id, batch_id=batch_id,
                prediction=prediction, confidence=confidence,
                confidence_scores=confidence_scores, decision=decision,
                decision_details=decision_details, recommendation=recommendation,
                corrective_action=corrective_action, investigation=investigation,
                shap_values=shap_dict, shap_plot_url=shap_plot_url,
                report_url=report_url,
                created_at=db_rec.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ))

        except Exception as e:
            print(f"[Process Route] Batch {batch_id} failed: {e}")
            results.append(PredictionResponse(
                batch_id=batch_id, document_id=document_id,
                prediction="Error", confidence=0.0,
                confidence_scores={}, decision="Error",
                decision_details=str(e), recommendation="",
                corrective_action="", investigation="",
                shap_values={}, validation_errors=[str(e)]
            ))

    # Update document status
    doc.status = "success"
    doc.total_batches = len(results)
    doc.valid_batches = sum(1 for r in results if r.prediction != "Error")
    doc.failed_batches = sum(1 for r in results if r.prediction == "Error")
    db.commit()

    return ProcessBatchesResponse(
        document_id=document_id,
        total_processed=len(results),
        results=results
    )
