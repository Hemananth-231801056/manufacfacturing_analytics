"""
Pydantic Schemas
=================
Request / Response schemas for the file-upload pipeline API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


# ─── Upload / Processing Responses ─────────────────────────────────────────

class ValidationReport(BaseModel):
    batch_index: int
    batch_id: Optional[str] = None
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class CleanedPreview(BaseModel):
    """A single cleaned batch row for the data-preview table."""
    batch_id: str
    data: Dict[str, Any]


class UploadPreviewResponse(BaseModel):
    """Returned by POST /api/upload — before prediction runs."""
    document_id: int
    filename: str
    file_format: str
    total_extracted: int
    validation_reports: List[ValidationReport]
    cleaning_log: List[str]
    cleaned_preview: List[CleanedPreview]
    has_errors: bool
    error_message: Optional[str] = None


# ─── Per-Batch Prediction ───────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    id: Optional[int] = None
    document_id: Optional[int] = None
    batch_id: str
    prediction: str
    confidence: float
    confidence_scores: Dict[str, float]
    decision: str
    decision_details: str
    recommendation: str
    corrective_action: str
    investigation: str
    shap_values: Dict[str, float]
    shap_plot_url: Optional[str] = None
    report_url: Optional[str] = None
    validation_errors: List[str] = []
    validation_warnings: List[str] = []
    created_at: Optional[str] = None


class ProcessBatchesResponse(BaseModel):
    """Returned by POST /api/process — after prediction runs."""
    document_id: int
    total_processed: int
    results: List[PredictionResponse]


# ─── History / Document List ────────────────────────────────────────────────

class DocumentSummary(BaseModel):
    id: int
    filename: str
    file_format: str
    status: str
    total_batches: int
    valid_batches: int
    failed_batches: int
    uploaded_at: str


class PredictionHistoryItem(BaseModel):
    id: int
    document_id: Optional[int] = None
    batch_id: str
    prediction: str
    confidence: float
    decision: str
    created_at: str


# ─── Model Info ─────────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    model_type: str
    accuracy: float
    f1_weighted: float
    f1_macro: float
    feature_count: int
    feature_names: List[str]
    training_samples: int
    test_samples: int
    class_distribution: Dict[str, int]
