# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import Request
import pinyin

from restaurant.items import DazhongdianpingItem


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Cache-Control": "max-age=0",
    "Host": "www.dianping.com",
    "HTTPS": "1",
    "RA-Sid": "7C4125DE-20150519-013547-91bdb7-b00401",
    "RA-Ver": "3.0.7",
    "Referer": "http://www.dianping.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36"
}


class DazhongdianpingSpider(CrawlSpider):
    name = 'dazhongdianping'
    allowed_domains = ['www.dianping.com']
    start_urls = ['http://www.www.dianping.com/citylist']

    rules = (
        #Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        province_list = response.xpath('//li[@class="root"]//dl[@class="terms"]').extract()
        for province in province_list:
            province = Selector(text=province)
            city_list = province.xpath('//strong/text()').extract()
            city_code_list = province.xpath('//a/@href').extract()
            for index, city in enumerate(city_list):
                print(city)
                item = DazhongdianpingItem()
                item['province'] = province.xpath('//dt/text()').extract()[0]
                item['province_code'] = pinyin.get(item['province'])
                item['city'] = city
                item['city_code'] = city_code_list[index]
                url = 'http://www.dianping.com' + item['city_code'] + 'food'

                yield Request(url,
                        method='GET',
                        meta={'item': item},
                        headers=headers,
                        cookies=None,
                        body=None,
                        priority=0,
                        errback=None,
                        encoding=response.encoding,
                        callback=self.parse_city)


    def parse_city(self, response):
        item = response.meta['item']
        
        url_set = set()

        #category
        #category_url_list = response.xpath('//li[@class="term-list-item"]//ul[@class="desc Fix"]//li/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_home_food_hotdaohang_fenlei")]/@href').extract()
        #category_list = response.xpath('//li[@class="term-list-item"]//ul[@class="desc Fix"]//li/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_home_food_hotdaohang_fenlei")]/text()').extract()
        category_list = response.xpath('//div[@class="pop-panel ep_quick-search ep_quick-search-styles Fix"]//a/text()').extract()
        category_id_list = response.xpath('//div[@class="pop-panel ep_quick-search ep_quick-search-styles Fix"]//a/@data-value').extract()

        #area
        region_data = response.xpath('//div[@class="pop-panel ep_quick-search ep_quick-search-regions Fix"]/div[@class="dp-option-wrap"]/dl').extract()
        for region in region_data:
            region_html = Selector(text=region)
            region_id = region_html.xpath('//dt/a/@data-value').extract()[0].strip()
            region = region_html.xpath('//dt/a/strong/text()').extract()[0].strip('[]\n\r\t ')

            area_list = region_html.xpath('//ul/li/a/text()').extract()
            area_id_list = region_html.xpath('//ul/li/a/@data-value').extract()
            for area_index, area in enumerate(area_list):
                for cate_index, category in enumerate(category_list):
                    one_item = deepcopy(item)
                    one_item['category'] = category
                    one_item['region'] = region
                    one_item['area'] = area
                    url = "".join([response.url, '/', 'g', category_id_list[cate_index], 'r', area_id_list[area_index]])
                    print(url)
                    if url not in url_set:
                        url_set.add(url)
                    else:
                        continue

                    yield Request(url,
                            method='GET',
                            meta={'item': one_item},
                            headers=headers,
                            cookies=None,
                            body=None,
                            priority=0,
                            errback=None,
                            encoding=response.encoding,
                            callback=self.parse_restaurant)


    def parse_restaurant(self, response):
        item = response.meta['item']
        return item









