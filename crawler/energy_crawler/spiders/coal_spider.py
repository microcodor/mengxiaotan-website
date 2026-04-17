"""
中国煤炭网爬虫 - 真实抓取版本
"""
import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime
import re

class CoalSpider(scrapy.Spider):
    """煤炭行业爬虫 - 中国煤炭市场网"""
    name = 'coal'
    
    allowed_domains = ['cctd.com.cn']
    start_urls = [
        'https://www.cctd.com.cn/news/',  # 新闻中心
        'https://www.cctd.com.cn/',  # 首页
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def parse(self, response):
        """解析列表页"""
        self.logger.info(f'正在解析: {response.url}')
        
        # 查找所有文章链接
        links = response.css('a[href]')
        
        articles_found = 0
        for link in links:
            href = link.css('::attr(href)').get()
            title = link.css('::text').get()
            
            if not title:
                title = link.css('::attr(title)').get()
            
            # 过滤条件
            if (title and href and 
                10 < len(title.strip()) < 100 and
                ('.html' in href or '.htm' in href or '/show/' in href)):
                
                title = title.strip()
                
                # 跳过导航链接
                if any(skip in title for skip in ['首页', '关于', '联系', '更多', '返回']):
                    continue
                
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'https://www.cctd.com.cn' + href
                    else:
                        href = response.urljoin(href)
                
                articles_found += 1
                
                self.logger.info(f'找到文章 {articles_found}: {title}')
                
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={'title': title},
                    dont_filter=True,
                    errback=self.handle_error
                )
                
                if articles_found >= 20:  # 限制每页最多20篇
                    break
        
        self.logger.info(f'本页共找到 {articles_found} 篇文章')
    
    def parse_article(self, response):
        """解析文章详情"""
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '中国煤炭市场网'
        item['source_url'] = response.url
        item['category'] = 'coal'
        item['published_at'] = datetime.now()
        
        # 尝试多种内容选择器
        content_selectors = [
            'div.content p::text',
            'div.article p::text',
            'div#content p::text',
            'div.main-content p::text',
            'div.text p::text',
            'div.article-content p::text',
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
            # 尝试提取整个内容区域
            for selector in ['div.content', 'div.article', 'div.text']:
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
        
        # 提取标签
        tags = ['煤炭', '能源', '市场分析']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = list(set(tags))[:5]
        
        if item['content'] and len(item['content']) > 100:
            self.logger.info(f'✅ 成功抓取: {item["title"]} (内容长度: {len(item["content"])})')
            yield item
        else:
            self.logger.warning(f'⚠️  内容太短或为空，跳过: {item["title"]}')
    
    def handle_error(self, failure):
        """处理请求错误"""
        self.logger.error(f'请求失败: {failure.request.url}')
        self.logger.error(f'错误: {failure.value}')
