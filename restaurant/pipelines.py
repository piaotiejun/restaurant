# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem


class MeituanPipeline(object):
    def __init__(self):
        self.filter_dic = {}

    def process_item(self, item, spider):
        if self.filter_dic.get(item['restaurant_name']) == item['address']:
            print(item['restaurant_name'])
            print(item['address'])
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.filter_dic[item['restaurant_name']] = item['address']
            return item
