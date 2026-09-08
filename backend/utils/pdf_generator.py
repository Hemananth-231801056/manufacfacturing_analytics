"""
PDF Report Generator Utility
============================
Uses ReportLab to generate professional pharmaceutical QC batch reports.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf_report(prediction_data: dict, output_path: str) -> str:
    """
    Generate a professional PDF Quality Control report using ReportLab.
    
    Args:
        prediction_data: Dict containing prediction details
        output_path: Path to save the generated PDF file
        
    Returns:
        str: Absolute path to generated PDF
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#1E293B'),
        spaceBefore=12, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#334155'),
        leading=13
    )
    
    story = []
    
    # Title & Header
    story.append(Paragraph("PHARMACEUTICAL BATCH QUALITY EVALUATION REPORT", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential QA Document", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#06B6D4'), spaceAfter=12))
    
    # Batch Info Table
    batch_id = prediction_data.get('batch_id', 'N/A')
    prediction = prediction_data.get('prediction', 'N/A')
    confidence = prediction_data.get('confidence', 0.0) * 100
    decision = prediction_data.get('decision', 'N/A')
    
    # Color badge for decision
    if decision == 'Approved':
        status_color = colors.HexColor('#10B981')
    elif decision == 'Rework':
        status_color = colors.HexColor('#F59E0B')
    else:
        status_color = colors.HexColor('#EF4444')
        
    info_data = [
        [Paragraph("<b>Batch Identifier:</b>", body_style), Paragraph(str(batch_id), body_style),
         Paragraph("<b>Evaluation Date:</b>", body_style), Paragraph(datetime.now().strftime('%Y-%m-%d'), body_style)],
        [Paragraph("<b>Predicted Status:</b>", body_style), Paragraph(f"<b>{prediction}</b>", body_style),
         Paragraph("<b>Confidence Score:</b>", body_style), Paragraph(f"<b>{confidence:.1f}%</b>", body_style)],
        [Paragraph("<b>Final Release Status:</b>", body_style), Paragraph(f"<font color='{status_color.hexval()}'><b>{decision}</b></font>", body_style),
         Paragraph("<b>Review Flag:</b>", body_style), Paragraph("QA Review Required" if prediction_data.get('review_required') else "Standard Release", body_style)]
    ]
    
    info_table = Table(info_data, colWidths=[120, 150, 120, 150])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))
    
    # Executive Summary & Decision Rationale
    story.append(Paragraph("1. Executive Summary & Decision Rationale", section_heading))
    details_text = prediction_data.get('decision_details', 'No details available.')
    story.append(Paragraph(details_text, body_style))
    story.append(Spacer(1, 8))
    
    # Recommendations & CAPA Plan
    story.append(Paragraph("2. Recommendations & Action Plan", section_heading))
    rec_text = prediction_data.get('recommendation', 'N/A')
    ca_text = prediction_data.get('corrective_action', 'N/A')
    inv_text = prediction_data.get('investigation', 'N/A')
    
    rec_data = [
        [Paragraph("<b>Recommendation:</b>", body_style), Paragraph(rec_text.replace('\n', '<br/>'), body_style)],
        [Paragraph("<b>Corrective Action:</b>", body_style), Paragraph(ca_text.replace('\n', '<br/>'), body_style)],
        [Paragraph("<b>Investigation Plan:</b>", body_style), Paragraph(inv_text.replace('\n', '<br/>'), body_style)],
    ]
    rec_table = Table(rec_data, colWidths=[130, 410])
    rec_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 10))
    
    # SHAP Plot Image (if available)
    shap_img_path = prediction_data.get('shap_plot_path')
    if shap_img_path and os.path.exists(shap_img_path):
        story.append(Paragraph("3. Explainable AI Feature Importance (SHAP Analysis)", section_heading))
        story.append(Image(shap_img_path, width=480, height=280))
        story.append(Spacer(1, 8))

    # Regulatory Disclaimer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=15, spaceAfter=10))
    disclaimer = ("<b>REGULATORY NOTICE & DISCLAIMER:</b> This Quality Control Report is generated by an "
                  "Agentic AI Decision Support System. This system is designed to assist Quality Engineers in early "
                  "defect detection. Final batch release and disposition decisions remain the sole responsibility of "
                  "authorized Quality Assurance (QA/QC) personnel in accordance with Good Manufacturing Practices (GMP) and site SOPs.")
    story.append(Paragraph(disclaimer, ParagraphStyle('Disclaimer', parent=body_style, fontSize=7, textColor=colors.HexColor('#94A3B8'))))
    
    doc.build(story)
    return output_path
