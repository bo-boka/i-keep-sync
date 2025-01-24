from ikeepsafe import connect_ikeepsafe
import pandas as pd
import traceback


def main():
    """
    TODO: grab today's date for to_csv() file name & add count suffix for exception statement
    :return:
    """
    try:
        new_data = connect_ikeepsafe()

        df = pd.DataFrame(new_data)
        try:
            df.to_csv("./data/iKeepSafe_certs_01_23_2025.csv", index=False, mode='x')  # mode x fails if file exists
        except FileExistsError:
            # df.to_csv('unique_name.csv')
            print("File already exists.")

        # Results
        print(df.head(10))
        print("Dataframe Row Count", len(df))

        # Count products by certification
        certification_summary = df[["FERPA", "COPPA", "CSPC", "ATLIS"]].sum()
        certification_summary["Total"] = certification_summary.sum()
        print(certification_summary)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
