"""
CCER碳交易爬虫 - Crawl4AI版本
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class CcerCrawler(Crawl4AIBase):
    """CCER碳交易爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="CCER碳交易",
            base_url="http://www.ccer.com.cn/",
            category="carbon"
        )
        
        # 列表页选择器
        self.list_schema = {
            "name": "CcerArticles",
            "baseSelector": "div.news-list li, ul.list li",
            "fields": [
                {
                    "name": "title",
                    "selector": "a",
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
                    "selector": "span.date, .time",
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
                    "selector": "div.content, div.article-content, article",
                    "type": "text",
                },
                {
                    "name": "summary",
                    "selector": "div.summary, .abstract",
                    "type": "text",
                }
            ]
        }

async def main():
    crawler = CcerCrawler()
    await crawler.crawl(max_articles=10)

if __name__ == "__main__":
    asyncio.run(main())
