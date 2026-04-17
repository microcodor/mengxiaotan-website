"""
中国能源报社爬虫 - Crawl4AI版本
URL: https://www.cnenergynews.cn/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class CnEnergyNewsCrawler(Crawl4AIBase):
    """中国能源报社爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="中国能源报",
            base_url="https://www.cnenergynews.cn/",
            category="energy"
        )
        
        # 不使用CSS选择器，直接用Markdown提取
        # 网站的文章链接格式: /article/xxxxx
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
            
            # 只保留 /article/ 开头的链接，且不是 /article/ 本身
            if '/article/' in href and href != '/article/' and text:
                articles.append({
                    'title': text.strip(),
                    'url': href,
                    'published_date': None
                })
        
        return articles

async def main():
    crawler = CnEnergyNewsCrawler()
    # 抓取本月所有文章，不限制数量
    await crawler.crawl(max_articles=100, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
