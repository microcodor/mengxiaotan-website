import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime
import re

class XinhuaEnergySpider(scrapy.Spider):
    """新华网能源频道爬虫"""
    name = 'xinhua'
    allowed_domains = ['xinhuanet.com']
    start_urls = [
        'http://www.news.cn/energy/',  # 新华网能源频道
    ]

    def parse(self, response):
        # 新华网使用标准的HTML结构
        articles = response.css('ul.dataList li, div.item')
        
        count = 0
        for article in articles:
            # 提取标题和链接
            link = article.css('a::attr(href)').get()
            title = article.css('a::text, h3::text, .tit::text').get()
            
            if link and title:
                title = title.strip()
                if not link.startswith('http'):
                    link = response.urljoin(link)
                
                # 提取日期
                date_text = article.css('.time::text, .date::text, span.time::text').get()
                published_at = self.parse_date(date_text) if date_text else datetime.now()
                
                count += 1
                yield scrapy.Request(
                    link,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'published_at': published_at
                    }
                )
        
        self.logger.info(f'在列表页找到 {count} 篇文章')
        
        # 翻页
        next_page = response.css('a.next::attr(href), a:contains("下一页")::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '新华网'
        item['source_url'] = response.url
        item['category'] = 'energy'
        item['published_at'] = response.meta['published_at']
        
        # 提取正文 - 新华网的文章结构
        content_selectors = [
            '#detail p::text',
            '.article p::text',
            '#content p::text',
            '.main-content p::text'
        ]
        
        content_parts = []
        for selector in content_selectors:
            parts = response.css(selector).getall()
            if parts:
                content_parts = parts
                break
        
        if content_parts:
            content = '\n'.join([p.strip() for p in content_parts if p.strip()])
            item['content'] = content
            item['summary'] = content[:200] + '...' if len(content) > 200 else content
        else:
            item['content'] = ''
            item['summary'] = ''
        
        # 提取标签
        tags = ['能源', '新华网']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()])
        item['tags'] = tags[:5]  # 限制标签数量
        
        if item['content']:
            self.logger.info(f'✅ 成功抓取: {item["title"]}')
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
