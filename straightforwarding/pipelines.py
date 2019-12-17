import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from straightforwarding.google_sheet_api import Entry
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("StraightForwardingSpider").sheet1  # Open the spreadhseet


class StraightforwardingPipeline(object):
    def process_item(self, item, spider):
        new_entry = Entry(HB_No=item['HB_No'],
                          PO_No=json.dumps(item['PO_No']),
                          ETD=item['ETD'],
                          ETA=item['ETA'],
                          Shipper=item['Shipper'],
                          POL=item['POL'],
                          POD=item['POD'],
                          Container_No=item['Container_No'],
                          Container_Info_Date=item['Container_Info_Date'],
                          Container_Info_Location=item['Container_Info_Location'],
                          Container_Info_Location_Description=item['Container_Info_Location_Description'],
                          Status=item['Status'])

        if new_entry.Container_Info_Location_Description == 'Container Returned to Carrier(Destination)' or \
                new_entry.Container_Info_Location_Description == 'Empty Container Returned from Customer' or\
                new_entry.Container_Info_Location_Description == 'Container to consignee' or\
                new_entry.Container_Info_Location_Description == 'Empty Equipment Returned':
            new_entry.Arrival_Date = new_entry.Container_Info_Date
            
        if bool(sheet.findall(new_entry.HB_No)):
            new_entry.update_entry
        else:
            new_entry.add_entry()
