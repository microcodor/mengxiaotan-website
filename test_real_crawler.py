#!/usr/bin/env python3
"""
测试真实爬虫 - 使用Playwright抓取国家能源局网站
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime

async def fetch_nea_news():
    """抓取国家能源局新闻"""
    print("=" * 60)
    print("  国家能源局新闻爬虫测试")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # 启动浏览器
        print("🚀 启动浏览器...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # 访问能源要闻页面
        url = 'https://www.nea.gov.cn/xwzx/nyyw.htm'
        print(f"📡 访问: {url}")
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print("✅ 页面加载完成")
            
            # 等待内容渲染
            await page.wait_for_timeout(3000)
            
            # 获取页面内容
            html = await page.content()
            print(f"📄 页面内容长度: {len(html)} 字符")
            
            # 使用BeautifulSoup解析
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找文章链接
            print("\n🔍 查找文章链接...")
            
            # 尝试多种选择器
            selectors = [
                ('ul.list li a', 'ul.list li a'),
                ('div.list-item a', 'div.list-item a'),
                ('a[href*=".html"]', 'a标签包含.html'),
                ('li a[href]', 'li下的a标签'),
            ]
            
            articles = []
            for selector, desc in selectors:
                links = soup.select(selector)
                if links:
                    print(f"  使用选择器 '{desc}' 找到 {len(links)} 个链接")
                    
                    for link in links[:10]:  # 只取前10个
                        href = link.get('href', '')
                        title = link.get_text(strip=True) or link.get('title', '')
                        
                        if href and title and len(title) > 5:
                            # 构建完整URL
                            if not href.startswith('http'):
                                if href.startswith('/'):
                                    full_url = f'https://www.nea.gov.cn{href}'
                                else:
                                    full_url = f'https://www.nea.gov.cn/xwzx/{href}'
                            else:
                                full_url = href
                            
                            articles.append({
                                'title': title,
                                'url': full_url
                            })
                    
                    if articles:
                        break
            
            print(f"\n✅ 找到 {len(articles)} 篇文章")
            print("\n" + "=" * 60)
            print("  文章列表")
            print("=" * 60)
            
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article['title']}")
                print(f"   URL: {article['url']}")
            
            # 抓取第一篇文章的详细内容
            if articles:
                print("\n" + "=" * 60)
                print("  抓取第一篇文章详情")
                print("=" * 60)
                
                first_article = articles[0]
                print(f"\n📡 访问: {first_article['url']}")
                
                try:
                    await page.goto(first_article['url'], wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    article_html = await page.content()
                    article_soup = BeautifulSoup(article_html, 'html.parser')
                    
                    # 尝试提取正文
                    content_selectors = [
                        'div.content',
                        'div.article-content',
                        'div.TRS_Editor',
                        'div#content',
                        'div.main-content',
                    ]
                    
                    content = None
                    for selector in content_selectors:
                        content_div = article_soup.select_one(selector)
                        if content_div:
                            # 提取所有段落
                            paragraphs = content_div.find_all('p')
                            if paragraphs:
                                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                                print(f"\n✅ 使用选择器 '{selector}' 提取到内容")
                                break
                    
                    if content:
                        print(f"\n📝 文章内容 (前500字):")
                        print("-" * 60)
                        print(content[:500])
                        print("-" * 60)
                        print(f"\n总长度: {len(content)} 字符")
                    else:
                        print("\n⚠️  未能提取文章内容")
                        print("页面HTML片段:")
                        print(article_html[:1000])
                
                except Exception as e:
                    print(f"\n❌ 抓取文章详情失败: {str(e)}")
        
        except Exception as e:
            print(f"\n❌ 访问页面失败: {str(e)}")
        
        finally:
            await browser.close()
            print("\n✅ 浏览器已关闭")

if __name__ == '__main__':
    asyncio.run(fetch_nea_news())
