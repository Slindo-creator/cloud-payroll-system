import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_employee_payslip(employee_name, email, role, gross, tax, net):
    """Generates a structured, professional corporate PDF payslip file."""
    
    # Define document name and page geometry boundaries
    filename = f"payslip_{employee_name.lower().replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Establish document stylesheets
    styles = getSampleStyleSheet()
    
    # Custom color palette coordinates
    primary_color = colors.HexColor("#1A365D")  # Deep Navy Blue
    text_dark = colors.HexColor("#2D3748")      # Charcoal Body Text
    accent_gray = colors.HexColor("#EDF2F7")    # Light Background Fill
    
    # Typography Styles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=primary_color, spaceAfter=6)
    sub_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.gray, spaceAfter=20)
    section_title = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=14, leading=18, textColor=primary_color, spaceBefore=10, spaceAfter=10)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=text_dark)
    bold_body = ParagraphStyle('BoldBodyText', parent=body_style, fontName='Helvetica-Bold')
    
    # FIX: Creating a clean, distinct style for the deductions text layout
    deduction_style = ParagraphStyle('DeductionText', parent=body_style, textColor=colors.HexColor("#C53030"))

    # 1. Header Banner Block
    story.append(Paragraph("CLOUD PAYROLL SYSTEM CORP", title_style))
    story.append(Paragraph(f"Official Employee Earnings Statement — Generated: {datetime.now().strftime('%Y-%m-%d')}", sub_style))
    story.append(Spacer(1, 10))
    
    # 2. Employee Profile Metadata Table
    story.append(Paragraph("Employee Information", section_title))
    emp_data = [
        [Paragraph("<b>Employee Name:</b>", body_style), Paragraph(employee_name, body_style), Paragraph("<b>Pay Period:</b>", body_style), Paragraph("Current Month", body_style)],
        [Paragraph("<b>Email Address:</b>", body_style), Paragraph(email, body_style), Paragraph("<b>Corporate Role:</b>", body_style), Paragraph(role, body_style)]
    ]
    emp_table = Table(emp_data, colWidths=[110, 160, 110, 150])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), accent_gray),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))
    
    # 3. Financial Calculations Ledger Breakdown Table
    story.append(Paragraph("Earnings & Deductions Summary", section_title))
    financial_data = [
        [Paragraph("Description", bold_body), Paragraph("Amount", bold_body)],
        [Paragraph("Gross Earnings Base Payout", body_style), Paragraph(f"R {gross:.2f}", body_style)],
        [Paragraph("Statutory Income Tax Withholding (20%)", body_style), Paragraph(f"- R {tax:.2f}", deduction_style)], # Fixed!
        [Paragraph("<b>Net Take-Home Pay</b>", bold_body), Paragraph(f"<b>R {net:.2f}</b>", bold_body)]
    ]
    fin_table = Table(financial_data, colWidths=[380, 150])
    fin_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1.5, primary_color), # Solid rule line under headers
        ('PADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,3), (-1,3), accent_gray),     # Highlight Net Pay total block
        ('LINEABOVE', (0,3), (-1,3), 1, primary_color),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),               # Align currency values to the right side
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 40))
    
    # 4. Footer Legal Disclaimer
    story.append(Paragraph("<font size=8 color=gray>This document is a confidential, automated payroll confirmation. If you find any data discrepancies, please notify your internal HR/Finance controller immediately.</font>", body_style))
    
    # Build Document File
    doc.build(story)
    print(f"Success: Generated local PDF record as '{filename}'")

if __name__ == "__main__":
    generate_employee_payslip("John Doe", "john.doe@company.com", "HR_Admin", 5000.00, 1000.00, 4000.00)
