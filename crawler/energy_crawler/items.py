import scrapy

class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    source_url = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    published_at = scrapy.Field()
