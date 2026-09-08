"""
Reports & Model Metadata Routes
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import joblib
import io
import zipfile

from backend.database import get_db
from backend.models_db import Prediction
from backend.schemas import ModelInfo
from backend.config import MODEL_COMPARISON_PATH, FEATURE_NAMES_PATH

router = APIRouter(prefix="/api", tags=["Reports & Info"])


@router.get("/reports/{prediction_id}/download")
def download_qc_report(prediction_id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record or not record.report_path or not os.path.exists(record.report_path):
        raise HTTPException(status_code=404, detail="QC Report PDF not found.")
    filename = f"QC_Report_{record.batch_id}.pdf"
    return FileResponse(path=record.report_path, media_type='application/pdf', filename=filename)


@router.get("/reports/download-all/{document_id}")
def download_all_reports(document_id: int, db: Session = Depends(get_db)):
    records = db.query(Prediction).filter(Prediction.document_id == document_id).all()
    if not records:
        raise HTTPException(status_code=404, detail="No reports found for this document.")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for record in records:
            if record.report_path and os.path.exists(record.report_path):
                filename = f"QC_Report_{record.batch_id}.pdf"
                zip_file.write(record.report_path, arcname=filename)
                
    if zip_buffer.tell() == 0:
        raise HTTPException(status_code=404, detail="No valid PDF files could be found to zip.")
        
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": f"attachment; filename=Batch_Reports_Doc_{document_id}.zip"}
    )


@router.get("/model-info", response_model=ModelInfo)
def get_model_info():
    if not os.path.exists(MODEL_COMPARISON_PATH):
        raise HTTPException(status_code=404, detail="Model metadata not found. Train model first.")
    with open(MODEL_COMPARISON_PATH) as f:
        comp = json.load(f)
    best = comp.get("best_model", "Random Forest")
    key  = "random_forest" if "Forest" in best else "xgboost"
    m    = comp.get(key, {})
    feats = comp.get("feature_names", [])
    return ModelInfo(
        model_type=best, accuracy=m.get("accuracy", 0.0),
        f1_weighted=m.get("f1_weighted", 0.0), f1_macro=m.get("f1_macro", 0.0),
        feature_count=len(feats), feature_names=feats,
        training_samples=comp.get("training_samples", 0),
        test_samples=comp.get("test_samples", 0),
        class_distribution=comp.get("class_distribution", {})
    )


@router.get("/features")
def get_features():
    if not os.path.exists(FEATURE_NAMES_PATH):
        raise HTTPException(status_code=404, detail="Feature list not found. Train model first.")
    return {"features": joblib.load(FEATURE_NAMES_PATH)}
