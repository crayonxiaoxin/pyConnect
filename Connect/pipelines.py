# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql


# class ConnectPipeline(object):
#
#     def open_spider(self, spider):
#         if spider.name == "baidu_hot":
#             self.file = open("baidu_hot.json", "w", encoding="utf-8")
#             # self.file.write("[\n")
#
#     def close_spider(self, spider):
#         if spider.name == "baidu_hot":
#             # self.file.write("\n]")
#             self.file.close()
#
#     def process_item(self, item, spider):
#         if spider.name == "baidu_hot":
#             lines = json.dumps(dict(item), ensure_ascii=False) + ",\n"
#             self.file.write(lines)
#         return item


class MysqlPipeline(object):
    def open_spider(self, spider):
        self.init_mysql()

    def close_spider(self, spider):
        self.close_mysql()

    def process_item(self, item, spider):
        self.insert_item(item)
        return item

    def init_mysql(self):
        self.mysql = pymysql.connect(host="localhost", user="root", password="@ne2Nine",
                                     database="wordpress", charset="utf8mb4")
        self.cursor = self.mysql.cursor()
        sql = """
            CREATE TABLE if NOT EXISTS `spider_news`(
                `id` int NOT NULL AUTO_INCREMENT,
                `title` varchar(255) NOT NULL DEFAULT '',
                `content` text,
                `author` varchar(255) NOT NULL DEFAULT '',
                `source` varchar(255) NOT NULL DEFAULT '',
                `pub_time` datetime not null,
                `url` text,
                `origin` varchar(255) NOT NULL DEFAULT '',
                `datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(`id`)
            )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
        self.cursor.execute(sql)
        self.mysql.commit()

    def close_mysql(self):
        self.cursor.close()
        self.mysql.close()

    def insert_item(self, item):
        tmp_item = dict(item)
        sql0 = """
            SELECT * FROM `spider_news` WHERE title = '%s' AND pub_time = '%s'
        """ % (tmp_item['title'], tmp_item['pub_time'])
        self.cursor.execute(sql0)
        exists = self.cursor.fetchone()
        if exists is None:
            sql = """
                INSERT INTO `spider_news`
                (title,content,author,source,pub_time,url,origin)
                VALUES
                ('%s','%s','%s','%s','%s','%s','%s')
            """ % (tmp_item['title'], tmp_item['content'], tmp_item['author'], tmp_item['source'],
                   tmp_item['pub_time'], tmp_item['url'], tmp_item['origin'])
            res = self.cursor.execute(sql)
            self.mysql.commit()
            if res is not None and res is not False:
                print('已保存："%s"' % tmp_item['title'])
            else:
                print('保存失败："%s"' % tmp_item['title'])
        else:
            print('已存在，不保存："%s"' % tmp_item['title'])
