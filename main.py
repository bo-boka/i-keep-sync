from ikeepsafe import connect_ikeepsafe
from google_sheets import GoogleSheets
from analyze import analyze_new_data
import pandas as pd
import datetime
import traceback
from dotenv import load_dotenv
import os


def load_env_variables():
    """Load environment variables from the .env file."""
    load_dotenv()
    service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
    if not service_account_file:
        raise ValueError("SERVICE_ACCOUNT_FILE is not set in the .env file!")
    print(f"Using service account file: {service_account_file}")
    return service_account_file


def save_data_to_csv(dataframe, filename):
    """Save data to a CSV file."""
    try:
        dataframe.to_csv(filename, index=False, mode='x')  # mode='x' fails if the file exists
        print(f"Data saved to {filename}.")
    except FileExistsError:
        raise FileExistsError(f"File {filename} already exists for today. Set DEBUG to True to use existing file."
                              f"Run script again.")


def main():
    """
    Runs main functions.
    If DEBUG is set to False and scrape hasn't been executed for today, script will scrape and save new file to CSV and
        create new Google sheet with scraped data.
    If DEBUG is set to True and scrape has already been executed today, script will skip scraping and saving.
    If DEBUG is set to True and scrape hasn't been executed for today, an error is raised to save new data.
    If DEBUG is set to False and scrape has already been executed today, an error is raised to prevent saving again.
    TODO: Implement argparse, and move const configs to .env file.
    TODO: Add comparison logic of old & new scrapes to find changes.
    TODO: Complete analyze.py
    :return:
    """
    _SPREADSHEET_NAME = "iKeepSafe_products_data_01_2025"
    _SHEET_INDEX = 0
    _DEBUG = True

    try:
        service_account_file = load_env_variables()
        # Initialize Google Sheets integration
        gs = GoogleSheets(service_account_file, _SPREADSHEET_NAME)

        new_worksheet_name = "iKeepSafe_certs_" + datetime.datetime.now().strftime("%Y-%m-%d")
        csv_filename = "./data/" + new_worksheet_name + ".csv"

        # Scrape or load data
        if _DEBUG:
            print(f"Loading data from CSV: {csv_filename}")
            try:
                new_df = pd.read_csv(csv_filename)
            except FileNotFoundError:
                raise FileNotFoundError(f"Scrape/save has not been executed for today. {csv_filename} does not exist. "
                                        f"Set DEBUG to False and run script again.")
        else:
            new_data = connect_ikeepsafe()
            new_df = pd.DataFrame(new_data)
            save_data_to_csv(new_df, csv_filename)
            gs.create_write_sheet(new_worksheet_name, new_df)
            analyze_new_data(new_data)

        # Read old data from Google Sheet
        old_df = gs.read_sheet(_SHEET_INDEX)
        print("Old sheet data:", old_df.head())

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
