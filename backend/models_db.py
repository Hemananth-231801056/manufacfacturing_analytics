"""
Database Models
================
SQLAlchemy ORM models for the file-upload pipeline.
Two tables:
  documents  — one row per uploaded file session
  predictions — one row per batch result (FK -> documents)
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Document(Base):
    """Represents an uploaded batch file."""
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    filename    = Column(String(255), nullable=False)
    file_format = Column(String(10))                    # csv, xlsx, pdf, docx
    status      = Column(String(20), default='pending') # pending / success / failed / warning
    total_batches   = Column(Integer, default=0)
    valid_batches   = Column(Integer, default=0)
    failed_batches  = Column(Integer, default=0)
    cleaning_log    = Column(Text, nullable=True)       # JSON list of log messages
    uploaded_at = Column(DateTime, server_default=func.now())

    predictions = relationship("Prediction", back_populates="document",
                               cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class Prediction(Base):
    """
    Stores prediction results from the agent pipeline.
    Each record = one batch from an uploaded file.
    """
    __tablename__ = "predictions"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    document_id      = Column(Integer, ForeignKey("documents.id"), nullable=True)
    batch_id         = Column(String(50), nullable=False, index=True)
    input_params     = Column(Text, nullable=False)   # JSON
    prediction       = Column(String(20), nullable=False)
    confidence       = Column(Float,  nullable=False)
    confidence_scores= Column(Text, nullable=True)    # JSON
    decision         = Column(String(20), nullable=False)
    decision_details = Column(Text, nullable=True)
    recommendation   = Column(Text, nullable=True)
    corrective_action= Column(Text, nullable=True)
    investigation    = Column(Text, nullable=True)
    shap_values      = Column(Text, nullable=True)    # JSON
    shap_plot_path   = Column(String(500), nullable=True)
    report_path      = Column(String(500), nullable=True)
    validation_errors= Column(Text, nullable=True)    # JSON
    validation_warnings= Column(Text, nullable=True)  # JSON
    created_at       = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="predictions")

    def __repr__(self):
        return (f"<Prediction(id={self.id}, batch_id='{self.batch_id}', "
                f"prediction='{self.prediction}')>")
