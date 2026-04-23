from fpdf import FPDF
from datetime import datetime
import pandas as pd


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "CSV Analyzer Report", border=0, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def add_section_title(pdf, title):
    pdf.set_font("Arial", "B", 12)
    pdf.ln(3)
    pdf.cell(0, 10, title, ln=True)


def add_text_line(pdf, text, font_size=10):
    pdf.set_font("Arial", "", font_size)
    pdf.multi_cell(0, 7, str(text))


def add_dataframe_to_pdf(pdf, df, font_size=7):
    pdf.set_font("Courier", "", font_size)

    text = df.to_string()

    for line in text.split("\n"):
        if pdf.get_y() > 270:
            pdf.add_page()
            pdf.set_font("Courier", "", font_size)

        pdf.multi_cell(0, 5, line)


def generate_pdf(report, email):
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # User Info
    add_section_title(pdf, "User Information")
    add_text_line(pdf, f"User: {email}")
    add_text_line(
        pdf,
        f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Shape
    add_section_title(pdf, "Dataset Shape")
    add_text_line(pdf, f"Rows, Columns: {report['Shape']}")

    # Null Values
    add_section_title(pdf, "Null Values")
    null_values = report["Null Values"]

    if null_values:
        for col, val in null_values.items():
            add_text_line(pdf, f"{col}: {val}")
    else:
        add_text_line(pdf, "No null values found.")

    # Descriptive Statistics
    add_section_title(pdf, "Descriptive Statistics")

    try:
        desc_df = report["df"].describe(include="all").fillna("").round(3)
        add_dataframe_to_pdf(pdf, desc_df)
    except Exception as e:
        add_text_line(pdf, f"Unable to generate stats: {e}")

    # Correlation Matrix
    add_section_title(pdf, "Correlation Matrix")

    try:
        corr_df = report["df"].corr(numeric_only=True).fillna(0).round(3)

        if corr_df.empty:
            add_text_line(pdf, "No numeric columns found.")
        else:
            add_dataframe_to_pdf(pdf, corr_df)

    except Exception as e:
        add_text_line(pdf, f"Unable to generate correlation: {e}")

    # Column Names
    add_section_title(pdf, "Column Names")

    try:
        cols = ", ".join(report["df"].columns.tolist())
        add_text_line(pdf, cols)
    except Exception:
        add_text_line(pdf, "Unable to fetch columns.")

    return pdf.output(dest="S").encode("latin1")