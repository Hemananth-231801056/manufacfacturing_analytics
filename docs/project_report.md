# Project Report: AI-Based API Batch Quality Evaluation System

## 1. Abstract
The pharmaceutical industry relies on rigorous batch review processes to ensure drug safety and efficacy. Currently, Quality Assurance (QA) personnel manually review over 50 process parameters and physical lab results before releasing a batch, leading to bottlenecks, subjective decisions, and delayed market entry. This project proposes an AI-based decision-support system utilizing Random Forest and XGBoost algorithms to predict final batch quality (Approved, Rework, Rejected) from early-stage process parameters. Evaluated on an industrial dataset of 1,005 batches, the models demonstrate robust predictive capability. Furthermore, the integration of SHapley Additive exPlanations (SHAP) provides global and local interpretability, essential for regulatory compliance. An agentic architecture consisting of five logical agents orchestrates the prediction, decision-making, and automated generation of PDF quality reports. This framework offers a scalable, transparent approach to pharmaceutical Quality by Design (QbD).

## 2. Problem Statement
In pharmaceutical tablet manufacturing, the manual review of Quality Control (QC) results and batch records is highly inefficient. Reviewing multi-dimensional data across high-speed tablet presses and complex granulation processes makes it difficult to detect multivariate deviations. Waiting for end-product physical lab testing (e.g., 14-day incubations or complex chromatography) creates massive inventory bottlenecks.

## 3. Existing System
The current industrial standard involves:
*   Manual execution of physical and chemical laboratory tests post-manufacturing.
*   QA analysts reviewing paper or digital Batch Manufacturing Records (BMRs) line-by-line.
*   A reactive paradigm: process failures are only detected *after* the entire batch is produced, resulting in costly scrap or rework.

## 4. Proposed System
We propose a multi-agent AI decision-support system featuring:
*   **Early Prediction Pipeline:** Machine learning models that infer quality outcomes directly from continuous process telemetry.
*   **Explainable AI:** SHAP integration to provide the "why" behind every prediction, crucial for GMP compliance.
*   **Automated Document Generation:** An automated reporting agent that compiles process data, model predictions, and SHAP explanations into a compliant PDF.

## 5. Dataset Description
The dataset is derived from real industrial data (Figshare: Žagar & Mihelič, 2022).
*   **Size:** 1,005 individual batches.
*   **Scope:** 25 product codes within a tablet product family.
*   **Features:** Over 90 columns, encompassing 35 continuous process parameters (e.g., compression force, granulator speed, temperatures) and 55 QC laboratory parameters (e.g., dissolution rates, impurities, assays).

## 6. Manufacturing KPIs
Key Performance Indicators evaluated in this context include:
*   **Dissolution Rate (Q30):** Percentage of API released in 30 minutes.
*   **Impurity Profile:** Total and unknown impurities.
*   **Process Capability (Cpk):** Statistical measure of process reliability.
*   **Yield & Waste:** Efficiency of raw material conversion.

## 7. Methodology
1.  **Data Preprocessing:** Handled missing sensor data via interpolation, merged disparate lab and process datasets, and normalized continuous features.
2.  **Feature Engineering:** Engineered 7 pharma-specific composite features (e.g., `Compression_Efficiency_Index`, `Thermal_Stress_Metric`) based on domain knowledge.
3.  **Quality Label Engineering:** Applied hierarchical programmatic rules (outlined in `labeling_rules.md`) using USP/ICH thresholds to synthesize `Approved`, `Rework`, and `Rejected` labels.
4.  **Model Development:** Trained Random Forest and XGBoost classifiers. Addressed class imbalance using SMOTE.
5.  **Explainable AI:** Calculated global feature importance and generated local SHAP force plots for individual batches.
6.  **Agentic Architecture:** Deployed a FastAPI backend orchestrating 5 specialized agents (Validation, Prediction, Decision, Recommendation, QC Report).

## 8. Model Comparison

Empirical evaluation results on a 20% stratified test set (201 batches):

| Model | Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score (Weighted) | ROC-AUC (OVR) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest (Best)** | **0.8060** | **0.8183** | **0.8060** | **0.8036** | **0.8672** |
| XGBoost | 0.7861 | 0.7928 | 0.7861 | 0.7837 | 0.8600 |

## 9. SHAP Analysis
SHAP analysis provided critical insights. Global feature importance revealed that parameters such as `Main_Compression_Force` and `Granulation_Temperature` had the highest impact on pushing a batch toward a 'Rejected' state. Local explanations for individual batches allow a QA reviewer to see precisely how an unexpected spike in temperature contributed to an anomaly prediction.

## 10. System Architecture
The system employs a React+Vite frontend for a responsive user dashboard, communicating via REST to a FastAPI backend. The backend manages a SQLite database for batch records and orchestrates the Python-based Agent Pipeline (ML inference, SHAP generation, ReportLab PDF creation).

## 11. Deployment
*   **Environment:** Python 3.10+, Node 18+.
*   **Backend:** Uvicorn serving FastAPI.
*   **Frontend:** Local Node development server.
*   **Instructions:** Refer to `README.md` for local deployment steps.

## 12. Limitations
*   **Synthetic Labels:** The target variables are assumed; they do not reflect the proprietary release decisions of the original manufacturer.
*   **Data Scope:** The models are constrained to a single product family's historical data.
*   **Integration:** The system is currently an offline decision-support tool, not integrated in real-time with an industrial MES or historians (e.g., OSIsoft PI).

## 13. Future Work
*   Integration with Real-Time Process Analytical Technology (PAT).
*   Scaling to multi-product, multi-site databases.
*   Implementing strict 21 CFR Part 11 compliance (Audit trails, e-signatures).
*   Employing Bayesian optimization for dynamic model retraining.

## 14. Conclusion
The AI-Based API Batch Quality Evaluation System successfully demonstrates how machine learning can transform the retrospective, manual QA batch release process into a predictive, proactive, and automated workflow. By anchoring advanced ML algorithms with SHAP explainability and automated reporting, the system meets the rigid transparency requirements of the pharmaceutical industry.

## 15. References
1.  Žagar, A., & Mihelič, J. (2022). *Dataset of manufacturing parameters and laboratory results of solid dosage form.* Scientific Data.
2.  Lundberg, S. M., & Lee, S.-I. (2017). *A Unified Approach to Interpreting Model Predictions.* NeurIPS.
3.  Chen, T., & Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System.* KDD.
4.  ICH Harmonised Tripartite Guideline (Q7, Q8, Q9, Q10, Q3A-C).
