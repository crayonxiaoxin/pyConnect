# -*- coding: utf-8 -*-
import scrapy

from Connect.items import ConnectItem


class BaiduHotSpider(scrapy.Spider):
    name = 'baidu_hot'
    allowed_domains = ['baidu.com', 'cn.bing.com']
    start_urls = ['https://top.baidu.com/board?tab=realtime']

    def parse(self, response, **kwargs):
        elements = response.xpath('//div[contains(@class,"category-wrap_")]')
        elements = [elements[0]]
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
            # yield item
            yield scrapy.Request(url="https://cn.bing.com/search?q=%s" % item['title'], callback=self.parse_from_bing,
                                 cb_kwargs={"item": item}, encoding="utf-8", cookies=None)

    def parse_from_bing(self, response, item):
        print(response.text)
        # print(item)
        url = response.xpath(
            '//ol[@id="b_results"]/li/div[contains(@class,"b_title")]/h2[contains(string(),"中青在线")]/a/@href').get()
        print(url)
        # yield response.cb_kwargs

# Bing => https://cn.bing.com/search?q=
# //ol[@id="b_results"]/li/div[contains(@class,"b_title")]/h2[contains(string(),"_中国网")]

# 中国网
# //div[@id="articleBody"]/p    # web版
# //div[contains(@class,"d_img")]   # m版
