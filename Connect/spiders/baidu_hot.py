# -*- coding: utf-8 -*-
import html
import random

import scrapy

from Connect.items import BaiduHotItem, NewsItem


def get_url_xpath_from_normal(name):
    return '//div[contains(@class,"c-row")]/*[contains(string(),"%s")]/ancestor::div[contains(@class,"c-container")]/descendant::h3[contains(@class,"tts-title")]/a/@href' % name


def get_url_xpath_from_group(name):
    return '//div[contains(@class,"group-content_")]/*[contains(string(),"%s")]/parent::div/a[contains(@class,"tts-title")]/@href' % name


def random_bd_url(wd):
    return 'https://www.baidu.com/s?wd=%s&inputT=%d' % (wd, random.randint(500, 4000))


site_names = ["中华网", "中国网", "东北网"]


class BaiduHotSpider(scrapy.Spider):
    name = 'baidu_hot'
    allowed_domains = ['baidu.com', 'china.com.cn', 'china.com', 'dbw.cn', 'hixin.cc', 'thekonnect.cn']
    start_urls = ['https://top.baidu.com/board?tab=realtime']

    custom_settings = {
        'DOWNLOAD_DELAY': 5
    }

    # url 规则
    china_com_cn = "china.com.cn/"
    china_com = "//news.china.com/"
    dbw_cn = "dbw.cn/"

    dbw_cn_origin = ["finance.dbw.cn", "house.dbw.cn", "legal.dbw.cn", "internal.dbw.cn", "international.dbw.cn",
                     "story.dbw.cn",
                     "heilongjiang.dbw.cn", "edu.dbw.cn", "health.dbw.cn", "tour.dbw.cn", "ms.dbw.cn", "society.dbw.cn",
                     "sports.dbw.cn", "entertainment.dbw.cn", "tv.dbw.cn"]
    dbw_cn_redirect = ["m.dbw.cn/caijing", "m.dbw.cn/fangchan", "m.dbw.cn/fazhi", "m.dbw.cn/guonei", "m.dbw.cn/guoji",
                       "m.dbw.cn/harbin", "m.dbw.cn/heilongjiang", "m.dbw.cn/jiaoyu", "m.dbw.cn/jiankang",
                       "m.dbw.cn/lvyou",
                       "m.dbw.cn/minsheng", "m.dbw.cn/shehui", "m.dbw.cn/tiyu", "m.dbw.cn/yule", "m.dbw.cn/sppd"]

    def parse(self, response, **kwargs):
        elements = response.xpath('//div[contains(@class,"category-wrap_")]')
        if elements is not None:
            for i in range(0, 10):
                element = elements[i]
                item = BaiduHotItem()
                link = element.xpath('./a/@href').get()
                item['link'] = link
                item['img_url'] = element.xpath('./a/img/@src').get()
                item['image_urls'] = [item['img_url']]
                title = element.xpath('string(./div[contains(@class,"content_")]/a/div)').get()
                item['title'] = title.strip()
                desc = element.xpath(
                    './div[contains(@class,"content_")]/div[contains(@class,"hot-desc_")]/text()').get()
                item['desc'] = desc.strip()
                hot_num = element.xpath(
                    './div[contains(@class,"trend_")]/div[contains(@class,"hot-index_")]/text()').get()
                hot_num = str(hot_num).strip()
                if hot_num == "":
                    hot_num = "0"
                item['hot_num'] = int(hot_num)
                if link is not None and i == 1:
                    yield item
                    yield scrapy.Request(random_bd_url(item['title']), callback=self.parse_s_wd,
                                         cb_kwargs={"item": item})

    def parse_s_wd(self, response, item):
        url = ""
        for site_name in site_names:
            group_urls = response.xpath(get_url_xpath_from_group(site_name)).getall()
            normal_urls = response.xpath(get_url_xpath_from_normal(site_name)).getall()
            if len(group_urls) > 0:
                url = group_urls[0]
                break
            elif len(normal_urls) > 0:
                url = normal_urls[0]
                break
        print("符合规则的链接：%s" % url)
        if url != "":
            # 中国网
            if url.find(self.china_com_cn) != -1:
                yield from self.parse_china_com_cn(response, url, item)
            # 中华网
            elif url.find(self.china_com) != -1:
                yield from self.parse_china_com(response, url, item)
            # 东北网
            elif url.find(self.dbw_cn) != -1:
                yield from self.parse_dbw_cn(response, url, item)
            else:
                # print("不支持爬取：%s" % url)
                yield scrapy.Request(url, callback=self.parse_bd, cb_kwargs={"origin_url": url, "item": item})

    def parse_bd(self, response, origin_url, item):
        url = response.url
        # 中国网
        if url.find(self.china_com_cn) != -1:
            yield from self.parse_china_com_cn(response, url, item)
        # 中华网
        elif url.find(self.china_com) != -1:
            yield from self.parse_china_com(response, url, item)
        # 东北网
        elif url.find(self.dbw_cn) != -1:
            yield from self.parse_dbw_cn(response, url, item)
        else:
            print("不支持爬取：%s" % url)

    # 中国网
    def parse_china_com_cn(self, response, url, hot_item):
        # http://news.china.com.cn/2022-03/29/content_78135389.htm
        title = response.xpath('//h1[@class="articleTitle"]/text()').get()
        # http://henan.china.com.cn/m/2022-03/29/content_41919531.html
        title_mobile = response.xpath('//div[contains(@class,"d_title")]/text()').get()
        if title is not None:
            yield from self.parse_china_com_cn_web(response, title, url, hot_item)
        elif title_mobile is not None:
            yield from self.parse_china_com_cn_mobile(response, title_mobile, url, hot_item)

    # 中国网 - mobile
    def parse_china_com_cn_mobile(self, response, title_mobile, url, hot_item):
        item = NewsItem()
        item['hot_title'] = hot_item['title']
        item['title'] = title_mobile
        content = response.xpath('//div[contains(@class,"d_img")]').get()
        item['content'] = html.escape(str(content))
        pubtime = response.xpath('//div[contains(@class,"d_time")]/span/text()').get()
        if pubtime is not None:
            pubtime = pubtime.strip()
        else:
            pubtime = ""
        item['pub_time'] = pubtime
        source = response.xpath('//div[contains(@class,"d_time")]/text()').get()
        if source is not None:
            source = source.strip().replace('来源：', '')
        else:
            source = ""
        item['pub_time'] = pubtime
        item['source'] = source
        item['author'] = ""
        item['url'] = url
        item['origin'] = "中国网"
        if content is not None:
            yield item

    # 中国网 - web
    def parse_china_com_cn_web(self, response, title, url, hot_item):
        item = NewsItem()
        item['hot_title'] = hot_item['title']
        item['title'] = title
        content = response.xpath('//div[@id="articleBody"]').get()
        video = response.xpath('string(//div[@id="videoarea"])').get()
        video_element = response.xpath('//div[@id="videoarea"]').get()
        if video is None or video == "":
            content = content.replace(video_element, '')
        item['content'] = html.escape(str(content))
        pubtime = response.xpath('//span[@id="pubtime_baidu"]/text()').get()
        if pubtime is None:
            pubtime = response.xpath('//div[contains(@class,"articleInfo")]/div[1]/text()').get()
        if pubtime is not None:
            pubtime = pubtime.replace('发布时间：', '')
        else:
            pubtime = ""
        item['pub_time'] = pubtime
        item['source'] = response.xpath('//span[@id="source_baidu"]/a/text()').get()
        author = response.xpath('//span[@id="author_baidu"]/text()').get()
        if author is not None:
            author = author.replace('作者：', '')
        else:
            author = ""
        item['author'] = author
        item['url'] = url
        item['origin'] = "中国网"
        if content is not None:
            yield item

    # 中华网
    def parse_china_com(self, response, url, hot_item):
        # https://news.china.com/socialgd/10000169/20220327/41785167.html
        title_type1 = response.xpath('//h1[@id="chan_newsTitle"]/text()').get()
        # https://news.china.com/domestic/945/20220330/41811858.html
        title_type2 = response.xpath('//h1[contains(@class,"article_title")]/text()').get()
        if title_type1 is not None:
            yield from self.parse_china_com_type_1(response, title_type1, url, hot_item)
        elif title_type2 is not None:
            yield from self.parse_china_com_type_2(response, title_type2, url, hot_item)

    # 中华网 - 类型1
    def parse_china_com_type_1(self, response, title_type1, url, hot_item):
        item = NewsItem()
        item['hot_title'] = hot_item['title']
        item['title'] = title_type1
        content = response.xpath('//div[@id="chan_newsDetail"]').get()
        item['content'] = html.escape(str(content))
        pubtime = response.xpath('//div[@id="chan_newsInfo"]/text()[3]').get()
        if pubtime is not None:
            pubtime = pubtime.strip().replace("&nbsp;", "")
        else:
            pubtime = ""
        item['pub_time'] = pubtime
        source = response.xpath('string(//span[@class="chan_newsInfo_source"])').get()
        if source is not None:
            source = source.strip()
        else:
            source = ""
        item['source'] = source.strip()
        author = response.xpath('string(//span[@class="chan_newsInfo_author"])').get()
        if author is not None:
            author = author.strip()
        else:
            author = ""
        item['author'] = author
        item['url'] = url
        item['origin'] = "中华网"
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_1, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            # print(item)
            yield item

    # 中华网 - 正文分页 - 类型1
    def parse_china_com_next_1(self, response, item):
        content = response.xpath('//div[@id="chan_newsDetail"]').get()
        if content is not None:
            item['content'] += html.escape(str(content))
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_1, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            # print(item)
            yield item

    # 中华网 - 类型2
    def parse_china_com_type_2(self, response, title_type1, url, hot_item):
        item = NewsItem()
        item['hot_title'] = hot_item['title']
        item['title'] = title_type1
        content = response.xpath('//div[contains(@class,"article_content")]').get()
        item['content'] = html.escape(str(content))
        pubtime = response.xpath('//div[contains(@class,"article_info")]/span[@class="time"]/text()').get()
        if pubtime is not None:
            pubtime = pubtime.strip().replace("&nbsp;", "")
        else:
            pubtime = ""
        item['pub_time'] = pubtime
        source = response.xpath('//div[contains(@class,"article_info")]/span[@class="source"]/a/text()').get()
        if source is not None:
            source = source.strip()
        else:
            source = ""
        item['source'] = source
        item['author'] = ""
        item['url'] = url
        item['origin'] = "中华网"
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_2, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            # print(item)
            yield item

    # 中华网 - 正文分页 - 类型2
    def parse_china_com_next_2(self, response, item):
        content = response.xpath('//div[contains(@class,"article_content")]').get()
        if content is not None:
            item['content'] += html.escape(str(content))
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_2, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            # print(item)
            yield item

    def dbw_url_redirect(self, url):
        if url.find(self.dbw_cn) != -1:
            for i in range(len(self.dbw_cn_origin)):
                o_u = self.dbw_cn_origin[i]
                if url.find(o_u) != -1:
                    url = url.replace(o_u, self.dbw_cn_redirect[i])
                    return url
            pass
        return None

    # 东北网
    def parse_dbw_cn(self, response, url, hot_item):
        redirect = self.dbw_url_redirect(response.request.url)
        if redirect is not None:
            yield scrapy.Request(redirect, callback=self.parse_dbw_cn, cb_kwargs={"url": url, "hot_item": hot_item})
        else:
            title = response.xpath('//div[@id="end-box"]/h1[1]/text()').get()
            if title is not None:
                item = NewsItem()
                item['hot_title'] = hot_item['title']
                item['title'] = title
                content = response.xpath('//div[@class="zhengw"]').get()
                item['content'] = html.escape(str(content))
                pubtime = response.xpath('//div[@class="time"]/text()[1]').get()
                if pubtime is not None:
                    pubtime = pubtime.strip()
                else:
                    pubtime = ""
                item['pub_time'] = pubtime
                author_source = response.xpath('//span[@class="rl"]/text()').get()
                if author_source is not None:
                    author_source = str(author_source).split(" 　")
                    if len(author_source) == 2:
                        author = author_source[0].replace("编辑：", "")
                        source = author_source[1].replace("来源：", "")
                    else:
                        author = ""
                        source = ""
                else:
                    author = ""
                    source = ""
                item['author'] = author
                item['source'] = source
                item['url'] = url
                item['origin'] = "东北网"
                yield item
