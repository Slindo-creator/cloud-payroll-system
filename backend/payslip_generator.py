import os
import sys
import psycopg2
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from dotenv import load_dotenv
load_dotenv()

# Your custom bucket target name
S3_BUCKET_NAME = "employee-payslips-project"


def get_db_connection():
    """Connects securely using system environment variables, keeping credentials hidden."""
    try:
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            sslmode='require'
        )
        return conn  # CRUCIAL: This passes the connection back to the script!
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)


def generate_employee_payslip(employee_name, email, role, gross, tax, net):
    """Generates a structured, professional corporate PDF payslip file."""
    filename = f"payslip_{employee_name.lower().replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    styles = getSampleStyleSheet()

    # Custom color palette coordinates
    primary_color = colors.HexColor("#1A365D")
    text_dark = colors.HexColor("#2D3748")
    accent_gray = colors.HexColor("#EDF2F7")

    # Typography Styles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28,
                                 textColor=primary_color, spaceAfter=6)
    sub_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.gray,
                               spaceAfter=20)
    section_title = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=14, leading=18,
                                   textColor=primary_color, spaceBefore=10, spaceAfter=10)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, textColor=text_dark)
    bold_body = ParagraphStyle('BoldBodyText', parent=body_style, fontName='Helvetica-Bold')
    deduction_style = ParagraphStyle('DeductionText', parent=body_style, textColor=colors.HexColor("#C53030"))

    # 1. Header Banner Block
    story.append(Paragraph("CLOUD PAYROLL SYSTEM CORP", title_style))
    story.append(Paragraph(f"Official Employee Earnings Statement — Generated: {datetime.now().strftime('%Y-%m-%d')}",
                           sub_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Employee Information", section_title))
    emp_data = [
        [Paragraph("<b>Employee Name:</b>", body_style), Paragraph(employee_name, body_style),
         Paragraph("<b>Pay Period:</b>", body_style), Paragraph("Current Month", body_style)],
        [Paragraph("<b>Email Address:</b>", body_style), Paragraph(email, body_style),
         Paragraph("<b>Corporate Role:</b>", body_style), Paragraph(role, body_style)]
    ]
    emp_table = Table(emp_data, colWidths=[110, 160, 110, 150])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), accent_gray),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))

    # 3. Financial Calculations Ledger Breakdown Table
    story.append(Paragraph("Earnings & Deductions Summary", section_title))
    financial_data = [
        [Paragraph("Description", bold_body), Paragraph("Amount", bold_body)],
        [Paragraph("Gross Earnings Base Payout", body_style), Paragraph(f"R {gross:.2f}", body_style)],
        [Paragraph("Statutory Income Tax Withholding (20%)", body_style), Paragraph(f"- R {tax:.2f}", deduction_style)],
        [Paragraph("<b>Net Take-Home Pay</b>", bold_body), Paragraph(f"<b>R {net:.2f}</b>", bold_body)]
    ]
    fin_table = Table(financial_data, colWidths=[380, 150])
    fin_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, primary_color),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 3), (-1, 3), accent_gray),
        ('LINEABOVE', (0, 3), (-1, 3), 1, primary_color),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 40))

    # 4. Footer Legal Disclaimer
    story.append(Paragraph(
        "<font size=8 color=gray>This document is a confidential, automated payroll confirmation. If you find any data discrepancies, please notify your internal HR/Finance controller immediately.</font>",
        body_style))

    doc.build(story)
    return filename


def upload_to_s3(local_file, bucket, s3_file):
    """Streams the generated PDF file straight up to the AWS S3 cloud bucket."""
    s3 = boto3.client('s3')
    try:
        # ExtraArgs block removed to bypass explicit ACL policies restriction errors
        s3.upload_file(local_file, bucket, s3_file)
        print(f"Cloud Saved: s3://{bucket}/{s3_file}")
        return True
    except NoCredentialsError:
        print("❌ S3 Error: AWS Local Profile Credentials Not Found.")
        return False
    except Exception as e:
        print(f"S3 Upload Failure: {str(e)}")
        return False


def process_all_payroll_slips():
    """Queries all active calculation details and builds cloud assets."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Connects transactional pay ledger history data directly with employee metadata
        cur.execute("""
                    SELECT e.first_name, e.last_name, e.email, e.role, p.gross_pay, p.tax_deductions, p.net_pay
                    FROM pay_runs p
                             JOIN employees e ON p.employee_id = e.id;
                    """)
        records = cur.fetchall()

        if not records:
            print("Warning: No records found. Run payroll_processor.py first.")
            return

        print(f"\n--- Processing and Streaming {len(records)} Payslip Statements to S3 ---")

        for row in records:
            first, last, email, role, gross, tax, net = row
            full_name = f"{first} {last}"

            # 1. Compile the PDF asset using your template setup logic
            pdf_file = generate_employee_payslip(full_name, email, role, float(gross), float(tax), float(net))

            # 2. Upload asset into a structured cloud folder structure
            s3_path = f"2026/may/{pdf_file}"
            upload_to_s3(pdf_file, S3_BUCKET_NAME, s3_path)

            # 3. Clean up the temporary local file off your workspace disk
            if os.path.exists(pdf_file):
                os.remove(pdf_file)

        print("--- Document Deliverable Generation Cycle Complete! ---\n")

    except Exception as e:
        print(f"Core engine pipeline error: {str(e)}")
    finally:
        if cur: cur.close()
        if conn: conn.close()


if __name__ == "__main__":
    process_all_payroll_slips()
