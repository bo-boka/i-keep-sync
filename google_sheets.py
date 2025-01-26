from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread


class GoogleSheets:
    def __init__(self, credentials_file, sheet_name):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.gc = self.authenticate()

    def authenticate(self):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, SCOPES)
        return gspread.authorize(credentials)

    def get_sheet(self):
        return self.gc.open(self.sheet_name).sheet1

    def read_sheet(self):
        sheet = self.get_sheet()
        data = sheet.get_all_records()
        return pd.DataFrame(data)

    def write_sheet(self, dataframe):
        sheet = self.get_sheet()
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    def append_row(self, row):
        sheet = self.get_sheet()
        sheet.append_row(row)
