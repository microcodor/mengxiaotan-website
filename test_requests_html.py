#!/usr/bin/env python3
"""
使用requests-html测试爬虫
"""
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time

def test_crawler():
    print("=" * 60)
    print("  测试多个能源新闻网站")
    print("=" * 60)
    print()
    
    session = HTMLSession()
    
    # 测试多个网站
    test_sites = [
        {
            'name': '新华网能源',
            'url': 'http://www.news.cn/energy/',
            'list_selector': 'ul li a, div.item a',
        },
        {
            'name': '人民网能源',
            'url': 'http://energy.people.com.cn/',
            'list_selector': 'ul li a, div.list a',
        },
        {
            'name': '中国能源网',
            'url': 'http://www.cnenergy.org/',
            'list_selector': 'ul li a, div.news a',
        },
    ]
    
    all_articles = []
    
    for site in test_sites:
        print(f"\n{'='*60}")
        print(f"  {site['name']}")
        print(f"{'='*60}")
        print(f"📡 访问: {site['url']}")
        
        try:
            response = session.get(site['url'], timeout=15)
            print(f"✅ 状态码: {response.status_code}")
            print(f"📄 内容长度: {len(response.text)} 字符")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找链接
            links = soup.select('a[href]')
            print(f"🔗 找到 {len(links)} 个链接")
            
            # 筛选新闻链接
            articles = []
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # 过滤条件
                if (title and len(title) > 10 and len(title) < 100 and
                    href and ('.html' in href or '.htm' in href or '/c_' in href)):
                    
                    # 构建完整URL
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            base_url = '/'.join(site['url'].split('/')[:3])
                            full_url = base_url + href
                        else:
                            full_url = site['url'].rstrip('/') + '/' + href
                    else:
                        full_url = href
                    
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'source': site['name']
                    })
                    
                    if len(articles) >= 10:  # 每个网站最多10篇
                        break
            
            print(f"✅ 找到 {len(articles)} 篇文章")
            
            for i, article in enumerate(articles[:5], 1):  # 显示前5篇
                print(f"\n{i}. {article['title'][:50]}...")
            
            all_articles.extend(articles)
            
            time.sleep(2)  # 礼貌延迟
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"  总结")
    print(f"{'='*60}")
    print(f"✅ 总共找到 {len(all_articles)} 篇文章")
    
    # 尝试抓取一篇文章的详细内容
    if all_articles:
        print(f"\n{'='*60}")
        print(f"  测试抓取文章详情")
        print(f"{'='*60}")
        
        test_article = all_articles[0]
        print(f"\n📰 {test_article['title']}")
        print(f"📡 {test_article['url']}")
        
        try:
            response = session.get(test_article['url'], timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取正文
            content_selectors = [
                'div.content p',
                'div.article p',
                'div#content p',
                'div.main-content p',
                'article p',
            ]
            
            content = None
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs and len(paragraphs) > 2:
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    print(f"\n✅ 使用选择器 '{selector}' 提取到内容")
                    break
            
            if content:
                print(f"\n📝 文章内容 (前300字):")
                print("-" * 60)
                print(content[:300])
                print("-" * 60)
                print(f"\n总长度: {len(content)} 字符")
            else:
                print("\n⚠️  未能提取文章内容，尝试其他方法...")
                # 尝试提取所有文本
                body = soup.find('body')
                if body:
                    text = body.get_text(separator='\n', strip=True)
                    lines = [line for line in text.split('\n') if len(line) > 20]
                    if lines:
                        print(f"\n📝 页面主要内容 (前10行):")
                        for line in lines[:10]:
                            print(f"  {line[:80]}...")
        
        except Exception as e:
            print(f"\n❌ 抓取详情失败: {str(e)}")
    
    session.close()

if __name__ == '__main__':
    test_crawler()
