"""
人民网能源频道爬虫 - 使用Playwright处理JavaScript渲染
"""
import scrapy
from scrapy.http import HtmlResponse
from energy_crawler.items import ArticleItem
from datetime import datetime
import re
import asyncio
from playwright.async_api import async_playwright

class PeopleDailySpider(scrapy.Spider):
    """人民网能源频道爬虫 - 使用Playwright"""
    name = 'peopledaily'
    
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
            'http://energy.people.com.cn/',
            'http://finance.people.com.cn/energy/',
        ]
        
        for url in urls:
            yield scrapy.Request(
                url,
                callback=self.parse_with_playwright,
                dont_filter=True
            )
    
    def parse_with_playwright(self, response):
        """使用Playwright解析页面"""
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
            await page.wait_for_timeout(3000)
            html = await page.content()
            await page.close()
            return html
        except Exception as e:
            self.logger.error(f'Playwright获取页面失败: {str(e)}')
            return None
    
    def parse_article_list(self, response):
        """解析文章列表"""
        self.logger.info(f'开始解析页面: {response.url}')
        
        links = response.css('a[href]')
        articles_found = 0
        
        for link in links:
            href = link.css('::attr(href)').get()
            title = link.css('::text').get()
            
            if not title:
                title = link.css('::attr(title)').get()
            
            if not title or not href:
                continue
            
            title = title.strip()
            
            if (10 < len(title) < 100 and 
                ('.html' in href or '.htm' in href) and
                not any(skip in title for skip in ['首页', '关于', '联系', '更多', '返回', '登录'])):
                
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'http://energy.people.com.cn' + href
                    else:
                        href = response.urljoin(href)
                
                articles_found += 1
                self.logger.info(f'找到文章 {articles_found}: {title}')
                
                yield scrapy.Request(
                    href,
                    callback=self.parse_article_with_playwright,
                    meta={'title': title},
                    dont_filter=True
                )
                
                if articles_found >= 20:
                    break
        
        self.logger.info(f'本页共找到 {articles_found} 篇文章')
    
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
        item['source'] = '人民网'
        item['source_url'] = response.url
        item['category'] = 'media'
        
        # 提取发布时间
        date_text = response.css('.time::text, .date::text, .box01 .fl::text').get()
        item['published_at'] = self.parse_date(date_text) if date_text else datetime.now()
        
        # 提取作者
        author = response.css('.author::text, .source::text, .box01 .fl::text').getall()
        if author:
            author = ' '.join([a.strip() for a in author if a.strip()])
            author = author.replace('来源：', '').replace('作者：', '')
        
        # 提取内容
        content_selectors = [
            'div.rm_txt_con p::text',
            'div.box_con p::text',
            'div.content p::text',
            'div#rwb_zw p::text',
            'div.article p::text',
            'div.text p::text',
        ]
        
        content_parts = []
        for selector in content_selectors:
            parts = response.css(selector).getall()
            if parts and len(parts) > 2:
                content_parts = parts
                self.logger.info(f'使用选择器 "{selector}" 提取到 {len(parts)} 段内容')
                break
        
        if content_parts:
            content = '\n\n'.join([p.strip() for p in content_parts if p.strip() and len(p.strip()) > 10])
            item['content'] = content
            item['summary'] = content[:200] + '...' if len(content) > 200 else content
        else:
            for selector in ['div.rm_txt_con', 'div.box_con', 'div#rwb_zw', 'div.content']:
                content_div = response.css(selector)
                if content_div:
                    text_parts = content_div.css('::text').getall()
                    text_parts = [t.strip() for t in text_parts if t.strip() and len(t.strip()) > 20]
                    if text_parts:
                        content = '\n\n'.join(text_parts[:50])
                        if len(content) > 100:
                            item['content'] = content
                            item['summary'] = content[:200] + '...'
                            break
        
        if not item.get('content'):
            item['content'] = ''
            item['summary'] = ''
        
        tags = ['人民网', '能源', '政策']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = list(set(tags))[:5]
        
        if item['content'] and len(item['content']) > 100:
            self.logger.info(f'✅ 成功抓取: {item["title"]} (内容长度: {len(item["content"])})')
            yield item
        else:
            self.logger.warning(f'⚠️  内容太短或为空，跳过: {item["title"]}')
    
    def parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.strip()
        patterns = [
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
            (r'(\d{4})/(\d{2})/(\d{2})', '%Y/%m/%d'),
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
