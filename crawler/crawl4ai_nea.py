"""
国家能源局爬虫 - Crawl4AI版本
URL: https://www.nea.gov.cn/xwzx/nyyw.htm
注意：网站使用Vue.js动态渲染，需要等待JavaScript执行
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class NeaCrawler(Crawl4AIBase):
    """国家能源局爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="国家能源局",
            base_url="https://www.nea.gov.cn/xwzx/nyyw.htm",
            category="energy"
        )
        
        # 列表页选择器 - Vue.js渲染后的结构
        self.list_schema = {
            "name": "NeaArticles",
            "baseSelector": "ul.list li",
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
                    "selector": ".sj, span.sj",
                    "type": "text",
                }
            ]
        }
        
        # 详情页选择器 - 使用CSS提取内容
        self.detail_schema = {
            "name": "NeaArticle",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "content",
                    "selector": "div.TRS_Editor p, div#TRS_AUTOADD_CONTENT p, div.content p, td.b12 p",
                    "type": "text",
                    "all": True
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
        
        # 如果是相对路径，补全为国家能源局域名
        if url.startswith('/'):
            return f"https://www.nea.gov.cn{url}"
        elif url.startswith('../'):
            # 处理 ../ 相对路径
            return f"https://www.nea.gov.cn/{url.replace('../', '')}"
        elif url.startswith('./'):
            return f"https://www.nea.gov.cn/xwzx/{url.replace('./', '')}"
        else:
            return f"https://www.nea.gov.cn/xwzx/{url}"

async def main():
    crawler = NeaCrawler()
    await crawler.crawl(max_articles=3)

if __name__ == "__main__":
    asyncio.run(main())
