import gspread
import os
import random
from retrying import retry
from oauth2client.service_account import ServiceAccountCredentials

'''
Get creds from env vars, and then open the specifying sheet.
'''

def create_keyfile_dict():
    variables_keys = {
        "type": os.getenv("SHEET_TYPE"),
        "project_id": os.getenv("SHEET_PROJECT_ID"),
        "private_key_id": os.getenv("SHEET_PRIVATE_KEY_ID"),
        "private_key": os.getenv("SHEET_PRIVATE_KEY"),
        "client_email": os.getenv("SHEET_CLIENT_EMAIL"),
        "client_id": os.getenv("SHEET_CLIENT_ID"),
        "auth_uri": os.getenv("SHEET_AUTH_URI"),
        "token_uri": os.getenv("SHEET_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("SHEET_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("SHEET_CLIENT_X509_CERT_URL")
    }
    return variables_keys


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    create_keyfile_dict(), scope)

client = gspread.authorize(creds)

# Open the Production Sheet
# sheet = client.open("StraightForwardingSpider").worksheet("DataFromSF")

# Open the Production Sheet
sheet = client.open("DataSync").worksheet("StraightForwarding")


'''
Entry model for data from StraightForwarding correspoind to google sheet's columns.
'''

class Entry:

    def __init__(self, HB_No='', PO_No='', ETD='', ETA='', Shipper='', POL='', POD='',
                 Container_No='', Container_Info_Date='', Container_Info_Location='',
                 Container_Info_Location_Description='', Status='', Arrival_Date=''):
        self.HB_No = HB_No
        self.PO_No = PO_No
        self.ETD = ETD
        self.ETA = ETA
        self.Shipper = Shipper
        self.POL = POL
        self.POD = POD
        self.Container_No = Container_No
        self.Container_Info_Date = Container_Info_Date
        self.Container_Info_Location = Container_Info_Location
        self.Container_Info_Location_Description = Container_Info_Location_Description
        self.Status = Status
        self.Arrival_Date = Arrival_Date

    @retry(wait_fixed=110000)
    def add_entry(self):
        sheet.append_row(list(vars(self).values()))
        print('added: {}'.format(self.HB_No))

    @retry(wait_fixed=110000)
    def update_entry(self):
        # use HB_No to find the row to update
        col_headers = sheet.row_values(1)
        row_to_update = sheet.find("{}".format(self.HB_No)).row
        last_col_A1_notation = Entry.colnum_to_string(len(col_headers))
        cell_list = sheet.range('A{}:{}{}'.format(
            row_to_update, last_col_A1_notation, row_to_update))
        for i in range(len(col_headers)):
            cell_list[i].value = getattr(self, col_headers[i], '')
        sheet.update_cells(cell_list)

        print('updated: {}'.format(self.HB_No))

    @staticmethod
    def colnum_to_string(n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

