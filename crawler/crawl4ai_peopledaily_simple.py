"""
人民网爬虫 - Crawl4AI简化版本
使用CSS选择器提取，不需要LLM API
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy
import pymysql
import json

class PeopleDailyCrawlerSimple:
    """人民网能源频道爬虫 - 简化版"""
    
    def __init__(self):
        self.source_name = "人民网"
        self.base_url = "http://energy.people.com.cn/"
        
        # 数据库配置
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'jinchun123',
            'database': 'energy_station',
            'charset': 'utf8mb4'
        }
        
        # CSS选择器配置
        self.schema = {
            "name": "PeopleDailyArticles",
            "baseSelector": "div.w1000 ul.list_14 li, div.list_14 li",  # 文章列表项
            "fields": [
                {
                    "name": "title",
                    "selector": "a",
                    "type": "text",
                },
                {
                    "name": "url",
                    "selector": "a",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "published_date",
                    "selector": "span.date, .time",
                    "type": "text",
                }
            ]
        }
    
    async def crawl(self):
        """执行爬取"""
        print(f"🚀 开始爬取 {self.source_name}")
        print(f"📍 URL: {self.base_url}")
        
        # 配置浏览器
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False
        )
        
        # 配置CSS提取策略
        extraction_strategy = JsonCssExtractionStrategy(
            self.schema,
            verbose=True
        )
        
        # 配置爬取参数
        run_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded",  # 改为更快的等待策略
            page_timeout=60000,  # 增加到60秒
            delay_before_return_html=2.0,  # 等待2秒让内容加载
        )
        
        try:
            # 执行爬取
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print("⏳ 正在加载页面...")
                result = await crawler.arun(
                    url=self.base_url,
                    config=run_config
                )
                
                if result.success:
                    print(f"✅ 页面加载成功")
                    print(f"📄 HTML长度: {len(result.html)}")
                    print(f"📝 Markdown长度: {len(result.markdown.raw_markdown) if result.markdown else 0}")
                    
                    # 解析提取的内容
                    if result.extracted_content:
                        try:
                            articles = json.loads(result.extracted_content)
                            print(f"📊 提取到 {len(articles)} 个链接")
                            
                            # 过滤和处理文章
                            valid_articles = []
                            for article in articles:
                                if article.get('title') and article.get('url'):
                                    # 补全URL
                                    url = article['url']
                                    if url.startswith('/'):
                                        url = 'http://energy.people.com.cn' + url
                                    elif not url.startswith('http'):
                                        url = 'http://energy.people.com.cn/' + url
                                    
                                    article['url'] = url
                                    valid_articles.append(article)
                            
                            print(f"✅ 有效文章: {len(valid_articles)} 篇")
                            
                            # 爬取每篇文章的详细内容
                            saved_count = await self.crawl_article_details(crawler, valid_articles)
                            
                            print(f"✅ 成功保存 {saved_count} 篇新文章")
                            return saved_count
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失败: {e}")
                            print(f"原始内容: {result.extracted_content[:500]}")
                            
                            # 尝试使用Markdown提取链接
                            print("\n📝 尝试从Markdown提取链接...")
                            if result.markdown:
                                links = result.links.get('internal', [])
                                print(f"找到 {len(links)} 个内部链接")
                                for link in links[:5]:
                                    print(f"  - {link.get('text', 'No text')}: {link.get('href', 'No href')}")
                            
                            return 0
                    else:
                        print("⚠️  未提取到任何内容")
                        print("\n📝 Markdown预览:")
                        if result.markdown:
                            print(result.markdown.raw_markdown[:1000])
                        return 0
                else:
                    print(f"❌ 爬取失败: {result.error_message}")
                    return 0
                    
        except Exception as e:
            print(f"❌ 爬取过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    async def crawl_article_details(self, crawler, articles):
        """爬取文章详细内容"""
        saved_count = 0
        
        for i, article in enumerate(articles[:10], 1):  # 限制前10篇
            try:
                print(f"\n📖 [{i}/{min(10, len(articles))}] 爬取文章: {article['title'][:50]}")
                
                # 配置文章详情页的提取
                detail_schema = {
                    "name": "ArticleDetail",
                    "baseSelector": "body",
                    "fields": [
                        {
                            "name": "content",
                            "selector": "div.rm_txt_con, div.box_con, article",
                            "type": "text",
                        },
                        {
                            "name": "summary",
                            "selector": "div.summary, .abstract, meta[name='description']",
                            "type": "text",
                        }
                    ]
                }
                
                detail_strategy = JsonCssExtractionStrategy(detail_schema, verbose=False)
                detail_config = CrawlerRunConfig(
                    extraction_strategy=detail_strategy,
                    cache_mode=CacheMode.BYPASS,
                    page_timeout=15000,
                )
                
                result = await crawler.arun(
                    url=article['url'],
                    config=detail_config
                )
                
                if result.success and result.extracted_content:
                    detail = json.loads(result.extracted_content)
                    if isinstance(detail, list) and len(detail) > 0:
                        detail = detail[0]
                    
                    # 合并数据
                    article['content'] = detail.get('content', '')
                    article['summary'] = detail.get('summary', article['content'][:200] if article.get('content') else '')
                    
                    # 保存到数据库
                    if self.save_article(article):
                        saved_count += 1
                        print(f"  ✅ 保存成功")
                    else:
                        print(f"  ⏭️  已存在或保存失败")
                else:
                    print(f"  ⚠️  详情页爬取失败")
                
                # 避免请求过快
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ❌ 处理文章出错: {str(e)}")
                continue
        
        return saved_count
    
    def save_article(self, article):
        """保存单篇文章到数据库"""
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM articles WHERE source_url = %s",
                (article.get('url', ''),)
            )
            
            if cursor.fetchone():
                return False
            
            # 插入新文章
            sql = """
                INSERT INTO articles 
                (title, summary, content, source, source_url, category, published_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 处理发布时间
            published_at = article.get('published_date')
            if published_at:
                try:
                    # 尝试解析时间格式：2026-04-15
                    if len(published_at) == 10:
                        published_at = datetime.strptime(published_at, '%Y-%m-%d')
                    else:
                        published_at = datetime.now()
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()
            
            cursor.execute(sql, (
                article.get('title', ''),
                article.get('summary', '')[:500],  # 限制摘要长度
                article.get('content', ''),
                self.source_name,
                article.get('url', ''),
                'energy',
                published_at,
                datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"    ❌ 保存出错: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

async def main():
    """主函数"""
    crawler = PeopleDailyCrawlerSimple()
    saved_count = await crawler.crawl()
    
    print("\n" + "="*50)
    print(f"📊 爬取完成")
    print(f"✅ 新增文章: {saved_count} 篇")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
