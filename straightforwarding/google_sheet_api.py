import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("StraightForwardingSpider").sheet1  # Open the spreadhseet


class Entry:

    def __init__(self, HB_No='', PO_No='', ETD='', ETA='', Shipper='', POL='', POD='',
                 Container_No='', Container_Info_Date='', Container_Info_Location='',
                 Container_Info_Location_Description='', Status='' ,Arrival_Date=''):
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
        
    def add_entry(self):
        sheet.append_row([self.HB_No,
                          self.PO_No,
                          self.ETD,
                          self.ETA,
                          self.Shipper,
                          self.POL,
                          self.POD,
                          self.Container_No,
                          self.Container_Info_Date,
                          self.Container_Info_Location,
                          self.Container_Info_Location_Description,
                          self.Status,
                          self.Arrival_Date
                          ])
        print('added')

    def update_entry(self, HB_No):
        cell_list = []
        # find the row to update
        row_look_up = sheet.find("{}".format(HB_No))
        headers = sheet.row_values(1)
        for header in headers:
            # find the column to update
            col_to_update = headers.index(header) + 1
            cell_to_update = sheet.cell(row_look_up.row, col_to_update)
            cell_to_update.value = getattr(self, header, '')
            cell_list.append(cell_to_update)




# test = Entry('TSGN4812597','CM-0442','12-10-2019','01-01-2020',
#         'VIETNAM YUZHAN PACKAGING TECHNOLOGY CO., LTD.',
#         'HAIPHONG','LONG BEACH', 'OOLU8950096','12-14-2019 07:27',
#         'Haiphong, Haiphong, Vietnam', 'Vessel Departed(Port of Load)' , 'Vessel Departed(Port of Load)')

#     test2 = Entry('update_succeed','CM-0442','12-10-2019','01-01-2020',
#             'VIETNAM YUZHAN PACKAGING TECHNOLOGY CO., LTD.',
#             'HAIPHONG','LONG BEACH', 'OOLU8950096','12-14-2019 07:27',
#             'Haiphong, Haiphong, Vietnam', 'Vessel Departed(Port of Load)' , 'Vessel Departed(Port of Load)')


# row = sheet.row_values(3)  # Get a specific row
# col = sheet.col_values(3)  # Get a specific column
# cell = sheet.cell(1,2).value  # Get the value of a specific cell

# insertRow = ["hello", 5, "red", "blue"]
# sheet.add_rows(insertRow, 4)  # Insert the list as a row at index 4

# sheet.update_cell(2,2, "CHANGED")  # Update one cell

# numRows = sheet.row_count  # Get the number of rows in the sheet
