"""
中国有色网爬虫 - Crawl4AI版本
URL: https://www.cnmn.com.cn/ (数字报: https://paper.cnmn.com.cn/)
"""
import asyncio
from crawl4ai_base import Crawl4AIBase
from bs4 import BeautifulSoup

class CNMNCrawler(Crawl4AIBase):
    """中国有色网爬虫（数字报）"""
    
    def __init__(self):
        super().__init__(
            source_name="中国有色网",
            base_url="https://paper.cnmn.com.cn/",
            category="nonferrous_metals"
        )
        
        # 不使用CSS选择器，直接用Markdown提取
        self.list_schema = None
        
        # 详情页选择器 - 使用Markdown
        self.detail_schema = None
    
    async def crawl_list_page(self, crawler):
        """重写列表页爬取方法 - 使用BeautifulSoup提取area标签"""
        print("📋 步骤1: 爬取列表页...")
        
        from crawl4ai import CrawlerRunConfig, CacheMode
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded",
            page_timeout=60000,
            delay_before_return_html=2.0,
        )
        
        result = await crawler.arun(url=self.base_url, config=run_config)
        
        if not result.success:
            print(f"❌ 列表页加载失败: {result.error_message}")
            return []
        
        print(f"✅ 列表页加载成功")
        
        # 使用BeautifulSoup解析HTML，提取area标签
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # 查找所有area标签
        areas = soup.find_all('area', href=True)
        print(f"📊 找到 {len(areas)} 个area标签")
        
        articles = []
        for area in areas:
            href = area.get('href', '')
            
            # 只保留 Content.aspx 的链接
            if 'Content.aspx' in href and 'id=' in href:
                # 处理URL
                url = self.process_url(href)
                if url:
                    # 从URL提取ID作为临时标题
                    import re
                    match = re.search(r'id=(\d+)', href)
                    if match:
                        title = f"文章{match.group(1)}"
                        articles.append({
                            'title': title,
                            'url': url,
                            'published_date': None
                        })
        
        print(f"✅ 有效文章: {len(articles)} 篇")
        
        return articles

async def main():
    crawler = CNMNCrawler()
    # 抓取本月所有文章
    await crawler.crawl(max_articles=50, date_filter='this_month')

if __name__ == "__main__":
    asyncio.run(main())
