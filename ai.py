def generate_ai_insights(df):
    insights = []

    insights.append(f"Total Rows: {len(df)}")
    insights.append(f"Total Columns: {len(df.columns)}")

    nulls = df.isnull().sum()
    missing = nulls[nulls > 0]

    if not missing.empty:
        insights.append(
            "Columns with null values: "
            + ", ".join(missing.index)
        )

    numeric = df.select_dtypes(include="number")

    if not numeric.empty:
        insights.append(
            "Numeric columns: "
            + ", ".join(numeric.columns)
        )

    return insights