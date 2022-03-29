import scrapy


class BingSpider(scrapy.Spider):
    name = 'bing'
    allowed_domains = ['cn.bing.com', 'hixin.cc',"baidu.com","httpbin.org"]
    # start_urls = ['https://cn.bing.com/search?q=%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%91%E4%B8%9C%E8%88%AA%E9%A3%9E%E8%A1%8C%E4%BA%8B%E6%95%85%E9%81%87%E9%9A%BE%E5%90%8C%E8%83%9E%E9%BB%98%E5%93%80']
    # start_urls = ['https://cn.bing.com/search?q=习近平向东航飞行事故遇难同胞默哀']
    # start_urls = ['https://cn.bing.com']
    start_urls = ['https://hixin.cc/?s=%E6%8F%92%E4%BB%B6']
    # start_urls = ['https://www.baidu.com/s?wd=%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%91%E4%B8%9C%E8%88%AA%E9%A3%9E%E8%A1%8C%E4%BA%8B%E6%95%85%E9%81%87%E9%9A%BE%E5%90%8C%E8%83%9E%E9%BB%98%E5%93%80&sa=fyb_news&rsv_dl=fyb_news']
    # start_urls = ['https://www.baidu.com/s?wd=习近平向东航飞行事故遇难同胞默哀&sa=fyb_news&rsv_dl=fyb_news']
    # start_urls = ['https://www.baidu.com/']
    # start_urls = ['http://httpbin.org/get']

    def parse(self, response):
        print(response.text)
