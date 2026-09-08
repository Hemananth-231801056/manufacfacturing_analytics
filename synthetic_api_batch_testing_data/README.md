# Synthetic Pharmaceutical API Batch Testing Dataset

This directory contains **10 daily lab-tested batch dataset files** generated for evaluating and demonstrating the **Agentic AI-Based API Batch Quality Evaluation & Intelligent Decision Support System**.

## Dataset Summary
- **Folder Name:** `synthetic_api_batch_testing_data/`
- **Total Files:** 10 CSV files (`Day_01.csv` through `Day_10.csv`)
- **Rows per File:** 20 batch records
- **Total Rows:** 200 batch records across all files
- **Target Classes:** `Approved`, `Rework`, `Rejected` (~50% Approved, ~25% Rework, ~25% Rejected per file)

## File List
1. `Day_01.csv` (20 rows) - Baseline production run
2. `Day_02.csv` (20 rows) - Mid-week shift testing
3. `Day_03.csv` (20 rows) - Contains minor missing values to test data cleaning imputation
4. `Day_04.csv` (20 rows) - High-throughput operational batch
5. `Day_05.csv` (20 rows) - Weekend shift production
6. `Day_06.csv` (20 rows) - Weekend shift production
7. `Day_07.csv` (20 rows) - Extended batch test run with minor missing values
8. `Day_08.csv` (20 rows) - Standard production run
9. `Day_09.csv` (20 rows) - Borderline quality parameter testing
10. `Day_10.csv` (20 rows) - Final validation run with edge-case parameter values

## Field Dictionary

| Column Name | Type | Description | Expected Range / Units |
|---|---|---|---|
| `batch_id` | String | Unique batch tracking identifier | B001 to B200 |
| `date` | Date | Laboratory testing date | YYYY-MM-DD |
| `product_code` | Integer | Product formulation code | 10, 11, 12, 13, 15, 20 |
| `weekend_shift` | Binary | Flag indicating weekend shift | 0 (No), 1 (Yes) |
| `api_water_content_percent` | Float | Moisture content in active API | % (0.4% - 5.5%) |
| `api_impurities_percent` | Float | Total organic/inorganic impurities | % (0.05% - 4.50%) |
| `api_particle_size_microns` | Float | Mean API particle size | µm (15.0 - 55.0 µm) |
| `compression_force_kn` | Float | Tablet press main compression force | kN (3.8 - 7.0 kN) |
| `fill_depth_mm` | Float | Die fill depth parameter | mm (5.0 - 6.5 mm) |
| `turret_speed_rpm` | Integer | Press turret rotational speed | rpm (28 - 48 rpm) |
| `ejection_force_n` | Float | Force required for tablet ejection | N (180.0 - 340.0 N) |
| `excipient_moisture_percent` | Float | Moisture level in excipient blend | % (3.5% - 7.5%) |
| `tablet_weight_mg` | Float | Average individual tablet weight | mg (470.0 - 530.0 mg) |
| `tablet_thickness_mm` | Float | Tablet thickness measurement | mm (2.90 - 3.70 mm) |
| `tablet_hardness_kp` | Float | Tablet breaking force (hardness) | kp (18.0 - 62.0 kp) |
| `tensile_strength_mpa` | Float | Computed compact tensile strength | MPa (0.6 - 2.4 MPa) |
| `coating_thickness_microns` | Float | Film coating thickness | µm (25.0 - 55.0 µm) |
| `waste_percentage` | Float | Total batch manufacturing material waste | % (0.8% - 14.2%) |
| `quality_label` | Categorical | Target classification outcome | Approved, Rework, Rejected |

## How to Use for Testing the AI Pipeline

1. **Upload:** Navigate to the Web Dashboard upload zone (`http://localhost:5173`).
2. **Select File:** Upload any of the individual CSV files (e.g., `Day_01.csv` or `Day_03.csv`).
3. **Pipeline Trigger:** The system automatically executes:
   - File format detection & parsing
   - Data cleaning & missing value median imputation (e.g. for `Day_03.csv`)
   - Feature engineering & SHAP impact analysis
   - Quality classification (`Approved`, `Rework`, `Rejected`)
   - Automated CAPA & QC Report PDF generation
4. **Verification:** Inspect batch status breakdown cards, download individual PDF reports, or export all reports as a `.zip` archive.
