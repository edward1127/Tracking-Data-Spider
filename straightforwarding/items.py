# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StraightforwardingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    Status = scrapy.Field()
    HB_No = scrapy.Field()
    PO_No = scrapy.Field()
    ATD_ETD = scrapy.Field()
    ATA_ETA = scrapy.Field()
    Shipper = scrapy.Field()
    POL = scrapy.Field()
    POD = scrapy.Field()
    Container_No = scrapy.Field()
    Container_Info_Date = scrapy.Field()
    Container_Info_Location = scrapy.Field()
    Container_Info_Location_Description = scrapy.Field()
