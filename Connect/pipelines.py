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
        if spider.name == "baidu_hot":
            self.file = open("baidu_hot.json", "w", encoding="utf-8")
            # self.file.write("[\n")

    def close_spider(self, spider):
        if spider.name == "baidu_hot":
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
        if spider.name == "zgw":
            self.init_mysql()
        pass

    def close_spider(self, spider):
        if spider.name == "zgw":
            self.close_mysql()
        pass

    def process_item(self, item, spider):
        if spider.name == "zgw":
            self.insert_item(item)
        return item

    def init_mysql(self):
        self.mysql = pymysql.connect(host="localhost", user="root", password="@ne2Nine",
                                     database="wordpress", charset="utf8mb4")
        self.cursor = self.mysql.cursor()
        sql = """
            create table if not exists `spider_news`(
                `id` int not null auto_increment,
                `title` varchar(255) not null default "",
                `content` text,
                `author` varchar(255) not null default "",
                `source` varchar(255) not null default "",
                `pub_time` datetime not null,
                `url` text,
                `origin` varchar(255) not null default "",
                primary key(`id`)
            )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self.cursor.execute(sql)
        self.mysql.commit()

    def close_mysql(self):
        self.cursor.close()
        self.mysql.close()

    def insert_item(self, item):
        tmp_item = dict(item)
        sql0 = """
            select * from `spider_news` where title = '%s' and pub_time = '%s'
        """ % (tmp_item['title'], tmp_item['pub_time'])
        self.cursor.execute(sql0)
        exists = self.cursor.fetchone()
        if exists is None:
            sql = """
                insert into `spider_news`
                (title,content,author,source,pub_time,url,origin)
                values
                ('%s','%s','%s','%s','%s','%s','%s')
            """ % (tmp_item['title'], tmp_item['content'], tmp_item['author'], tmp_item['source'],
                   tmp_item['pub_time'], tmp_item['url'], tmp_item['origin'])
            self.cursor.execute(sql)
            self.mysql.commit()
