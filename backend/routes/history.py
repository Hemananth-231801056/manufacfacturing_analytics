"""
History & Documents Route
==========================
GET /api/documents           — list all uploaded document sessions
GET /api/documents/{id}      — detail + all batch predictions for a document
GET /api/predictions         — paginated flat list of all batch predictions
GET /api/predictions/{id}    — single prediction detail
"""

import json
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.models_db import Document, Prediction
from backend.schemas import (
    DocumentSummary, PredictionHistoryItem, PredictionResponse, ProcessBatchesResponse
)

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/documents", response_model=List[DocumentSummary])
def list_documents(db: Session = Depends(get_db)):
    """Return all uploaded document sessions, newest first."""
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        DocumentSummary(
            id=d.id, filename=d.filename, file_format=d.file_format or "",
            status=d.status, total_batches=d.total_batches or 0,
            valid_batches=d.valid_batches or 0, failed_batches=d.failed_batches or 0,
            uploaded_at=d.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if d.uploaded_at else ""
        )
        for d in docs
    ]


@router.get("/documents/{document_id}/predictions", response_model=ProcessBatchesResponse)
def get_document_predictions(document_id: int, db: Session = Depends(get_db)):
    """Return all batch predictions associated with a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    records = (db.query(Prediction)
               .filter(Prediction.document_id == document_id)
               .order_by(Prediction.id)
               .all())

    results = [_pred_to_response(r) for r in records]
    return ProcessBatchesResponse(
        document_id=document_id,
        total_processed=len(results),
        results=results
    )


@router.get("/predictions", response_model=List[PredictionHistoryItem])
def get_all_predictions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    decision_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Paginated flat list of all batch predictions."""
    q = db.query(Prediction)
    if decision_filter and decision_filter.lower() != "all":
        q = q.filter(Prediction.decision == decision_filter.capitalize())
    records = q.order_by(Prediction.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    return [
        PredictionHistoryItem(
            id=r.id, document_id=r.document_id, batch_id=r.batch_id,
            prediction=r.prediction, confidence=r.confidence,
            decision=r.decision,
            created_at=r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ""
        )
        for r in records
    ]


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction_detail(prediction_id: int, db: Session = Depends(get_db)):
    r = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Prediction not found.")
    return _pred_to_response(r)


def _pred_to_response(r: Prediction) -> PredictionResponse:
    return PredictionResponse(
        id=r.id, document_id=r.document_id, batch_id=r.batch_id,
        prediction=r.prediction, confidence=r.confidence,
        confidence_scores=json.loads(r.confidence_scores or "{}"),
        decision=r.decision, decision_details=r.decision_details or "",
        recommendation=r.recommendation or "",
        corrective_action=r.corrective_action or "",
        investigation=r.investigation or "",
        shap_values=json.loads(r.shap_values or "{}"),
        shap_plot_url=f"/plots/shap_{r.batch_id}.png" if r.shap_plot_path else None,
        report_url=f"/api/reports/{r.id}/download" if r.report_path else None,
        validation_errors=json.loads(r.validation_errors or "[]"),
        validation_warnings=json.loads(r.validation_warnings or "[]"),
        created_at=r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ""
    )
