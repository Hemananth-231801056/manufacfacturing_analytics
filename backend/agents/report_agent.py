"""
QC Report Agent
===============
Agent 5 of 5 in the Agentic AI Pipeline.

Orchestrates the generation of downloadable, professional PDF QC reports
using the pdf_generator utility.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.config import REPORTS_DIR
from backend.utils.pdf_generator import generate_pdf_report


class ReportAgent:
    """Agent responsible for assembling and compiling PDF Quality Control Reports."""

    def generate(self, prediction_data: dict) -> str:
        """
        Compile and generate a PDF report for a given batch prediction.
        
        Args:
            prediction_data: Full prediction dataset including batch_id, SHAP, decision details
            
        Returns:
            str: Relative/Absolute file path to the generated PDF report
        """
        batch_id = prediction_data.get('batch_id', 'batch_unknown')
        filename = f"QC_Report_{batch_id}.pdf"
        output_path = os.path.join(REPORTS_DIR, filename)

        try:
            pdf_path = generate_pdf_report(prediction_data, output_path)
            print(f"[Report Agent] Generated QC Report PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"[Report Agent] Error generating PDF report: {e}")
            return None
