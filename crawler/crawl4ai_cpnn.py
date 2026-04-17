"""
中国电力新闻网爬虫 - Crawl4AI版本
URL: http://www.cpnn.com.cn/
"""
import asyncio
from crawl4ai_base import Crawl4AIBase

class CPNNCrawler(Crawl4AIBase):
    """中国电力新闻网爬虫"""
    
    def __init__(self):
        super().__init__(
            source_name="中国电力新闻网",
            base_url="http://www.cpnn.com.cn/news/",
            category="power"
        )
        
        # 不使用CSS选择器，直接用Markdown提取
        self.list_schema = None
        self.detail_schema = None
    
    def extract_from_markdown(self, result):
        """从Markdown提取链接"""
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
            
            # 中国电力新闻网的文章链接格式
            if ('.html' in href or '.htm' in href or '/content/' in href):
                # 过滤掉导航链接
                if not any(skip in text for skip in [
                    '首页', '关于', '联系', '更多', '返回', '登录', '注册',
                    '网站地图', 'English', '订阅', '搜索', '帮助',
                    '【', '】', '栏目', '频道', '专题', '视频', '图片'
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
    crawler = CPNNCrawler()
    await crawler.crawl(max_articles=50, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
