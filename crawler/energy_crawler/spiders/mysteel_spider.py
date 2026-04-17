"""
我的钢铁网爬虫
钢铁行业最权威门户
"""
import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime
import re

class MySteelSpider(scrapy.Spider):
    """我的钢铁网爬虫"""
    name = 'mysteel'
    
    allowed_domains = ['mysteel.com']
    start_urls = [
        'https://www.mysteel.com/',
        'https://www.mysteel.com/news/',  # 新闻中心
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': True,
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
                10 < len(title.strip()) < 150 and
                ('.html' in href or '/news/' in href or '/article/' in href)):
                
                title = title.strip()
                
                # 跳过导航链接
                if any(skip in title for skip in ['首页', '关于', '联系', '更多', '返回', '登录', '注册', '会员']):
                    continue
                
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'https://www.mysteel.com' + href
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
                
                if articles_found >= 25:  # 限制每次最多25篇
                    break
        
        self.logger.info(f'本次共找到 {articles_found} 篇文章')
    
    def parse_article(self, response):
        """解析文章详情"""
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '我的钢铁网'
        item['source_url'] = response.url
        item['category'] = 'steel'
        item['published_at'] = datetime.now()
        
        # 尝试提取发布时间
        time_selectors = [
            'span.time::text',
            'div.time::text',
            'span.date::text',
            'div.date::text',
            'meta[property="article:published_time"]::attr(content)',
        ]
        
        for selector in time_selectors:
            time_text = response.css(selector).get()
            if time_text:
                try:
                    # 尝试解析时间
                    time_text = time_text.strip()
                    if re.match(r'\d{4}-\d{2}-\d{2}', time_text):
                        item['published_at'] = datetime.strptime(time_text[:10], '%Y-%m-%d')
                        break
                except:
                    pass
        
        # 尝试多种内容选择器
        content_selectors = [
            'div.content p::text',
            'div.article-content p::text',
            'div.detail-content p::text',
            'div#content p::text',
            'div.main-content p::text',
            'article p::text',
            'div.news-content p::text',
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
            # 尝试提取整个内容区域
            for selector in ['div.content', 'div.article', 'div.detail', 'div.news-content', 'div.text']:
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
        tags = ['钢铁', '我的钢铁网', '碳排放']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = list(set(tags))[:5]
        
        if item.get('content') and len(item['content']) > 100:
            self.logger.info(f'✅ 成功抓取: {item["title"]} (内容长度: {len(item["content"])})')
            yield item
        else:
            self.logger.warning(f'⚠️  内容太短或为空，跳过: {item["title"]}')
    
    def handle_error(self, failure):
        """处理请求错误"""
        self.logger.error(f'请求失败: {failure.request.url}')
        self.logger.error(f'错误: {failure.value}')
