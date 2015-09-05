# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import (CrawlSpider, Rule)
from scrapy.http import Request
from scrapy.selector import Selector

from restaurant.items import MeituanItem


headers = {
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
"Cache-Control":"max-age=0",
"Host":"i.meituan.com",
"RA-Sid":"7C4125DE-20150519-013547-91bdb7-b00401",
"RA-Ver":"3.0.7",
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
}

city = 'weihai'
country = 'china'
province = 'shandong'

class MeituanSpider(CrawlSpider):
    name = 'meituan'
    allowed_domains = ['i.meituan.com']

    """美团url参数:
    :city: 城市拼音
    :cateType: cateType=poi 只有这个值
    :stid: stid=_b1 只有这个值
    :cid: cid=分类id poi分类 美食为1
    :bid: bid=商圈id
    :p: p=页数
    """
    start_urls = ['http://i.meituan.com/%s?cid=1&cateType=poi&stid=_b1'%city]

    rules = (
        #Rule(LinkExtractor(allow=r'http://i\.meituan\.com/poi/\d*?$'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        js = response.xpath('//script[@type="commment"]').extract()[0]
        data = re.search('\{[\s\S]*\}', js).group(0)
        data = json.loads(data)
        region_list = data['BizAreaList']
        category_list = data['CateList'][0]['subCategories']

        for category in category_list:
            if category['name'] == u'全部':
                continue
            for region in region_list:
                if region['name'] == u'全城':
                    continue
                for area in region['subareas']:
                    if area['name'] == u'全部':
                        continue
                    item = MeituanItem()
                    item['country'] = country
                    item['province'] = province
                    item['city'] = city
                    item['region'] = region['name'].strip()
                    item['area'] = area['name'].strip()
                    item['category'] = category['name'].strip()
                    url = 'http://i.meituan.com/%s?cid=%d&bid=%d&cateType=poi&stid=_b1'%(item['city'], category['id'], area['id'])

                    yield Request(url,
                            method='GET',
                            meta={'item': item, 'url': url},
                            headers=headers,
                            cookies=None,
                            body=None,
                            priority=0,
                            errback=None,
                            encoding=response.encoding,
                            callback=self.parse_category_area)


    def parse_category_area(self, response):
        item = response.meta['item']

        next_url = response.xpath('//a[@gaevent="imt/deal/list/pageNext"]/@data-page-num').extract()
        if next_url:
            next_url = ''.join([response.meta['url'], '&p=', str(next_url[0])])

            yield Request(next_url,
                    method='GET',
                    meta={'item': item, 'url': response.meta['url']},
                    headers=headers,
                    cookies=None,
                    body=None,
                    priority=0,
                    errback=None,
                    encoding=response.encoding,
                    callback=self.parse_category_area)

        restaurant_list = response.xpath('//dd[@class="poi-list-item"]').extract()
        for restaurant in restaurant_list:
            one_item = deepcopy(item)
            restaurant = Selector(text=restaurant)

            #url
            try:
                one_item['meituan_url'] = restaurant.xpath('//a/@href').extract()[0].strip()
            except BaseException as e:
                one_item['meituan_url'] = ''

            #restaurant_name
            try:
                one_item['restaurant_name'] = restaurant.xpath('//a/span[1]/text()').extract()[0].strip()
            except BaseException as e:
                continue

            #score
            try:
                one_item['score'] = restaurant.xpath('//a//em/text()').extract()[0].strip()
            except BaseException as e:
                one_item['score'] = '-1'

            yield Request(one_item['meituan_url'],
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

        #phoone
        try:
            item['phone'] = response.xpath('//a[@data-com="phonecall"]/@data-tele').extract()[0]
        except BaseException as e:
            item['phone'] = ''

        #meituan_logo_url
        meituan_logo_url = response.xpath('//div[@class="imgbox headimg"]/@data-src').extract()
        if meituan_logo_url:
            item['meituan_logo_url'] = meituan_logo_url[0].strip()
        else:
            item['meituan_logo_url'] = ''

        #brief
        summary = response.xpath('//dd[@class="dd-padding kv-line"]').extract()
        item['brief'] = {}
        for s in summary:
            s = Selector(text=s)
            k = s.xpath('//h6/text()').extract()[0].strip()
            v = "".join([w.strip() for w in s.xpath('//p/text()').extract()])
            item['brief'][k] = v

        #comment
        comment = response.xpath('//div[@class="feedbackCard"]').extract()
        item['comment'] = {}
        for c in comment:
            c = Selector(text=c)
            name = c.xpath('//weak[@class="username"]/text()').extract()[0].strip()
            time = c.xpath('//weak[@class="time"]/text()').extract()[0].strip()
            word = "".join([w.strip() for w in c.xpath('//div[@class="comment"]//text()').extract()])
            item['comment'][name] = [time, word]

        #address
        try:
            item['address'] = response.xpath('//div[@class="kv-line-r"]/h6/a/text()').extract()[0].strip()
        except BaseException as e:
            item['address'] = ''

        gaode_url = response.xpath('//div[@class="kv-line-r"]/h6/a/@href').extract()[0]

        yield Request(gaode_url,
                method='GET',
                meta={'item': item},
                headers=headers,
                cookies=None,
                body=None,
                priority=0,
                errback=None,
                encoding=response.encoding,
                callback=self.parase_gaode_address)

    def parase_gaode_address(self, response):
        item = response.meta['item']

        #lat & lng
        item['lat'], item['lng'] = response.xpath('//a[@class="btn kv-v"]/@href').extract()[0].split('(')[0].split('=')[-1].split(',')

        return item
