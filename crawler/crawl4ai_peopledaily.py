"""
人民网财经频道爬虫 - Crawl4AI版本
注意：人民网能源频道已重定向到财经频道
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class PeopleDailyCrawler(Crawl4AIBase):
    """人民网财经频道爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="人民网",
            base_url="http://finance.people.com.cn/",
            category="energy",
            date_filter='this_month'  # 抓取本月数据
        )
        
        # 列表页选择器 - 使用实际测试的选择器
        self.list_schema = {
            "name": "PeopleDailyArticles",
            "baseSelector": "ul.list_14 li",
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
                    "selector": "span.date, .time, em",
                    "type": "text",
                }
            ]
        }
        
        # 详情页选择器 - 使用CSS提取内容
        self.detail_schema = {
            "name": "PeopleDailyArticle",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "content",
                    "selector": "div.rm_txt_con p",
                    "type": "text",
                    "all": True
                },
                {
                    "name": "summary",
                    "selector": "div.rm_txt_con p",
                    "type": "text",
                }
            ]
        }
    
    def process_url(self, url):
        """处理URL，补全相对路径"""
        if not url:
            return None
        
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        if url.startswith('/'):
            return f"http://finance.people.com.cn{url}"
        else:
            return f"http://finance.people.com.cn/{url}"  # 不使用CSS选择器，直接用Markdown

async def main():
    crawler = PeopleDailyCrawler()
    await crawler.crawl(max_articles=20)  # 增加到20篇

if __name__ == "__main__":
    asyncio.run(main())
