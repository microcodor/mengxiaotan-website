import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime
import re

class XinhuaSpider(scrapy.Spider):
    """新华网 - 能源频道"""
    name = 'xinhua'
    allowed_domains = ['xinhuanet.com']
    start_urls = [
        'http://www.xinhuanet.com/energy/',  # 能源频道
        'http://www.xinhuanet.com/power/',   # 电力
    ]

    def parse(self, response):
        # 解析列表页
        articles = response.css('ul.dataList li, div.news-list li')
        
        for article in articles:
            title = article.css('a::text, h3 a::text').get()
            url = article.css('a::attr(href)').get()
            date_str = article.css('span.time::text, span::text').get()
            
            if url and title:
                if not url.startswith('http'):
                    url = response.urljoin(url)
                
                published_at = self.parse_date(date_str)
                
                yield scrapy.Request(
                    url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'published_at': published_at
                    }
                )

    def parse_article(self, response):
        item = ArticleItem()
        
        item['title'] = response.meta['title']
        item['source'] = '新华网'
        item['source_url'] = response.url
        item['category'] = 'media'
        item['published_at'] = response.meta['published_at']
        
        # 提取正文
        content_div = response.css('div#detail, div.article, div.content')
        if content_div:
            paragraphs = content_div.css('p::text').getall()
            content = '\n'.join([p.strip() for p in paragraphs if p.strip()])
            item['content'] = content
            item['summary'] = content[:200] + '...' if len(content) > 200 else content
        else:
            item['content'] = ''
            item['summary'] = ''
        
        # 提取标签
        tags = ['新华网', '能源']
        keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if keywords:
            tags.extend([k.strip() for k in keywords.split(',') if k.strip()])
        item['tags'] = list(set(tags))
        
        yield item

    def parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
        
        date_str = date_str.strip()
        patterns = [
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    return datetime.strptime(match.group(0), fmt)
                except:
                    pass
        
        return datetime.now()
