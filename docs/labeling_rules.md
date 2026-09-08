# Quality Labeling Methodology & Rules

## 1. The Challenge of Missing Labels

In real-world pharmaceutical manufacturing, public datasets rarely include final batch release decisions (Approved / Rework / Rejected). This omission is due to the proprietary nature of release decisions, commercial sensitivities, and strict regulatory confidentiality. 

To utilize the Figshare dataset (Žagar & Mihelič, Scientific Data 2022) for supervised machine learning, we must programmatically engineer the target variable (`Quality_Label`). **It is critical to note that the resulting labels are PROJECT ASSUMPTIONS and do not represent the actual industrial release decisions made by the original manufacturer.**

## 2. Quality Labeling Methodology

We engineered the `Quality_Label` by applying deterministic rules to key analytical laboratory parameters present in the dataset. We selected features that correspond directly to standard pharmacopeial quality attributes:
1.  **Dissolution Rate:** How quickly the API dissolves in a simulated gastric/intestinal medium.
2.  **Impurity Levels:** Unwanted chemicals present in the final product.
3.  **Residual Solvents:** Trace solvents left over from the manufacturing process.
4.  **Assay / API Content:** The actual concentration of the active ingredient.

## 3. Parameter Thresholds & Specifications

The following table defines the thresholds used to simulate our synthetic quality labels:

| Parameter Category | Metric / Feature | Approved Threshold | Rework Threshold | Rejected Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **Dissolution** | `Dissolution_Q30` (%) | ≥ 80.0% | 75.0% - 79.9% | < 75.0% |
| **Impurities** | `Total_Impurities` (%) | ≤ 0.5% | 0.51% - 1.0% | > 1.0% |
| **Solvents** | `Residual_Solvent_ppm` | ≤ 500 ppm | 501 - 1000 ppm | > 1000 ppm |
| **Assay** | `API_Assay` (%) | 95.0% - 105.0% | 90.0%-94.9% or 105.1%-110.0% | < 90.0% or > 110.0% |

## 4. Decision Logic (Hierarchical)

The system applies a strict, hierarchical decision logic to assign the final batch label:

1.  **Rule 1 (REJECTED):** If *any single parameter* falls into the **Rejected** threshold range, the entire batch is labeled as **Rejected**. (Life-safety critical failure).
2.  **Rule 2 (REWORK):** If no parameters are Rejected, but *at least one parameter* falls into the **Rework** threshold range, the batch is labeled as **Rework**. (Marginal failure that might be remediable via reprocessing, though costly).
3.  **Rule 3 (APPROVED):** If *all parameters* satisfy the **Approved** thresholds, the batch is labeled as **Approved**.

## 5. Pharmaceutical Rationale

The selected thresholds are calibrated based on established regulatory standards:
*   **USP Dissolution Q Criteria:** The United States Pharmacopeia typically requires a minimum dissolution "Q" value of 80% dissolved at a specified time (e.g., 30 or 45 minutes) for immediate-release tablets.
*   **ICH Q3A/B (Impurities):** The International Council for Harmonisation sets strict qualification and identification thresholds for impurities, generally keeping total unknown impurities well below 1.0%.
*   **ICH Q3C (Residual Solvents):** Sets PDE (Permitted Daily Exposure) limits; Class 2/3 solvents typically have limits in the hundreds to thousands of ppm (e.g., 500 ppm used here as a conservative proxy).
*   **Standard Assay Limits:** Most pharmacopeial monographs require the active ingredient to be between 95.0% and 105.0% of the label claim.

## 6. Class Distribution and Calibration

The thresholds were iteratively calibrated to achieve a realistic, yet imbalanced class distribution suitable for anomaly detection ML tasks, roughly targeting:
*   ~85-90% Approved
*   ~5-10% Rework
*   ~2-5% Rejected

*Again, explicitly state these are PROJECT ASSUMPTIONS designed to simulate a realistic pharmaceutical AI decision-support environment.*
