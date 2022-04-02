# -*- coding: utf-8 -*-
import html
import random

import scrapy

from Connect.items import BaiduHotItem, NewsItem, StatusItem


def get_url_xpath_from_normal(name):
    return '//div[contains(@class,"c-row")]/*[contains(string(),"%s")]/ancestor::div[contains(@class,"c-container")]/descendant::h3[contains(@class,"tts-title")]/a/@href' % name


def get_url_xpath_from_group(name):
    return '//div[contains(@class,"group-content_")]/*[contains(string(),"%s")]/parent::div/a[contains(@class,"tts-title")]/@href' % name


def random_bd_url(wd):
    return 'https://www.baidu.com/s?wd=%s&inputT=%d' % (wd, random.randint(500, 4000))


site_names = ["中华网", "中国网", "东北网", "新浪网", "新浪新闻", "搜狐网"]


class BaiduHotSpider(scrapy.Spider):
    name = 'baidu_hot'
    allowed_domains = ['baidu.com', 'china.com.cn', 'china.com', 'dbw.cn', 'sohu.com', 'sina.com.cn', 'hixin.cc',
                       'thekonnect.cn']
    start_urls = ['https://top.baidu.com/board?tab=realtime']

    # url 规则
    china_com_cn = "china.com.cn/"
    china_com = "china.com/"
    dbw_cn = "dbw.cn/"
    sohu_com = "sohu.com/a/"
    sina_com_cn = "sina.com.cn/"

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
                if link is not None:
                    yield item
                    yield scrapy.Request(random_bd_url(item['title']), callback=self.parse_s_wd,
                                         cb_kwargs={"item": item})
                else:
                    yield from self.not_support_parse(item['title'], "没有找到链接", response.request.headers)

    def not_support_parse(self, title, desc="", url="", headers=None):
        status_item = StatusItem()
        if url.find("//wappass.baidu.com/") != -1:
            desc += "，跳百度安全验证"
        elif url == "https://www.baidu.com/":
            desc += "，百度强制重定向"
        if headers is not None:
            head = html.escape(str(headers))
        status_item['status_title'] = title
        status_item['status_desc'] = desc
        status_item['status_url'] = url
        status_item['status_headers'] = url
        yield status_item

    def parse_s_wd(self, response, item):
        url = ""
        for site_name in site_names:
            group_rule = get_url_xpath_from_group(site_name)
            normal_rule = get_url_xpath_from_normal(site_name)
            group_urls = response.xpath(group_rule).getall()
            normal_urls = response.xpath(normal_rule).getall()
            if len(group_urls) > 0:
                url = group_urls[0]
                print("xpath规则：%s" % group_rule)
                print(group_urls)
                print("符合规则的链接：%s" % url)
                break
            elif len(normal_urls) > 0:
                url = normal_urls[0]
                print("xpath规则：%s" % normal_rule)
                print(normal_urls)
                print("符合规则的链接：%s" % url)
                break

        if url != "":
            # # 中国网
            # if url.find(self.china_com_cn) != -1:
            #     yield from self.parse_china_com_cn(response, url, item)
            # # 中华网
            # elif url.find(self.china_com) != -1:
            #     yield from self.parse_china_com(response, url, item)
            # # 东北网
            # elif url.find(self.dbw_cn) != -1:
            #     yield from self.parse_dbw_cn(response, url, item)
            # # 搜狐网
            # elif url.find(self.sohu_com) != -1:
            #     yield from self.parse_sohu_com(response, url, item)
            # else:
            yield scrapy.Request(url, callback=self.parse_bd, cb_kwargs={"origin_url": url, "item": item})
        else:
            print("链接不在规则列表中：%s" % url)
            print("百度搜索链接：%s" % response.url)
            yield from self.not_support_parse(item['title'], "链接不在规则列表中", response.url, response.request.headers)

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
        # 新浪网
        elif url.find(self.sina_com_cn) != -1:
            yield from self.parse_sina_com_cn(response, url, item)
        # 搜狐网
        elif url.find(self.sohu_com) != -1:
            yield from self.parse_sohu_com(response, url, item)
        else:
            print("不支持爬取：%s" % url)
            yield from self.not_support_parse(item['title'], "链接不在规则列表中", url, response.request.headers)

    # 中国网
    def parse_china_com_cn(self, response, url, hot_item):
        # http://news.china.com.cn/2022-03/29/content_78135389.htm
        title = response.xpath('//h1[@class="articleTitle"]/text()').get()
        # http://henan.china.com.cn/m/2022-03/29/content_41919531.html
        title_mobile = response.xpath('//div[contains(@class,"d_title")]/text()').get()
        # http://zjnews.china.com.cn/yuanchuan/2022-04-02/334005.html
        title_zjnews = response.xpath('//div[contains(@class,"zuoce")]/div[@class="title"]/text()').get()
        if title is not None:
            yield from self.parse_china_com_cn_web(response, title, url, hot_item)
        elif title_mobile is not None:
            yield from self.parse_china_com_cn_mobile(response, title_mobile, url, hot_item)
        elif title_zjnews is not None:
            yield from self.parse_china_com_cn_zjnews(response, title_zjnews, url, hot_item)
        else:
            yield from self.not_support_parse(hot_item['title'], "中国网: 未支持该链接", url, response.request.headers)

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
        else:
            yield from self.not_support_parse(hot_item['title'], "中国网: 未支持该链接", url, response.request.headers)

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
        else:
            yield from self.not_support_parse(hot_item['title'], "中国网: 未支持该链接", url, response.request.headers)

    # 中国网 - web zjnews
    def parse_china_com_cn_zjnews(self, response, title, url, hot_item):
        item = NewsItem()
        item['hot_title'] = hot_item['title']
        item['title'] = title
        content = response.xpath('//div[contains(@class,"pimg")]').get()
        rexian = response.xpath('//p[contains(@class,"rexian")]').get()
        laiyuan = response.xpath('//p[contains(@class,"laiYuan")]').get()
        if rexian is None or rexian == "":
            content = content.replace(rexian, '')
        if laiyuan is None or laiyuan == "":
            content = content.replace(laiyuan, '')
        item['content'] = html.escape(str(content))
        pubtime = response.xpath('//div[contains(@class,"issue")]/text()').get()
        if pubtime is not None:
            pubtime = pubtime.replace('发布时间', '').replace('&nbsp;', '').strip()
        else:
            pubtime = ""
        item['pub_time'] = pubtime
        source = response.xpath('//div[contains(@class,"issue")]/span[contains(@class,"username")]/text()').get()
        if source is not None:
            source = source.replace('&nbsp;', '').replace('·  |', '').strip()
        else:
            source = ""
        item['source'] = source
        item['author'] = ""
        item['url'] = url
        item['origin'] = "中国网"
        if content is not None:
            yield item
        else:
            yield from self.not_support_parse(hot_item['title'], "中国网: 未支持该链接", url, response.request.headers)

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
        else:
            yield from self.not_support_parse(hot_item['title'], "中华网: 未支持该链接", url, response.request.headers)

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
            else:
                yield from self.not_support_parse(hot_item['title'], "东北网: 未支持该链接", url, response.request.headers)

    # 搜狐网
    def parse_sohu_com(self, response, url, hot_item):
        title = response.xpath('string(//div[@class="text-title"]/h1/text())').get()
        if title is not None:
            item = NewsItem()
            item['hot_title'] = hot_item['title']
            item['title'] = title.replace('\n', "").replace('\t', "").strip()
            content = response.xpath('//article').get()
            backsouhu = response.xpath('//a[@id="backsohucom"]').get()
            if content is not None and backsouhu is not None:
                content = content.replace(backsouhu, "")
            item['content'] = html.escape(str(content))
            pubtime = response.xpath('//span[@id="news-time"]/text()').get()
            if pubtime is not None:
                pubtime = pubtime.strip()
            else:
                pubtime = ""
            item['pub_time'] = pubtime
            author_source = response.xpath('//div[@id="user-info"]/h4/a/text()').get()
            if author_source is not None:
                author = source = author_source
            else:
                author = source = ""
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "搜狐网"
            yield item
        else:
            yield from self.not_support_parse(hot_item['title'], "搜狐网: 未支持该链接", url, response.request.headers)

    # 新浪网 新浪新闻
    def parse_sina_com_cn(self, response, url, hot_item):
        title = response.xpath('//h1[@class="main-title"]/text()').get()
        if title is not None:
            item = NewsItem()
            item['hot_title'] = hot_item['title']
            item['title'] = title
            content = response.xpath('//div[@id="article"]').get()
            sina_notice = response.xpath('//div[@class="article-notice"]').get()
            if content is not None and sina_notice is not None:
                content = content.replace(sina_notice, "")
            wap_special = response.xpath('//div[@class="wap_special"]').get()
            if content is not None and wap_special is not None:
                content = content.replace(wap_special, "")
            item['content'] = html.escape(str(content))
            pubtime = response.xpath('//div[@class="date-source"]/span[@class="date"]/text()').get()
            if pubtime is not None:
                pubtime = pubtime.strip().replace('年', '-').replace('月', '-').replace('日', '-')
                pubtime += ":00"
            else:
                pubtime = ""
            item['pub_time'] = pubtime
            source = response.xpath('//div[@class="date-source"]/a[contains(@class,"source")]/text()').get()
            if source is None:
                source = ""
            author = response.xpath('//div[@class="date-source"]/span[contains(@class,"author")]/a/text()').get()
            if author is None:
                author = ""
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "新浪网"
            yield item
        else:
            yield from self.not_support_parse(hot_item['title'], "新浪网: 未支持该链接", url, response.request.headers)
