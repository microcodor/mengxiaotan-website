"""
新华网能源频道爬虫 - Crawl4AI版本
URL: http://www.news.cn/energy/
合并了原xinhua_energy_spider、xinhua_spider和xinhua_real_spider
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class XinhuaCrawler(Crawl4AIBase):
    """新华网能源频道爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="新华网",
            base_url="http://www.news.cn/energy/",
            category="energy"
        )
        
        # 列表页选择器
        self.list_schema = {
            "name": "XinhuaArticles",
            "baseSelector": "ul.dataList li, div.item, ul.news-list li, div.list-item",
            "fields": [
                {
                    "name": "title",
                    "selector": "a, h3, .tit",
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
                    "selector": ".time, .date, span.time, span.date",
                    "type": "text",
                }
            ]
        }
        
        # 详情页选择器 - 使用Markdown提取
        self.detail_schema = None

async def main():
    crawler = XinhuaCrawler()
    await crawler.crawl(max_articles=10)

if __name__ == "__main__":
    asyncio.run(main())
