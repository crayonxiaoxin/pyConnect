import scrapy


class DbwSpider(scrapy.Spider):
    name = 'dbw'
    allowed_domains = ['dbw.cn']
    start_urls = ['https://dbw.cn/']

    categories = ["heilongjiang", "guonei", "guoji", "harbin", "yule", "shehui", "jiaoyu", "fazhi", "caijing", "lvyou",
                  "fangchan", "jiankang", "minsheng", "tiyu", "difang"]

    def parse(self, response, **kwargs):

        pass
