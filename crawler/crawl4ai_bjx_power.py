"""
北极星电力网爬虫 - Crawl4AI版本
URL: https://news.bjx.com.cn/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class BJXPowerCrawler(Crawl4AIBase):
    """北极星电力网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="北极星电力网",
            base_url="https://news.bjx.com.cn/list/power.html",
            category="power"
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
            
            # 北极星电力网的文章链接格式: .shtml 或 .html
            # 过滤条件：包含 .shtml 或 .html，且标题长度合适
            if ('.shtml' in href or '.html' in href) and text and 10 < len(text.strip()) < 100:
                # 过滤掉导航链接
                if not any(skip in text for skip in ['首页', '关于', '联系', '更多', '返回', '登录', '注册', '订阅']):
                    articles.append({
                        'title': text.strip(),
                        'url': href,
                        'published_date': None
                    })
        
        return articles

async def main():
    crawler = BJXPowerCrawler()
    # 抓取本月所有文章
    await crawler.crawl(max_articles=100, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
