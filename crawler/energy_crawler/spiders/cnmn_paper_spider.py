"""
中国有色金属报数字报爬虫
有色金属行业官方报纸
"""
import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime
import re

class CNMNPaperSpider(scrapy.Spider):
    """中国有色金属报数字报爬虫"""
    name = 'cnmn_paper'
    
    allowed_domains = ['cnmn.com.cn']
    start_urls = [
        'https://paper.cnmn.com.cn/',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        """解析数字报首页"""
        self.logger.info(f'正在解析: {response.url}')
        
        # 方法1: 查找图片地图中的 AREA 标签（数字报特有结构）
        area_links = response.css('area[href]')
        
        articles_found = 0
        for area in area_links:
            href = area.css('::attr(href)').get()
            
            # 过滤条件：只抓取 Content.aspx 页面
            if href and 'Content.aspx' in href:
                # 构建完整URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = 'https://paper.cnmn.com.cn' + href
                    else:
                        href = response.urljoin(href)
                
                # 清理URL中的 &amp;
                href = href.replace('&amp;', '&')
                
                articles_found += 1
                
                self.logger.info(f'找到文章 {articles_found}: {href}')
                
                yield scrapy.Request(
                    href,
                    callback=self.parse_article,
                    meta={'title': None},  # 标题从详情页提取
                    dont_filter=True,
                    errback=self.handle_error
                )
                
                if articles_found >= 20:  # 限制每次最多20篇
                    break
        
        # 方法2: 如果没有找到 AREA 标签，尝试查找普通链接
        if articles_found == 0:
            self.logger.info('未找到图片地图链接，尝试查找普通链接...')
            links = response.css('a[href]')
            
            for link in links:
                href = link.css('::attr(href)').get()
                title = link.css('::text').get()
                
                if not title:
                    title = link.css('::attr(title)').get()
                
                # 过滤条件
                if (title and href and 
                    10 < len(title.strip()) < 150 and
                    ('.html' in href or '/content/' in href.lower() or '/article/' in href)):
                    
                    title = title.strip()
                    
                    # 跳过导航链接
                    if any(skip in title for skip in ['首页', '关于', '联系', '更多', '返回', '登录', '注册', '版面']):
                        continue
                    
                    # 构建完整URL
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = 'https://paper.cnmn.com.cn' + href
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
                    
                    if articles_found >= 20:
                        break
        
        self.logger.info(f'本次共找到 {articles_found} 篇文章')
    
    def parse_article(self, response):
        """解析文章详情"""
        item = ArticleItem()
        
        # 如果meta中没有标题，尝试从页面提取
        title = response.meta.get('title')
        if not title:
            # 尝试多种标题选择器（数字报特有结构）
            title_selectors = [
                'a.TitleA::text',  # 中国有色金属报特有
                'h1::text',
                'h2::text',
                'div.title::text',
                'div.article-title::text',
                'span.title::text',
                'td.title::text',
                'font[size="4"]::text',  # 老式网页常用
                'b::text',  # 加粗文本可能是标题
            ]
            for selector in title_selectors:
                titles = response.css(selector).getall()
                for t in titles:
                    t = t.strip()
                    if t and 10 < len(t) < 150:
                        # 排除明显不是标题的文本
                        if not any(skip in t for skip in ['返回', '打印', '关闭', '上一篇', '下一篇', '首页']):
                            title = t
                            self.logger.info(f'使用选择器 "{selector}" 提取标题: {title}')
                            break
                if title:
                    break
        
        if not title:
            self.logger.warning(f'⚠️  无法提取标题，跳过: {response.url}')
            return
        
        item['title'] = title
        item['source'] = '中国有色金属报'
        item['source_url'] = response.url
        item['category'] = 'nonferrous_metals'
        item['published_at'] = datetime.now()
        
        # 尝试提取发布时间
        time_selectors = [
            'span.time::text',
            'div.time::text',
            'span.date::text',
            'div.date::text',
            'div.info::text',
        ]
        
        for selector in time_selectors:
            time_text = response.css(selector).get()
            if time_text:
                try:
                    time_text = time_text.strip()
                    # 匹配日期格式
                    date_match = re.search(r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})', time_text)
                    if date_match:
                        year, month, day = date_match.groups()
                        item['published_at'] = datetime(int(year), int(month), int(day))
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
            'td.content p::text',
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
            for selector in ['div.content', 'div.article', 'div.detail', 'div.news-content', 'td.content']:
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
        tags = ['有色金属', '中国有色金属报', '碳排放']
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
