"""
国家能源局真实爬虫 - 使用Playwright处理动态内容
"""
import scrapy
from scrapy.http import HtmlResponse
from energy_crawler.items import ArticleItem
from datetime import datetime
import re
import asyncio
from playwright.async_api import async_playwright
import logging

class RealNeaSpider(scrapy.Spider):
    """国家能源局真实爬虫 - 使用Playwright"""
    name = 'real_nea'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'ROBOTSTXT_OBEY': False,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def init_playwright(self):
        """初始化Playwright"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
    
    async def close_playwright(self):
        """关闭Playwright"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def start_requests(self):
        """开始请求"""
        urls = [
            'https://www.nea.gov.cn/xwzx/nyyw.htm',  # 能源要闻
            'https://www.nea.gov.cn/news/jwzdt.htm',  # 局工作动态
        ]
        
        for url in urls:
            yield scrapy.Request(
                url,
                callback=self.parse_with_playwright,
                meta={'playwright': True},
                dont_filter=True
            )
    
    def parse_with_playwright(self, response):
        """使用Playwright解析页面"""
        # 创建异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            html = loop.run_until_complete(self.fetch_page(response.url))
            
            if html:
                # 创建新的Response对象
                new_response = HtmlResponse(
                    url=response.url,
                    body=html.encode('utf-8'),
                    encoding='utf-8'
                )
                
                # 解析文章列表
                yield from self.parse_article_list(new_response)
        finally:
            loop.close()
    
    async def fetch_page(self, url):
        """使用Playwright获取页面内容"""
        await self.init_playwright()
        
        try:
            page = await self.context.new_page()
            
            self.logger.info(f'正在访问: {url}')
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待内容加载
            await page.wait_for_timeout(3000)
            
            # 获取渲染后的HTML
            html = await page.content()
            
            await page.close()
            
            return html
        except Exception as e:
            self.logger.error(f'Playwright获取页面失败: {str(e)}')
            return None
    
    def parse_article_list(self, response):
        """解析文章列表"""
        self.logger.info(f'开始解析页面: {response.url}')
        
        # 尝试多种选择器
        selectors = [
            'ul.list li',
            'div.list-item',
            'ul li a[href*=".html"]',
            'div.news-list li',
            'ul.news li',
        ]
        
        articles_found = 0
        
        for selector in selectors:
            articles = response.css(selector)
            if articles:
                self.logger.info(f'使用选择器 "{selector}" 找到 {len(articles)} 个元素')
                
                for article in articles[:20]:  # 限制每页最多20篇
                    # 提取链接
                    link = article.css('a::attr(href)').get()
                    if not link:
                        continue
                    
                    # 提取标题
                    title = article.css('a::text, a::attr(title)').get()
                    if not title:
                        title = article.css('::text').get()
                    
                    if not title or not link:
                        continue
                    
                    title = title.strip()
                    if len(title) < 5:  # 标题太短，跳过
                        continue
                    
                    # 构建完整URL
                    if not link.startswith('http'):
                        link = response.urljoin(link)
                    
                    # 提取日期
                    date_text = article.css('.date::text, .time::text, span::text').getall()
                    published_at = self.parse_date(' '.join(date_text))
                    
                    articles_found += 1
                    
                    self.logger.info(f'找到文章: {title}')
                    
                    # 请求文章详情页
                    yield scrapy.Request(
                        link,
                        callback=self.parse_article_with_playwright,
                        meta={
                            'playwright': True,
                            'title': title,
                            'published_at': published_at
                        },
                        dont_filter=True
                    )
                
                if articles_found > 0:
                    break
        
        if articles_found == 0:
            self.logger.warning(f'未找到文章，页面内容长度: {len(response.text)}')
            # 保存HTML用于调试
            with open('/tmp/nea_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.logger.info('页面HTML已保存到 /tmp/nea_debug.html')
    
    def parse_article_with_playwright(self, response):
        """使用Playwright解析文章详情"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            html = loop.run_until_complete(self.fetch_page(response.url))
            
            if html:
                new_response = HtmlResponse(
                    url=response.url,
                    body=html.encode('utf-8'),
                    encoding='utf-8'
                )
                
                yield from self.parse_article(new_response, response.meta)
        finally:
            loop.close()
    
    def parse_article(self, response, meta):
        """解析文章详情"""
        item = ArticleItem()
        
        item['title'] = meta['title']
        item['source'] = '国家能源局'
        item['source_url'] = response.url
        item['category'] = 'energy'
        item['published_at'] = meta['published_at']
        
        # 尝试多种内容选择器
        content_selectors = [
            'div.content p::text',
            'div.article-content p::text',
            'div.TRS_Editor p::text',
            'div#content p::text',
            'div.main-content p::text',
            'div.article p::text',
        ]
        
        content_parts = []
        for selector in content_selectors:
            parts = response.css(selector).getall()
            if parts and len(parts) > 2:  # 至少有3段内容
                content_parts = parts
                break
        
        if content_parts:
            content = '\n'.join([p.strip() for p in content_parts if p.strip()])
            item['content'] = content
            item['summary'] = content[:200] + '...' if len(content) > 200 else content
        else:
            # 如果没有找到段落，尝试获取整个内容区域的文本
            for selector in ['div.content', 'div.article-content', 'div.TRS_Editor']:
                content = response.css(f'{selector}::text').getall()
                if content:
                    content = '\n'.join([c.strip() for c in content if c.strip()])
                    if len(content) > 100:
                        item['content'] = content
                        item['summary'] = content[:200] + '...' if len(content) > 200 else content
                        break
        
        # 如果还是没有内容，记录警告
        if not item.get('content'):
            self.logger.warning(f'未能提取文章内容: {item["title"]}')
            item['content'] = ''
            item['summary'] = ''
        
        # 提取标签
        tags = ['能源', '国家能源局']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = tags
        
        if item['content']:
            self.logger.info(f'✅ 成功抓取: {item["title"]} (内容长度: {len(item["content"])})')
            yield item
        else:
            self.logger.warning(f'⚠️  内容为空，跳过: {item["title"]}')
    
    def parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.strip()
        patterns = [
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
            (r'(\d{4})/(\d{2})/(\d{2})', '%Y/%m/%d'),
            (r'(\d{2})-(\d{2})-(\d{2})', '%y-%m-%d'),
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    return datetime.strptime(match.group(0), fmt)
                except:
                    pass
        
        return datetime.now()
    
    def closed(self, reason):
        """爬虫关闭时清理资源"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.close_playwright())
        loop.close()
