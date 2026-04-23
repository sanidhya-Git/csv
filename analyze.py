import pandas as pd

def analyze_csv(file):
    try:
        df = pd.read_csv(file)
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="latin1")
    except Exception as e:
        raise Exception(f"CSV read error: {e}")

    report = {}

    report["df"] = df
    report["Shape"] = df.shape
    report["Null Values"] = df.isnull().sum().to_dict()
    report["Descriptive Stats"] = df.describe(include='all').fillna("").to_html(classes="styled-table")
    report["Correlation"] = df.corr(numeric_only=True).fillna(0).to_html(classes="styled-table")

    return report