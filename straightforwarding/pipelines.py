import json
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from straightforwarding.google_sheet_api import Entry, sheet
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


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
            new_entry.update_entry(new_entry.HB_No)
        else:
            new_entry.add_entry()
