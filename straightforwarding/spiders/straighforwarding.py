# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy.http import FormRequest
from ..items import StraightforwardingItem
from datetime import datetime


class StraightForwardingSpider(scrapy.Spider):
    name = 'straightforwarding'
    allowed_domains = ['tracking.straightforwardinginc.com']

    BASE_URL_LIST = 'https://tracking.straightforwardinginc.com'
    BASE_URL_SPECIFIC = 'https://tracking.straightforwardinginc.com/shipment/'

    def start_requests(self):
        return [scrapy.Request("https://tracking.straightforwardinginc.com/login/",
                               callback=self.logged_in)]

    def logged_in(self, response):
        token = response.xpath(
            '//input[@name="csrfmiddlewaretoken"]/@value').get()
        return FormRequest.from_response(response, formdata={
            'csrfmiddlewaretoken': token,
            'next': '/',
            'username': os.getenv('USERNAME'),
            'password': os.getenv('PASSWORD'),
        }, callback=self.redir_after_login)

    def redir_after_login(self, response):
        if response.url == 'https://tracking.straightforwardinginc.com/':
            print('login succeeded')
            now = datetime.now()
            begin_date = '11-01-2019'
            year = now.year + 1
            end_date = now.strftime("%m-%d") + '-{}'.format(year)
            links_url = 'https://tracking.straightforwardinginc.com/search/?adv=1&type=I&begin_date=' + \
                begin_date + '&end_date=' + end_date + '&pol=&pod=&show_finished=1'
            return scrapy.Request(links_url, callback=self.parse_links)
        else:
            print('login failed')

    def parse_links(self, response):
        items = StraightforwardingItem()

        for row in response.xpath('//tr[starts-with(@class, "single_shipment_row")]'):
            # PO_No_from_list = row.xpath('./td[3]/text()').getall()
            Status = row.xpath('./td[10]/@uib-tooltip-html').get()

            # items['PO_No_from_list'] = PO_No_from_list
            # items['Status'] = " ".join(Status.split('\'')[1].split('<br>'))

            link = self.BASE_URL_SPECIFIC + row.xpath('./@data-hbl').get()
            yield scrapy.Request(link,
                                 callback=self.start_scraping,
                                 cb_kwargs=dict(Status=Status))

        # links = response.xpath('//tr/@data-hbl').getall()
        # for link in links:
        #     absolute_url = self.BASE_URL_SPECIFIC + link
        #     yield scrapy.Request(absolute_url, callback=self.start_scraping)

        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()

        if next_page is not None:
            next_page = self.BASE_URL_LIST + next_page
            yield response.follow(next_page, callback=self.parse_links)

    def start_scraping(self, response, Status):
        items = StraightforwardingItem()

        HB_No = response.xpath(
            '//table[contains(@class, "shipment_info")]//tr[1]/td[1]/text()').get()
        PO_No = response.xpath('//td[@class="colspan7"]/text()').getall()
        ETD = response.xpath('//tr[2]/td[3]/text()').get()
        ETA = response.xpath('//tr[2]/td[2]/text()').get()
        Shipper = response.xpath('//td[@colspan="3"]/text()').get()
        POL = response.xpath('//tr[1]/td[3]/text()').get()
        POD = response.xpath('//tr[1]/td[2]/text()').get()
        Container_No = response.xpath(
            '//table[@id="container_info_table"]//tr[1]/td[2]/div/text()').get()
        Container_Info_Date = response.xpath(
            '//table[@id="container_info_table"]//tr[1]/td[4]/text()').get()
        Container_Info_Location = response.xpath(
            '//table[@id="container_info_table"]//tr[1]/td[3]/text()').get()
        Container_Info_Location_Description = response.xpath(
            '//table[@id="container_info_table"]//tr[1]/td[5]/text()').get()

        items['Status'] = " ".join(Status.split('\'')[1].split('<br>'))
        items['HB_No'] = HB_No
        items['PO_No'] = PO_No
        items['ETD'] = ETD
        items['ETA'] = ETA
        items['Shipper'] = Shipper
        items['POL'] = POL
        items['POD'] = POD
        items['Container_No'] = Container_No
        items['Container_Info_Date'] = Container_Info_Date
        items['Container_Info_Location'] = Container_Info_Location
        items['Container_Info_Location_Description'] = Container_Info_Location_Description

        yield items
