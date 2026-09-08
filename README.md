# AI-Based API Batch Quality Evaluation System

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![React Version](https://img.shields.io/badge/react-18%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

## Description

This project implements an Agentic AI-Based decision-support system for pharmaceutical tablet manufacturing. By analyzing multi-dimensional manufacturing process parameters, the system predicts the quality outcome of a pharmaceutical batch (Approved, Rework, or Rejected) before time-consuming physical lab tests are completed.

Leveraging a multi-agent architecture, the system not only provides predictive analytics using Random Forest and XGBoost but also provides deep explainability using SHAP values. This ensures that human Quality Assurance (QA) professionals can understand the AI's reasoning, maintaining compliance with Good Manufacturing Practices (GMP) and building trust in automated decision support.

## Key Features

*   **Early Quality Prediction:** Predict batch status (Approved/Rework/Rejected) based on real-time process parameters.
*   **Explainable AI (XAI):** Global and local SHAP analysis to explain model predictions to QA personnel.
*   **Multi-Agent Architecture:** 5 logical agents (Validation, Prediction, Decision, Recommendation, QC Report) orchestrating the workflow.
*   **Automated PDF Reporting:** Programmatic generation of compliant QC reports using ReportLab.
*   **Interactive Dashboard:** A React/Vite-based frontend for monitoring batch statuses and exploring SHAP explanations.

## System Architecture

```text
[ Frontend (React + Vite) ] <--- REST ---> [ Backend (FastAPI) ]
                                                |
                                                +---> [ SQLite Database ]
                                                |
                                                +---> [ Agent Pipeline ]
                                                        1. Validation Agent
                                                        2. Prediction Agent (RF/XGBoost)
                                                        3. Explainability (SHAP)
                                                        4. Decision & Recommendation Agent
                                                        5. QC Report Generation (ReportLab)
```

## Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React, Vite, TailwindCSS, Recharts |
| **Backend** | Python, FastAPI, Uvicorn |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Machine Learning** | Scikit-Learn, XGBoost, SHAP |
| **Reporting** | ReportLab |

## Project Structure

```
x:\manufactoring\
├── backend/               # FastAPI backend, Agents, ML models
├── frontend/              # React + Vite web application
├── docs/                  # Documentation (Context, Labeling rules, Report)
├── data/                  # Dataset directory (raw and processed)
├── scripts/               # Training and data processing scripts
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Prerequisites

*   Python 3.10+
*   Node.js 18+
*   npm or yarn

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pharma-batch-ai.git
   cd pharma-batch-ai
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the Machine Learning Models:**
   ```bash
   python scripts/train_model.py
   ```

4. **Start the FastAPI Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Install Frontend Dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

6. **Start the Frontend Development Server:**
   ```bash
   npm run dev
   ```

## Dataset Attribution

The dataset used in this project is based on real industrial pharmaceutical manufacturing data sourced from Figshare:
*Žagar, A., & Mihelič, J. (2022). Scientific Data.* 
It includes 1,005 batches across 25 product codes. Please note that Quality Labels have been synthetically engineered for educational and modeling purposes based on project assumptions.

## Limitations

*   **Label Assumptions:** Target labels (Approved/Rework/Rejected) are synthesized via assumed thresholds, not actual industrial decisions.
*   **Data Scope:** Models are trained on historical data for a specific product family.
*   **Integration:** Currently standalone; not integrated in real-time with an industrial Manufacturing Execution System (MES).

## Future Work

*   Real-time Manufacturing Execution System (MES) and Process Analytical Technology (PAT) integration.
*   Expansion to multi-product, multi-site modeling.
*   Implementation of 21 CFR Part 11 compliant audit trails and electronic signatures.
*   Bayesian optimization for hyperparameter tuning.

## License & Disclaimer

This project is licensed under the MIT License.

**Disclaimer:** This software is a proof-of-concept AI decision-support system. It is NOT intended for actual clinical or pharmaceutical release without extensive validation, regulatory approval, and human QA oversight.
