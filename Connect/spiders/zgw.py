import scrapy
import json

from Connect.items import NewsItem


class ZgwSpider(scrapy.Spider):
    name = 'zgw'
    allowed_domains = ['china.com.cn', 'china.com', 'dbw.cn', 'hixin.cc']
    start_urls = ['https://hixin.cc/testing']

    def parse(self, response, **kwargs):
        result = json.loads(response.text)
        urls = result['urls']
        print(urls)
        for url in urls:
            # 中国网
            if url.find("//news.china.com.cn/") != -1:
                yield scrapy.Request(url, callback=self.parse_china_com_cn, cookies=None, cb_kwargs={"url": url})
            # 中华网
            if url.find("//news.china.com/") != -1:
                yield scrapy.Request(url, callback=self.parse_china_com, cookies=None, cb_kwargs={"url": url})
            # 东北网
            if url.find("//m.dbw.cn/") != -1:
                yield scrapy.Request(url, callback=self.parse_dbw_cn, cookies=None, cb_kwargs={"url": url})

    # 中国网
    def parse_china_com_cn(self, response, url):
        # http://news.china.com.cn/2022-03/29/content_78135389.htm
        title = response.xpath('//h1[@class="articleTitle"]/text()').get()
        if title is not None:
            content = response.xpath('//div[@id="articleBody"]').get()
            pubtime = response.xpath('//span[@id="pubtime_baidu"]/text()').get()
            pubtime = pubtime.replace('发布时间：', '')
            source = response.xpath('//span[@id="source_baidu"]/a/text()').get()
            author = response.xpath('//span[@id="author_baidu"]/text()').get()
            author = author.replace('作者：', '')
            item = NewsItem()
            item['title'] = title
            item['content'] = str(content)
            item['pub_time'] = pubtime
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "中国网"
            if content is not None:
                yield item

    # 中华网
    def parse_china_com(self, response, url):
        # https://news.china.com/socialgd/10000169/20220327/41785167.html
        title = response.xpath('//h1[@id="chan_newsTitle"]/text()').get()
        if title is not None:
            content = response.xpath('//div[@id="chan_newsDetail"]').get()
            pubtime = response.xpath('//div[@id="chan_newsInfo"]/text()[3]').get()
            pubtime = pubtime.strip().replace("&nbsp;", "")
            source = response.xpath('string(//span[@class="chan_newsInfo_source"])').get()
            source = source.strip()
            author = response.xpath('string(//span[@class="chan_newsInfo_author"])').get()
            author = author.strip()
            item = NewsItem()
            item['title'] = title
            item['content'] = str(content)
            item['pub_time'] = pubtime
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "中华网"
            next_link = response.xpath('//a[@class="allPage"]/@href').get()
            if next_link is not None and next_link.find(".html") != -1:
                yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next, cookies=None,
                                     cb_kwargs={"item": item})
            else:
                print(item)
                yield item

    # 中华网 - 正文分页
    def parse_china_com_next(self, response, item):
        content = response.xpath('//div[@id="chan_newsDetail"]').get()
        item['content'] += str(content)
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            print(item)
            yield item

    # 东北网
    def parse_dbw_cn(self, response, url):
        title = response.xpath('//div[@id="end-box"]/h1[1]/text()').get()
        if title is not None:
            content = response.xpath('//div[@class="zhengw"]').get()
            pubtime = response.xpath('//div[@class="time"]/text()[1]').get()
            author_source = response.xpath('//span[@class="rl"]/text()').get()
            author_source = str(author_source).split(" 　")
            if len(author_source) == 2:
                author = author_source[0].replace("编辑：", "")
                source = author_source[1].replace("来源：", "")
            else:
                author = ""
                source = ""
            item = NewsItem()
            item['title'] = title
            item['content'] = str(content)
            item['pub_time'] = pubtime.strip()
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "东北网"
            yield item
