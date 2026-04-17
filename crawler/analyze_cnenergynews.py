"""
详细分析中国能源报网站
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.cnenergynews.cn/"

print(f"\n{'='*80}")
print(f"分析网站: {url}")
print(f"{'='*80}\n")

# 获取页面
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

if response.status_code == 200:
    print(f"✅ 页面加载成功\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有链接
    print(f"{'='*80}")
    print(f"所有链接分析")
    print(f"{'='*80}\n")
    
    links = soup.find_all('a', href=True)
    print(f"总链接数: {len(links)}\n")
    
    # 分类链接
    article_links = []
    nav_links = []
    other_links = []
    
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # 判断是否是文章链接
        if '/article/' in href or '/news/' in href or '/content/' in href:
            article_links.append((text, href))
        elif href.startswith('#') or href == '/' or href == url:
            nav_links.append((text, href))
        else:
            other_links.append((text, href))
    
    print(f"文章链接: {len(article_links)} 个")
    if article_links:
        print("示例:")
        for text, href in article_links[:5]:
            print(f"  - {text[:30]:<30} | {href}")
    
    print(f"\n导航链接: {len(nav_links)} 个")
    if nav_links:
        print("示例:")
        for text, href in nav_links[:5]:
            print(f"  - {text[:30]:<30} | {href}")
    
    print(f"\n其他链接: {len(other_links)} 个")
    if other_links:
        print("示例:")
        for text, href in other_links[:10]:
            print(f"  - {text[:30]:<30} | {href}")
    
    # 查找特定的容器
    print(f"\n{'='*80}")
    print(f"查找文章容器")
    print(f"{'='*80}\n")
    
    # 常见的文章列表容器
    containers = [
        ('div.news-list', 'div.news-list'),
        ('ul.article-list', 'ul.article-list'),
        ('div.article-item', 'div.article-item'),
        ('div.list-item', 'div.list-item'),
        ('div.box01', 'div.box01'),
        ('div.main-content', 'div.main-content'),
    ]
    
    for name, selector in containers:
        parts = selector.split('.')
        if len(parts) == 2:
            tag, class_name = parts
            elements = soup.find_all(tag, class_=class_name)
        else:
            elements = soup.find_all(selector)
        
        if elements:
            print(f"✅ {name}: {len(elements)} 个")
            # 查看第一个元素的内容
            if elements:
                first = elements[0]
                links_in_container = first.find_all('a', href=True)
                print(f"   包含链接: {len(links_in_container)} 个")
                if links_in_container:
                    print(f"   示例:")
                    for link in links_in_container[:3]:
                        print(f"     - {link.get_text(strip=True)[:40]:<40} | {link.get('href')}")
        else:
            print(f"❌ {name}: 未找到")
    
    # 检查是否是动态加载
    print(f"\n{'='*80}")
    print(f"检查动态加载")
    print(f"{'='*80}\n")
    
    # 查找script标签
    scripts = soup.find_all('script')
    has_vue = any('vue' in str(script).lower() for script in scripts)
    has_react = any('react' in str(script).lower() for script in scripts)
    has_ajax = any('ajax' in str(script).lower() or 'fetch' in str(script).lower() for script in scripts)
    
    print(f"Vue.js: {'✅ 是' if has_vue else '❌ 否'}")
    print(f"React: {'✅ 是' if has_react else '❌ 否'}")
    print(f"AJAX/Fetch: {'✅ 是' if has_ajax else '❌ 否'}")
    
    if has_vue or has_react or has_ajax:
        print(f"\n⚠️  网站使用动态加载，需要使用Scrapy + Playwright")
    else:
        print(f"\n✅ 网站使用静态HTML，可以使用Crawl4AI")

else:
    print(f"❌ 页面加载失败: {response.status_code}")
