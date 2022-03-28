# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

import pymysql
from scrapy.pipelines.images import ImagesPipeline


class ConnectPipeline(object):

    def open_spider(self, spider):
        self.file = open("baidu_hot.json", "w", encoding="utf-8")
        # self.file.write("[\n")

    def close_spider(self, spider):
        # self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        if spider.name == "baidu_hot":
            lines = json.dumps(dict(item), ensure_ascii=False) + ",\n"
            self.file.write(lines)
        return item


class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        filename = "baidu_hot/%s.jpg" % item['title']
        return filename


class MysqlPipeline(object):
    def open_spider(self, spider):
        self.mysql = pymysql.connect(host="localhost", port=8080, user="root", password="@ne2Nine",
                                     database="wordpress")
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if spider.name == "baidu_hot":
            pass
        return item
