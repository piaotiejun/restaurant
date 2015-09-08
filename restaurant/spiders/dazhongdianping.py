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

big_city_xx_cnt = 0
small_city_xx_cnt = 0
restaurant_cnt = 0

class DazhongdianpingSpider(CrawlSpider):
    name = 'dazhongdianping'
    allowed_domains = ['www.dianping.com']
    start_urls = ['http://www.www.dianping.com/citylist']
    #download_delay = 1 # 下载间隔

    rules = (
        #Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        city_cnt = 0
        big_city_list = response.xpath('//ul[@id="divArea"]/li[1]/div/a/strong/text()').extract()
        big_city_code_list = response.xpath('//ul[@id="divArea"]/li[1]/div/a/@href').extract()
        for index, city in enumerate(big_city_list):
            item = DazhongdianpingItem()
            item['province'] = ''
            item['province_code'] = ''
            item['city_code'] = big_city_code_list[index]
            item['city'] = city
            url = 'http://www.dianping.com' + item['city_code'] + '/food'

            city_cnt += 1
            print('大城市数量:\t'+str(city_cnt))
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

        city_cnt = 0
        province_list = response.xpath('//li[@class="root"]//dl[@class="terms"]').extract()
        for province in province_list:
            province = Selector(text=province)
            city_list = province.xpath('//strong/text()').extract()
            city_code_list = province.xpath('//a/@href').extract()
            for index, city in enumerate(city_list):
                item = DazhongdianpingItem()
                item['province'] = province.xpath('//dt/text()').extract()[0]
                item['province_code'] = pinyin.get(item['province']).strip()
                item['city'] = city.strip()
                item['city_code'] = city_code_list[index].strip('\r\n\t/ ')
                url = 'http://www.dianping.com' + item['city_code'] + '/food'

                city_cnt += 1
                print('小城市数量:\t'+str(city_cnt))
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
        is_big_city = False if len(response.xpath('//div[@class="block-title"]/h1/text()').extract()) > 0 else True
        if is_big_city:
            for request in self.parse_big_city(response):
                yield request
        else:
            for request in self.parse_small_city(response):
                yield request


    def parse_big_city(self, response):
        item = response.meta['item']
        request_list = []
        url_set = set()

        #category
        category_id_list = response.xpath('//div[@class="secondary-category J-secondary-category"]/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_head_guangzhou_food_fenlei")]/@href').extract()
        category_list = response.xpath('//div[@class="secondary-category J-secondary-category"]/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_head_guangzhou_food_fenlei")]/text()').extract()

        #area
        js = re.search('<script class="J_auto-load" type="text/plain">([\s\S]*?)</script>', response.body).group(1)
        data = Selector(text=js)
        region_data = data.xpath('//div[@class="fpp_business"]//dl').extract()
        for region in region_data:
            region_html = Selector(text=region)
            region = region_html.xpath('//dt/a/text()').extract()[0].strip('[]\n\r\t ')

            area_list = region_html.xpath('//li/a/text()').extract()
            area_url_list = region_html.xpath('//li/a/@href').extract()
            for area_index, area in enumerate(area_list):
                for cate_index, category in enumerate(category_list):
                    one_item = deepcopy(item)
                    one_item['category'] = category.strip()
                    one_item['region'] = region
                    one_item['region_code'] = pinyin.get(one_item['region'])
                    one_item['area'] = area.strip()
                    one_item['area_code'] = pinyin.get(one_item['area'])

                    url = "".join(['http://www.dianping.com', area_url_list[area_index], 'g', category_id_list[cate_index]])
                    print('大城市分类商圈url:')
                    print(url)
                    if url not in url_set:
                        url_set.add(url)
                    else:
                        continue
                    global big_city_xx_cnt
                    big_city_xx_cnt += 1
                    print('大城市商圈分类url数量:\t'+str(big_city_xx_cnt))
                    request_list.append(Request(url,
                                                method='GET',
                                                meta={'item': one_item},
                                                headers=headers,
                                                cookies=None,
                                                body=None,
                                                priority=0,
                                                errback=None,
                                                encoding=response.encoding,
                                                callback=self.parse_restaurant_list))

        return request_list


    def parse_small_city(self, response):
        item = response.meta['item']
        request_list = []
        url_set = set()

        #category
        category_url_list = response.xpath('//li[@class="term-list-item"]//ul[@class="desc Fix"]//li/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_home_food_hotdaohang_fenlei")]/@href').extract()
        category_list = response.xpath('//li[@class="term-list-item"]//ul[@class="desc Fix"]//li/a[starts-with(@onclick, "pageTracker._trackPageview(\'dp_home_food_hotdaohang_fenlei")]/text()').extract()

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
                    one_item['category'] = category.strip()
                    one_item['region'] = region.strip()
                    one_item['region_code'] = pinyin.get(one_item['region'])
                    one_item['area'] = area.strip()
                    one_item['area_code'] = pinyin.get(one_item['area'])
                    url = "".join(['http://www.dianping.com', category_url_list[cate_index], 'r', area_id_list[area_index]])
                    print('小城市饭店分类商圈 url:')
                    print(url)
                    if url not in url_set:
                        url_set.add(url)
                    else:
                        continue
                    global small_city_xx_cnt
                    small_city_xx_cnt += 1
                    print('大城市商圈分类url数量:\t'+str(small_city_xx_cnt))
                    request_list.append(Request(url,
                                                method='GET',
                                                meta={'item': one_item},
                                                headers=headers,
                                                cookies=None,
                                                body=None,
                                                priority=0,
                                                errback=None,
                                                encoding=response.encoding,
                                                callback=self.parse_restaurant_list))

        return request_list


    def parse_restaurant_list(self, response):
        item = response.meta['item']

        # 处理下一页
        next_url = response.xpath('//a[@class="next"]/@href').extract()
        if next_url:
            next_url = 'http://www.dianping.com' + next_url[0]
            one_item = deepcopy(item)

            yield Request(next_url,
                    method='GET',
                    meta={'item': one_item},
                    headers=headers,
                    cookies=None,
                    body=None,
                    priority=0,
                    errback=None,
                    encoding=response.encoding,
                    callback=self.parse_restaurant_list)

        # 处理饭店列表
        restaurant_list = response.xpath('//div[@class="shop-list J_shop-list shop-all-list"]/ul/li').extract()
        for restaurant in restaurant_list:
            restaurant = Selector(text=restaurant)
            one_item = deepcopy(item)
            one_item['restaurant_name'] = restaurant.xpath('//img/@title').extract()
            one_item['dianping_logo_url'] = restaurant.xpath('//img/@title').extract()
            one_item['address'] = restaurant.xpath('//span[@class="addr"]/text()').extract()
            url = restaurant.xpath('//a[@rel="nofollow"]/@href').extract()
            url = 'http://www.dianping.com' + url[0].strip()
            one_item['dianping_url'] = url
            print('饭店详情页url')
            print(url)
            global restaurant_cnt
            restaurant_cnt += 1
            print('饭店数量:\t'+str(restaurant_cnt))

            # 跳转到饭店详情页
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

        item['phone'] = response.xpath('//p[@class="expand-info tel"]/span[@class="item"]/text()').extract()
        item['score'] = response.xpath('//div[@class="brief-info"]/span[1]/@class').extract() # mid-rank-stars mid-str30
        r = re.search('\{lng:(.*?),lat:(.*?)\}', response.body)
        item['lng'] = r.group(1)
        item['lat'] = r.group(2)
        item['comment'] = '' # 没用

        return item
