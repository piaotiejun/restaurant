# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem
from .utils.location import gaode_to_baidu


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
            try:
                item['lng'], item['lat'] = gaode_to_baidu(float(item['lng']), float(item['lat']))
            except BaseException as e:
                print(e)
            return item
