# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GuaziScrapyItem(scrapy.Item):
    #定义collection用于创建数据库表
    collection = 'guazi_car'
    #汽车唯一id，用于去重
    car_id = scrapy.Field()
    car_name = scrapy.Field()
    #网页原始url
    from_url = scrapy.Field()
    car_price = scrapy.Field()
    # 许可证时间（上牌时间）
    license_time = scrapy.Field()
    km_info = scrapy.Field()
    #许可证位置（上牌地点）
    license_location = scrapy.Field()
    #排量信息
    desplacement_info =  scrapy.Field()
    #变速箱，手动还是自动
    transmission_case = scrapy.Field()

