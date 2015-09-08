# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem
import pinyin


from .utils.location import gaode_to_baidu


class MeituanPipeline(object):
    def __init__(self):
        self.filter_dic = {}

    def process_item(self, item, spider):
        if spider.name not in ['meituan']:
            return item
        if self.filter_dic.get(item['restaurant_name']) == item['address']:
            print(item['restaurant_name'])
            print(item['address'])
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.filter_dic[item['restaurant_name']] = item['address']
            try:
                item['lng'], item['lat'] = gaode_to_baidu(float(item['lng']), float(item['lat']))
                item['province_code'] = pinyin.get(item['province'])
                item['city_code'] = pinyin.get(item['city'])
                item['region_code'] = pinyin.get(item['region'])
                item['area_code'] = pinyin.get(item['area'])
            except BaseException as e:
                print(e)
            return item


class DianpingPipeline(object):
    def __init__(self):
        self.filter_dic = {}

    def process_item(self, item, spider):
        if spider.name not in ['dazhongdianping']:
            return item

        # restaurant_name
        if len(item['restaurant_name']) != 1:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            item['restaurant_name'] = item['restaurant_name'][0]

        if self.filter_dic.get(item['restaurant_name']) == item['address']:
            print(item['restaurant_name'])
            print(item['address'])
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.filter_dic[item['restaurant_name']] = item['address']

        # lng lat
        # item['lng'], item['lat'] = gaode_to_baidu(float(item['lng']), float(item['lat']))

        # logo url
        if len(item['dianping_logo_url']) != 1:
            item['dianping_logo_url'] = ''
        else:
            item['dianping_logo_url'] = item['dianping_logo_url'][0].strip()

        # address
        if len(item['address']) != 1:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            item['address'] = item['address'][0].strip()

        # phone
        if len(item['phone']) == 0:
            item['phone'] = ''
        else:
            item['phone'] = ','.join(item['address'])

        # score
        if len(item['score']) == 0:
            item['score'] = '-1'
        else:
            item['score'] = item['score'][0].split('str')[-1]

        return item




