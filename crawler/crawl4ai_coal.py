"""
中国煤炭市场网爬虫 - Crawl4AI版本
URL: https://www.cctd.com.cn/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class CoalCrawler(Crawl4AIBase):
    """中国煤炭市场网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="中国煤炭市场网",
            base_url="https://www.cctd.com.cn/news/",
            category="coal"
        )
        
        # 不使用CSS选择器，直接用Markdown提取
        self.list_schema = None
        
        # 详情页选择器 - 使用Markdown
        self.detail_schema = None
    
    def extract_from_markdown(self, result):
        """从Markdown提取链接 - 只保留文章链接"""
        articles = []
        
        if not result.markdown or not result.links:
            return articles
        
        # 从内部链接中提取
        for link in result.links.get('internal', []):
            href = link.get('href', '')
            text = link.get('text', '')
            
            # 中国煤炭市场网的文章链接格式: .html 或 .htm 或 /show/
            if (('.html' in href or '.htm' in href or '/show/' in href) and 
                text and 10 < len(text.strip()) < 100):
                # 过滤掉导航链接
                if not any(skip in text for skip in ['首页', '关于', '联系', '更多', '返回', '登录', '注册']):
                    articles.append({
                        'title': text.strip(),
                        'url': href,
                        'published_date': None
                    })
        
        return articles

async def main():
    crawler = CoalCrawler()
    # 抓取本月所有文章
    await crawler.crawl(max_articles=100, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
