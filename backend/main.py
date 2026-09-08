"""
FastAPI Main Application
"""
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import PLOTS_DIR, REPORTS_DIR
from backend.database import create_tables
from backend.routes import prediction, history, reports

app = FastAPI(
    title="Agentic AI Pharmaceutical Batch Quality Evaluation System",
    description="File-upload-based intelligent decision support system for pharmaceutical QC.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("[Startup] Initialising database tables …")
    create_tables()
    print("[Startup] Ready.")

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app.mount("/plots",          StaticFiles(directory=PLOTS_DIR),   name="plots")
app.mount("/static/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

app.include_router(prediction.router)
app.include_router(history.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {
        "status": "Online",
        "version": "2.0.0",
        "workflow": "File Upload -> Extract -> Validate -> Clean -> Predict -> Report",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
