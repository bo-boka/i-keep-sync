from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread


class GoogleSheets:
    def __init__(self, credentials_file, spreadsheet_name, sheet_index=None):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.sheet_index = self._validate_index(sheet_index)
        self.gc = self.authenticate()

    def _validate_index(self, value):
        if value is None:
            return value
        if type(value) == int:
            return value
        else:
            raise TypeError("Sheet Index provided is not an integer: "+value)

    def authenticate(self):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, SCOPES)
        return gspread.authorize(credentials)

    def get_spreadsheet(self):
        return self.gc.open(self.spreadsheet_name)

    def get_sheet(self, sheet_idx):
        if sheet_idx is not None:
            return self.get_spreadsheet().get_worksheet(self._validate_index(sheet_idx))
        if self.sheet_index is not None:
            return self.get_spreadsheet().get_worksheet(self.sheet_index)
        else:
            raise ValueError("Missing sheet index arg on get_sheet() method call or GoogleSheets class initialization.")

    def read_sheet(self, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        data = sheet.get_all_records()
        return pd.DataFrame(data)

    def write_sheet(self, dataframe, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    def append_row(self, row, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        sheet.append_row(row)
