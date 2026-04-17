"""
上海有色金属网爬虫 - Crawl4AI版本
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class SmmMetalCrawler(Crawl4AIBase):
    """上海有色金属网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="上海有色金属网",
            base_url="https://news.smm.cn/",
            category="steel"
        )
        
        # 列表页选择器
        self.list_schema = {
            "name": "SmmMetalArticles",
            "baseSelector": "div.news-list li, ul.list li, div.list-item",
            "fields": [
                {
                    "name": "title",
                    "selector": "a, h3",
                    "type": "text",
                },
                {
                    "name": "url",
                    "selector": "a",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "published_date",
                    "selector": "span.date, .time, span.pub-time",
                    "type": "text",
                }
            ]
        }
        
        # 详情页选择器
        self.detail_schema = {
            "name": "ArticleDetail",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "content",
                    "selector": "div.content, div.article-content, article, div.detail-content",
                    "type": "text",
                },
                {
                    "name": "summary",
                    "selector": "div.summary, .abstract, div.intro",
                    "type": "text",
                }
            ]
        }

async def main():
    crawler = SmmMetalCrawler()
    await crawler.crawl(max_articles=10)

if __name__ == "__main__":
    asyncio.run(main())
