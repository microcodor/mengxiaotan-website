"""
中国电力网爬虫 - Crawl4AI版本
URL: http://www.chinapower.com.cn/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class ChinaPowerCrawler(Crawl4AIBase):
    """中国电力网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="中国电力网",
            base_url="http://www.chinapower.com.cn/xw/",
            category="power"
        )
        
        # 列表页选择器
        self.list_schema = {
            "name": "ChinaPowerArticles",
            "baseSelector": "ul.list li, div.list-item, div.news-list li",
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
                    "selector": ".date, .time, span.date, span.time",
                    "type": "text",
                }
            ]
        }
        
        # 详情页选择器 - 使用Markdown提取
        self.detail_schema = None
    
    def process_url(self, url):
        """处理URL，补全相对路径"""
        if not url:
            return None
        
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        if url.startswith('/'):
            return f"http://www.chinapower.com.cn{url}"
        else:
            return f"http://www.chinapower.com.cn/{url}"

async def main():
    crawler = ChinaPowerCrawler()
    await crawler.crawl(max_articles=10)

if __name__ == "__main__":
    asyncio.run(main())
