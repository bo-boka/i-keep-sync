from ikeepsafe import connect_ikeepsafe
from google_sheets import GoogleSheets
import pandas as pd
import datetime
import traceback
from dotenv import load_dotenv
import os


def main():
    """
    TODO: grab today's date for to_csv() file name & add count suffix for exception statement
    :return:
    """
    try:

        spreadsheet_name = "iKeepSafe_products_data_01_2025"
        sheet_idx = 0

        new_worksheet_name = "iKeepSafe_certs_" + datetime.datetime.now().strftime("%Y-%m-%d")
        new_data = connect_ikeepsafe()
        new_df = pd.DataFrame(new_data)

        try:
            new_df.to_csv("./data/" + new_worksheet_name + ".csv", index=False, mode='x')  # mode x fails if file exists
        except FileExistsError:
            print("File already exists.")

        # Results
        print(new_df.head(10))
        print("Dataframe Row Count", len(new_df))

        # Count products by certification
        certification_summary = new_df[["FERPA", "COPPA", "CSPC", "ATLIS"]].sum()
        certification_summary["Total"] = certification_summary.sum()
        print(certification_summary)

        # Load environment variables from the .env file
        load_dotenv()
        # Get the path to the service account JSON from the environment
        service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
        # Verify the path (optional)
        if not service_account_file:
            raise ValueError("SERVICE_ACCOUNT_FILE is not set in the .env file!")
        print(f"Using service account file: {service_account_file}")

        # Initialize Google Sheets integration
        gs = GoogleSheets(service_account_file, spreadsheet_name)

        # Read data from Google Sheet
        old_df = gs.read_sheet(sheet_idx)
        print("Old sheet data:", old_df.head())
        # Create new sheet
        gs.create_write_sheet(new_worksheet_name, new_df)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
