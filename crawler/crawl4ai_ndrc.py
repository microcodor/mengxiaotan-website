"""
国家发改委爬虫 - Crawl4AI版本
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class NdrcCrawler(Crawl4AIBase):
    """国家发改委爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="国家发改委",
            base_url="https://www.ndrc.gov.cn/xwdt/tzgg/",
            category="government"
        )
        
        # 列表页选择器
        self.list_schema = {
            "name": "NdrcArticles",
            "baseSelector": "ul.u-list li, div.list-date li",
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
                    "selector": "div.TRS_Editor, div.content, article",
                    "type": "text",
                },
                {
                    "name": "summary",
                    "selector": "div.summary, .abstract",
                    "type": "text",
                }
            ]
        }
    
    def process_url(self, url):
        """处理URL，补全相对路径"""
        if not url:
            return None
        
        # 如果是完整URL，直接返回
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        # 处理 ./ 开头的相对路径
        if url.startswith('./'):
            url = url[2:]  # 去掉 ./
        
        # 如果是相对路径，补全
        if url.startswith('/'):
            return f"https://www.ndrc.gov.cn{url}"
        
        # 其他情况，拼接base_url的目录部分
        base_dir = self.base_url.rsplit('/', 1)[0]
        return base_dir + '/' + url

async def main():
    crawler = NdrcCrawler()
    # 抓取本月所有文章
    await crawler.crawl(max_articles=50, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
