"""
新华网能源频道真实爬虫
"""
import scrapy
from energy_crawler.items import ArticleItem
from energy_crawler.content_extractor import extractor
from datetime import datetime
import re

class XinhuaRealSpider(scrapy.Spider):
    """新华网能源频道爬虫 - 抓取真实新闻"""
    name = 'xinhua_real'
    
    allowed_domains = ['news.cn', 'xinhuanet.com']
    start_urls = [
        'http://www.news.cn/energy/',  # 新华网能源频道
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
            
            # 过滤条件：标题长度合适，URL包含.html
            if (title and href and 
                10 < len(title.strip()) < 100 and
                ('.html' in href or '/c_' in href)):
                
                title = title.strip()
                
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'https://www.news.cn' + href
                    else:
                        href = response.urljoin(href)
                
                articles_found += 1
                
                self.logger.info(f'找到文章 {articles_found}: {title}')
                
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={'title': title},
                    dont_filter=True
                )
                
                if articles_found >= 20:  # 限制每页最多20篇
                    break
        
        self.logger.info(f'本页共找到 {articles_found} 篇文章')
    
    def parse_article(self, response):
        """解析文章详情"""
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '新华网'
        item['source_url'] = response.url
        item['category'] = 'energy'
        item['published_at'] = datetime.now()
        
        # 使用智能内容提取器
        # 定义备用的CSS选择器
        css_selectors = [
            'div#detail p::text',
            'div.article p::text',
            'div#content p::text',
            'div.main-content p::text',
            'article p::text',
            'div.content p::text',
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
        tags = ['能源', '新华网']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()][:3])
        item['tags'] = list(set(tags))[:5]  # 去重并限制数量
        
        if item.get('content') and len(item['content']) > 100:
            yield item
