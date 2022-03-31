# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduHotItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
    img_url = scrapy.Field()
    hot_num = scrapy.Field()
    image_urls = scrapy.Field()


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    pub_time = scrapy.Field()
    source = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    origin = scrapy.Field()
    hot_id = scrapy.Field()
