"""
中国电力网爬虫 - 电力行业资讯
"""
import scrapy
from energy_crawler.items import ArticleItem
from energy_crawler.content_extractor import extractor
from datetime import datetime
import re

class ChinaPowerSpider(scrapy.Spider):
    """中国电力网爬虫"""
    name = 'chinapower'
    
    allowed_domains = ['chinapower.com.cn']
    start_urls = [
        'http://www.chinapower.com.cn/',
        'http://www.chinapower.com.cn/xw/',  # 新闻
        'http://www.chinapower.com.cn/dlxxh/',  # 电力信息化
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def parse(self, response):
        """解析列表页"""
        self.logger.info(f'正在解析: {response.url}')
        
        # 设置正确的编码
        response = response.replace(encoding='utf-8')
        
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
                ('.html' in href or '.htm' in href or '/content/' in href)):
                
                title = title.strip()
                
                # 跳过导航链接
                if any(skip in title for skip in ['首页', '关于', '联系', '更多', '返回']):
                    continue
                
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'http://www.chinapower.com.cn' + href
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
                
                if articles_found >= 30:  # 限制每页最多30篇
                    break
        
        self.logger.info(f'本页共找到 {articles_found} 篇文章')
    
    def parse_article(self, response):
        """解析文章详情"""
        # 设置正确的编码
        response = response.replace(encoding='utf-8')
        
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '中国电力网'
        item['source_url'] = response.url
        item['category'] = 'power'
        item['published_at'] = datetime.now()
        
        # 使用智能内容提取器
        # 定义备用的CSS选择器
        css_selectors = [
            'div.content p::text',
            'div.article p::text',
            'div#content p::text',
            'div.main-content p::text',
            'div.text p::text',
            'div.article-content p::text',
            'td.content p::text',
        ]
        
        # 提取内容
        extraction_result = extractor.extract_with_fallback(response, css_selectors)
        
        if extraction_result['success']:
            content = extraction_result['content']
            item['content'] = content
            item['summary'] = content[:200] + '...' if len(content) > 200 else content
            
            # 如果提取到了标题,可以覆盖原标题
            if extraction_result['title'] and len(extraction_result['title']) > 5:
                item['title'] = extraction_result['title']
            
            self.logger.info(f'✅ 成功抓取: {item["title"]} (内容长度: {len(content)})')
        else:
            item['content'] = ''
            item['summary'] = ''
            self.logger.warning(f'⚠️  内容提取失败，跳过: {item["title"]}')
        
        # 提取标签
        tags = ['电力', '中国电力网']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = list(set(tags))[:5]
        
        if item.get('content') and len(item['content']) > 100:
            yield item
    
    def handle_error(self, failure):
        """处理请求错误"""
        self.logger.error(f'请求失败: {failure.request.url}')
        self.logger.error(f'错误: {failure.value}')
