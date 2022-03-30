import scrapy
import json

from Connect.items import NewsItem


class ZgwSpider(scrapy.Spider):
    name = 'zgw'
    allowed_domains = ['china.com.cn', 'china.com', 'dbw.cn', 'hixin.cc', 'thekonnect.cn']
    start_urls = ['https://thekonnect.cn/api-spider/']

    def parse(self, response, **kwargs):
        result = json.loads(response.text)
        urls = result['urls']
        print(urls)
        for url in urls:
            # 中国网
            if url.find("china.com.cn/") != -1:
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
        # http://henan.china.com.cn/m/2022-03/29/content_41919531.html
        title_mobile = response.xpath('//div[contains(@class,"d_title")]/text()').get()
        if title is not None:
            yield from self.parse_china_com_cn_web(response, title, url)
        elif title_mobile is not None:
            yield from self.parse_china_com_cn_mobile(response, title_mobile, url)

    # 中国网 - mobile
    def parse_china_com_cn_mobile(self, response, title_mobile, url):
        item = NewsItem()
        item['title'] = title_mobile
        content = response.xpath('//div[contains(@class,"d_img")]').get()
        item['content'] = str(content)
        pubtime = response.xpath('//div[contains(@class,"d_time")]/span/text()').get()
        item['pub_time'] = pubtime.strip()
        source = response.xpath('//div[contains(@class,"d_time")]/text()').get()
        item['source'] = source.strip().replace('来源：', '')
        item['author'] = ""
        item['url'] = url
        item['origin'] = "中国网"
        if content is not None:
            yield item

    # 中国网 - web
    def parse_china_com_cn_web(self, response, title, url):
        item = NewsItem()
        item['title'] = title
        content = response.xpath('//div[@id="articleBody"]').get()
        video = response.xpath('string(//div[@id="videoarea"])').get()
        video_element = response.xpath('//div[@id="videoarea"]').get()
        if video is None or video == "":
            content = content.replace(video_element, '')
        item['content'] = str(content)
        pubtime = response.xpath('//span[@id="pubtime_baidu"]/text()').get()
        item['pub_time'] = pubtime.replace('发布时间：', '')
        item['source'] = response.xpath('//span[@id="source_baidu"]/a/text()').get()
        author = response.xpath('//span[@id="author_baidu"]/text()').get()
        item['author'] = author.replace('作者：', '')
        item['url'] = url
        item['origin'] = "中国网"
        if content is not None:
            yield item

    # 中华网
    def parse_china_com(self, response, url):
        # https://news.china.com/socialgd/10000169/20220327/41785167.html
        title_type1 = response.xpath('//h1[@id="chan_newsTitle"]/text()').get()
        # https://news.china.com/domestic/945/20220330/41811858.html
        title_type2 = response.xpath('//h1[contains(@class,"article_title")]/text()').get()
        if title_type1 is not None:
            yield from self.parse_china_com_type_1(response, title_type1, url)
        elif title_type2 is not None:
            yield from self.parse_china_com_type_2(response, title_type2, url)

    # 中华网 - 类型1
    def parse_china_com_type_1(self, response, title_type1, url):
        item = NewsItem()
        item['title'] = title_type1
        content = response.xpath('//div[@id="chan_newsDetail"]').get()
        item['content'] = str(content)
        pubtime = response.xpath('//div[@id="chan_newsInfo"]/text()[3]').get()
        item['pub_time'] = pubtime.strip().replace("&nbsp;", "")
        source = response.xpath('string(//span[@class="chan_newsInfo_source"])').get()
        item['source'] = source.strip()
        author = response.xpath('string(//span[@class="chan_newsInfo_author"])').get()
        item['author'] = author.strip()
        item['url'] = url
        item['origin'] = "中华网"
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_1, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            print(item)
            yield item

    # 中华网 - 正文分页 - 类型1
    def parse_china_com_next_1(self, response, item):
        content = response.xpath('//div[@id="chan_newsDetail"]').get()
        item['content'] += str(content)
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_1, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            print(item)
            yield item

    # 中华网 - 类型2
    def parse_china_com_type_2(self, response, title_type1, url):
        item = NewsItem()
        item['title'] = title_type1
        content = response.xpath('//div[contains(@class,"article_content")]').get()
        item['content'] = str(content)
        pubtime = response.xpath('//div[contains(@class,"article_info")]/span[@class="time"]/text()').get()
        item['pub_time'] = pubtime.strip().replace("&nbsp;", "")
        source = response.xpath('//div[contains(@class,"article_info")]/span[@class="source"]/a/text()').get()
        item['source'] = source.strip()
        item['author'] = ""
        item['url'] = url
        item['origin'] = "中华网"
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_2, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            print(item)
            yield item

    # 中华网 - 正文分页 - 类型2
    def parse_china_com_next_2(self, response, item):
        content = response.xpath('//div[contains(@class,"article_content")]').get()
        item['content'] += str(content)
        next_link = response.xpath('//a[@class="allPage"]/@href').get()
        if next_link is not None and next_link.find(".html") != -1:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_china_com_next_2, cookies=None,
                                 cb_kwargs={"item": item})
        else:
            print(item)
            yield item

    # 东北网
    def parse_dbw_cn(self, response, url):
        title = response.xpath('//div[@id="end-box"]/h1[1]/text()').get()
        if title is not None:
            item = NewsItem()
            item['title'] = title
            content = response.xpath('//div[@class="zhengw"]').get()
            item['content'] = str(content)
            pubtime = response.xpath('//div[@class="time"]/text()[1]').get()
            item['pub_time'] = pubtime.strip()
            author_source = response.xpath('//span[@class="rl"]/text()').get()
            author_source = str(author_source).split(" 　")
            if len(author_source) == 2:
                author = author_source[0].replace("编辑：", "")
                source = author_source[1].replace("来源：", "")
            else:
                author = ""
                source = ""
            item['author'] = author
            item['source'] = source
            item['url'] = url
            item['origin'] = "东北网"
            yield item
