import pandas as pd


def analyze_new_data(data):
    data = pd.DataFrame(data)
    print(data.head(10))
    print("Dataframe Row Count", len(data))

    # Count products by certification
    certification_summary = data[["FERPA", "COPPA", "CSPC", "ATLIS"]].sum()
    certification_summary["Total"] = certification_summary.sum()
    print(certification_summary)

