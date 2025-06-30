import pandas as pd

def analyze_csv(file):
    df = pd.read_csv(file)
    report = {}

    report["df"] = df
    report["Shape"] = df.shape
    report["Null Values"] = df.isnull().sum().to_dict()
    report["Descriptive Stats"] = df.describe(include='all').to_html(classes="styled-table")
    report["Correlation"] = df.corr(numeric_only=True).to_html(classes="styled-table")

    return report
