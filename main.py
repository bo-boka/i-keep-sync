from ikeepsafe import connect_ikeepsafe
from google_sheets import GoogleSheets
import traceback
from dotenv import load_dotenv
import os


def main():
    """
    TODO: grab today's date for to_csv() file name & add count suffix for exception statement
    :return:
    """
    try:
        '''
        new_data = connect_ikeepsafe()

        df = pd.DataFrame(new_data)

        try:
            df.to_csv("./data/iKeepSafe_certs_01_23_2025.csv", index=False, mode='x')  # mode x fails if file exists
        except FileExistsError:
            # df.to_csv('unique_name.csv')
            
        # Results
        print(df.head(10))
        print("Dataframe Row Count", len(df))

        # Count products by certification
        certification_summary = df[["FERPA", "COPPA", "CSPC", "ATLIS"]].sum()
        certification_summary["Total"] = certification_summary.sum()
        print(certification_summary)
            print("File already exists.")
        '''

        # Load environment variables from the .env file
        load_dotenv()
        # Get the path to the service account JSON from the environment
        service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")

        # Verify the path (optional)
        if not service_account_file:
            raise ValueError("SERVICE_ACCOUNT_FILE is not set in the .env file!")
        print(f"Using service account file: {service_account_file}")

        sheet_name = "iKeepSafe_products_data_01_2025"
        # Initialize Google Sheets integration
        gs = GoogleSheets(service_account_file, sheet_name)

        # Read data from Google Sheets
        df = gs.read_sheet()
        print(df)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
