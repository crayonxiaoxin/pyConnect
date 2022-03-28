# -*- coding: utf-8 -*-
import scrapy

from Connect.items import ConnectItem


class BaiduHotSpider(scrapy.Spider):
    name = 'baidu_hot'
    allowed_domains = ['baidu.com']
    start_urls = ['https://top.baidu.com/board?tab=realtime']

    def parse(self, response, **kwargs):
        elements = response.xpath('//div[contains(@class,"category-wrap_")]')
        for element in elements:
            item = ConnectItem()
            item['link'] = element.xpath('./a/@href').get()
            item['img_url'] = element.xpath('./a/img/@src').get()
            item['image_urls'] = [item['img_url']]
            title = element.xpath('string(./div[contains(@class,"content_")]/a/div)').get()
            item['title'] = title.strip()
            desc = element.xpath(
                './div[contains(@class,"content_")]/div[contains(@class,"hot-desc_")]/text()').get()
            item['desc'] = desc.strip()
            hot_num = element.xpath(
                './div[contains(@class,"trend_")]/div[contains(@class,"hot-index_")]/text()').get()
            item['hot_num'] = str(hot_num).strip()
            yield item
