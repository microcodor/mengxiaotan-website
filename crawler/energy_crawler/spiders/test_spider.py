import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime

class TestSpider(scrapy.Spider):
    """测试爬虫 - 生成测试数据验证流程"""
    name = 'test'
    
    def start_requests(self):
        # 生成3篇测试文章
        for i in range(3):
            yield scrapy.Request(
                url=f'http://httpbin.org/delay/1?id={i}',  # 使用不同的URL避免去重
                callback=self.parse,
                meta={'index': i},
                dont_filter=False  # 允许重复URL
            )
    
    def parse(self, response):
        index = response.meta['index']
        
        item = ArticleItem()
        item['title'] = f'测试文章 {index + 1} - {datetime.now().strftime("%H:%M:%S")}'
        item['summary'] = f'这是第{index + 1}篇测试文章的摘要，用于验证爬虫系统是否正常工作。'
        item['content'] = f'''这是第{index + 1}篇测试文章的详细内容。

本文用于测试爬虫管理系统的以下功能：
1. 爬虫启动和停止
2. 数据抓取和存储
3. 状态实时更新
4. 日志记录

测试时间：{datetime.now().isoformat()}
'''
        item['source'] = '测试数据源'
        item['source_url'] = f'http://test.example.com/article/{index + 1}'
        item['category'] = 'test'
        item['tags'] = ['测试', '爬虫', '系统验证']
        item['published_at'] = datetime.now()
        
        self.logger.info(f'✅ 成功抓取测试文章 {index + 1}')
        
        yield item
