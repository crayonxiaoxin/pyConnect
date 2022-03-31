# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql


class MysqlPipeline(object):

    def open_spider(self, spider):
        self.init_mysql(spider)

    def close_spider(self, spider):
        self.close_mysql()

    def process_item(self, item, spider):
        if spider.name == "baidu_hot":
            self.insert_baidu_hot_item(item)
        else:
            self.insert_item(item)
        return item

    def init_mysql(self, spider):
        self.mysql = pymysql.connect(host="localhost", user="root", password="@ne2Nine",
                                     database="wordpress", charset="utf8mb4")
        self.cursor = self.mysql.cursor()
        if spider.name == "baidu_hot":
            sql = """
                CREATE TABLE if NOT EXISTS `spider_baidu_hot`(
                    `id` int NOT NULL AUTO_INCREMENT,
                    `title` varchar(255) NOT NULL DEFAULT '',
                    `content` text,
                    `image` text,
                    `url` text,
                    `hot_num` int NOT NULL DEFAULT 0,
                    `datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(`id`)
                )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
        else:
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
                    `hot_title` varchar(255) NOT NULL DEFAULT '',
                    `datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(`id`)
                )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
        self.cursor.execute(sql)
        self.mysql.commit()

        # 每次清空
        if spider.name == "baidu_hot":
            sql_del = "TRUNCATE TABLE `spider_baidu_hot`"
            self.cursor.execute(sql_del)
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
            hot_title = ""
            hot_id = item['hot_id']
            if hot_id is not None and str(hot_id).isnumeric() and int(hot_id) > 0:
                sql_hot = """
                SELECT * FROM `spider_baidu_hot` WHERE id = %d
                """ % (int(hot_id))
                self.cursor.execute(sql_hot)
                hot_row = self.cursor.fetchone()
                if hot_row is not None and hot_row is not False:
                    hot_title = hot_row[1]

            sql = """
                INSERT INTO `spider_news`
                (title,content,author,source,pub_time,url,origin,hot_title)
                VALUES
                ('%s','%s','%s','%s','%s','%s','%s','%s')
            """ % (tmp_item['title'], tmp_item['content'], tmp_item['author'], tmp_item['source'],
                   tmp_item['pub_time'], tmp_item['url'], tmp_item['origin'], hot_title)
            res = self.cursor.execute(sql)
            self.mysql.commit()
            if res is not None and res is not False:
                print('已保存："%s"' % tmp_item['title'])
            else:
                print('保存失败："%s"' % tmp_item['title'])
        else:
            print('已存在，不保存："%s"' % tmp_item['title'])

    def insert_baidu_hot_item(self, item):
        tmp_item = dict(item)
        sql0 = """
            SELECT * FROM `spider_baidu_hot` WHERE title = '%s'
        """ % (tmp_item['title'])
        self.cursor.execute(sql0)
        exists = self.cursor.fetchone()
        if exists is None:
            sql = """
                INSERT INTO `spider_baidu_hot`
                (title,content,image,url,hot_num)
                VALUES
                ('%s','%s','%s','%s','%d')
            """ % (tmp_item['title'], tmp_item['desc'], tmp_item['img_url'], tmp_item['link'], tmp_item['hot_num'])
            res = self.cursor.execute(sql)
            self.mysql.commit()
            if res is not None and res is not False:
                print('已保存："%s"' % tmp_item['title'])
            else:
                print('保存失败："%s"' % tmp_item['title'])
        else:
            print('已存在，不保存："%s"' % tmp_item['title'])
