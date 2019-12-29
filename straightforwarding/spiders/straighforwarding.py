# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy.http import FormRequest
from ..items import StraightforwardingItem
from datetime import datetime
from scrapy_splash import SplashRequest


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
            begin_date = os.getenv('BEGIN_DATE')
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

            Status = row.xpath('./td[10]/@uib-tooltip-html').get()

            link = self.BASE_URL_SPECIFIC + row.xpath('./@data-hbl').get()
            yield SplashRequest(link,
                                callback=self.start_scraping,
                                args={'wait': 1},
                                cb_kwargs=dict(Status=Status))

        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()

        if next_page is not None:
            next_page = self.BASE_URL_LIST + next_page
            yield response.follow(next_page, callback=self.parse_links)

    def start_scraping(self, response, Status):
        items = StraightforwardingItem()

        HB_No = response.xpath(
            '//table[contains(@class, "shipment_info")]//tr[1]/td[1]/text()').get()
        PO_No = response.xpath('//td[@class="colspan7"]/text()').get()
        ATD_ETD_ng_if = response.xpath(
            '(//li[contains(@class, "vessel-info") and contains(@class,"ng-scope")])[1]/@ng-if').get()
        if ATD_ETD_ng_if.startswith('!'):
            ATD_ETD = response.xpath(
                '(//li[contains(@class, "vessel-info") and contains(@class,"ng-scope")])[1]/text()')\
                .get().strip()
        else:
            ATD_ETD = response.xpath(
                '(//a[contains(@class, "vessel-info-btn")])[1]/text()').get().strip()

        ATA_ETA = response.xpath(
            '//span[contains(@class, "ng-binding") and contains(@class, "ng-scope")]/text()').get().strip()

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
        items['ATD_ETD'] = ATD_ETD
        items['ATA_ETA'] = ATA_ETA
        items['Shipper'] = Shipper
        items['POL'] = POL
        items['POD'] = POD
        items['Container_No'] = Container_No
        items['Container_Info_Date'] = Container_Info_Date
        items['Container_Info_Location'] = Container_Info_Location
        items['Container_Info_Location_Description'] = Container_Info_Location_Description

        yield items
