from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "CSV Analyzer Report", border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(report, email):
    pdf = PDFReport()
    pdf.add_page()

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"User: {email}", ln=True)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)


    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Data Shape:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, str(report["Shape"]), ln=True)
    pdf.ln(5)


    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Null Values:", ln=True)
    pdf.set_font("Arial", "", 10)
    for col, val in report["Null Values"].items():
        pdf.cell(0, 8, f"{col}: {val}", ln=True)
    pdf.ln(5)


    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Descriptive Statistics:", ln=True)
    pdf.set_font("Arial", "", 8)

  
    try:
        desc_df = report["df"].describe(include='all')
        desc_str = desc_df.round(3).to_string()
        for line in desc_str.split('\n'):
            pdf.cell(0, 6, line, ln=True)
    except Exception as e:
        pdf.cell(0, 8, f"Error generating stats: {e}", ln=True)
    pdf.ln(5)


    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Correlation Matrix:", ln=True)
    pdf.set_font("Arial", "", 8)
    try:
        corr_df = report["df"].corr(numeric_only=True).round(3)
        corr_str = corr_df.to_string()
        for line in corr_str.split('\n'):
            pdf.cell(0, 6, line, ln=True)
    except Exception as e:
        pdf.cell(0, 8, f"Error generating correlation: {e}", ln=True)


    return pdf.output(dest='S').encode('latin1')
