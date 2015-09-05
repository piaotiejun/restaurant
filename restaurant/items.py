# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeituanItem(scrapy.Item):
    restaurant_name = scrapy.Field()
    phone = scrapy.Field()
    address = scrapy.Field()
    score = scrapy.Field()
    brief = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()
    meituan_url = scrapy.Field()
    meituan_logo_url = scrapy.Field()
    comment = scrapy.Field()

    country = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    area = scrapy.Field()
    category = scrapy.Field()
