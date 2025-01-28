from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread


class GoogleSheets:
    """
    Google Sheets integration using Google Sheets API functionality.
    """
    def __init__(self, credentials_file, spreadsheet_name, sheet_index=None):
        """
        Instantiates Google Sheet. Sheet index optional on instantiation, but if not provided, then it's required upon
        method calls.
        Future Note: Added .open() to .authenticate() for gs property. May need to undo if authentication obj is
        needed later.
        :param credentials_file: (string) Path to Google service account json file
        :param spreadsheet_name: (string) Name of Google Sheets spreadsheet
        :param sheet_index: (int) (optional) Index number of sheet in spreadsheet.
        """
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.sheet_index = self._validate_index(sheet_index)
        self.gs = self.authenticate().open(spreadsheet_name)

    def _validate_index(self, value):
        """
        Validates that index provided is an int type.
        :param value: (int) sheet index number
        :return: int value or TypeError exception.
        """
        if value is None:
            return value
        if type(value) == int:
            return value
        else:
            raise TypeError("Sheet Index provided is not an integer: "+value)

    def authenticate(self):
        """
        Authenticates connection, assuming scopes, Google Sheets API and Google Drive API, are enabled.
        :return:
        """
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, SCOPES)
        return gspread.authorize(credentials)

    def get_spreadsheet(self):
        """
        Gets specific Google Spreadsheet using name provided upon instantiation.
        :return: (object) spreadsheet
        """
        return self.gs

    def get_sheet(self, sheet_idx):
        """
        Gets sheet from spreadsheet based on index number either provided on class instantiation or in method call.
        Prioritizes sheet number used in method call. If none provided, uses class index attribute.
        If neither are given, a ValueError is raised.
        If index number given doesn't exist, IndexError is raised.
        :param sheet_idx: (int) index number of the preferred sheet in spreadsheet.
        :return: (object) sheet from spreadsheet
        """
        s_idx = self._validate_index(sheet_idx) if sheet_idx is not None else self.sheet_index
        if s_idx is None:
            raise ValueError("Missing sheet index arg on get_sheet() method call or GoogleSheets class initialization.")

        # return self.get_spreadsheet().get_worksheet(s_idx)
        return self.gs.get_worksheet(s_idx)

    def read_sheet(self, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        data = sheet.get_all_records()
        return pd.DataFrame(data)

    def create_write_sheet(self, title, dataframe):
        """
        Creates a new worksheet in the spreadsheet and writes to it.
        :param title: (string) Name of new worksheet
        :param dataframe: (obj) pandas dataframe to write to new sheet
        :return:
        """
        if type(title) is not str:
            raise TypeError("Worksheet title is not a string: " + title)
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("New worksheet data is not a Pandas Dataframe")
        worksheet = self.gs.add_worksheet(title=title, rows=100, cols=20)
        worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        print("New Worksheet created: " + title)

    def write_sheet(self, dataframe, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    def append_row(self, row, sheet_idx=None):
        sheet = self.get_sheet(sheet_idx)
        sheet.append_row(row)
