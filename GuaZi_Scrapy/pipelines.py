# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from GuaZi_Scrapy.handle_mongo import mongo_data

class SaveMongoDB(object):
    def process_item(self, item, spider):
        mongo_data.save_data(item)
        return item