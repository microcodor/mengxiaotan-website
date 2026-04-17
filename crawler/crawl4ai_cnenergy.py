"""
中国能源网爬虫 - Crawl4AI版本
URL: https://www.china5e.com/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class CnEnergyCrawler(Crawl4AIBase):
    """中国能源网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="中国能源网",
            base_url="https://www.china5e.com/news/",
            category="energy"
        )
        
        # 不使用CSS选择器，直接用Markdown提取
        self.list_schema = None
        
        # 详情页选择器 - 使用Markdown
        self.detail_schema = None
    
    def extract_from_markdown(self, result):
        """从Markdown提取链接 - 只保留真正的文章链接"""
        articles = []
        
        if not result.markdown or not result.links:
            return articles
        
        # 从内部链接中提取
        for link in result.links.get('internal', []):
            href = link.get('href', '')
            text = link.get('text', '')
            
            if not text or not href:
                continue
            
            text = text.strip()
            
            # 只保留真正的文章链接
            # 文章链接格式: /news/news-数字-1.html
            if '/news/news-' in href and href.endswith('.html'):
                # 过滤掉明显的导航链接和栏目页
                if not any(skip in text for skip in [
                    '首页', '关于', '联系', '更多', '返回', '登录', '注册',
                    '政策与经济', '油气', '煤炭', '电力', '新能源', '节能环保',
                    '【', '】', 'English', '网站地图', '资讯', '新闻'
                ]):
                    # 标题长度合理
                    if 10 < len(text) < 100:
                        articles.append({
                            'title': text,
                            'url': href,
                            'published_date': None
                        })
        
        return articles

async def main():
    crawler = CnEnergyCrawler()
    await crawler.crawl(max_articles=50, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
