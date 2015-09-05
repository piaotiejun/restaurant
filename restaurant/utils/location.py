# coding=utf8

import math

pi = 3.14159265358979324


def gaode_to_baidu(gaode_lng, gaode_lat):
    """高德地图坐标到百度地图坐标的转换
    :param gaode_lng: {float} 高德地图经度
    :param gaode_lat: {float} 高德地图纬度
    :return: {(float, float)} 百度地图经纬度元组
    """
    z = math.sqrt(pow(gaode_lng, 2) + pow(gaode_lat, 2)) + 0.00002 * math.sin(gaode_lat*pi)
    theta = math.atan2(gaode_lat, gaode_lng) + 0.000003 * math.cos(gaode_lng*pi)
    #baidu_lng = z * math.cos(theta) + 0.0065
    #baidu_lat = z * math.sin(theta) + 0.006
    baidu_lng = z * math.cos(theta) + 0.00657
    baidu_lat = z * math.sin(theta) + 0.0058

    return (baidu_lng, baidu_lat)

if __name__ == "__main__":
    print(gaode_to_baidu(122.136819,37.486766))
