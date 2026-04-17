"""
Solarbe光伏网爬虫 - Crawl4AI版本
URL: https://www.solarbe.com/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class SolarbeCrawler(Crawl4AIBase):
    """Solarbe光伏网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="Solarbe光伏网",
            base_url="https://www.solarbe.com/news/",
            category="solar"
        )
        
        self.list_schema = None
        self.detail_schema = None
    
    def extract_from_markdown(self, result):
        """从Markdown提取链接"""
        articles = []
        
        if not result.markdown or not result.links:
            return articles
        
        for link in result.links.get('internal', []):
            href = link.get('href', '')
            text = link.get('text', '')
            
            if not text or not href:
                continue
            
            text = text.strip()
            
            if ('.html' in href or '.htm' in href or '/news/' in href):
                if not any(skip in text for skip in [
                    '首页', '关于', '联系', '更多', '返回', '登录', '注册',
                    '【', '】', '栏目', '频道', '视频', '图片'
                ]):
                    if 10 < len(text) < 100:
                        articles.append({
                            'title': text,
                            'url': href,
                            'published_date': None
                        })
        
        return articles

async def main():
    crawler = SolarbeCrawler()
    await crawler.crawl(max_articles=50, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
