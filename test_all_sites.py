#!/usr/bin/env python3
"""
测试所有目标网站的可访问性和结构
"""
import requests
from bs4 import BeautifulSoup
import time

def test_site(name, url, description):
    """测试单个网站"""
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")
    print(f"📡 URL: {url}")
    print(f"📝 说明: {description}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ 状态码: {response.status_code}")
        print(f"📄 内容长度: {len(response.text)} 字符")
        print(f"🔤 编码: {response.encoding}")
        
        # 检查是否是动态网站
        if 'vue' in response.text.lower() or 'react' in response.text.lower() or 'angular' in response.text.lower():
            print("⚠️  检测到前端框架，可能需要JavaScript渲染")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找新闻链接
        links = soup.find_all('a', href=True)
        news_links = [link for link in links if link.get_text(strip=True) and len(link.get_text(strip=True)) > 10]
        print(f"🔗 找到 {len(links)} 个链接，其中 {len(news_links)} 个可能是新闻")
        
        # 显示前5个新闻链接
        if news_links:
            print("\n前5个新闻链接示例:")
            for i, link in enumerate(news_links[:5], 1):
                title = link.get_text(strip=True)[:60]
                href = link.get('href', '')[:80]
                print(f"  {i}. {title}...")
                print(f"     {href}")
        
        # 检查常见的新闻列表选择器
        selectors = [
            ('ul.list li', 'ul.list li'),
            ('div.news-list', 'div.news-list'),
            ('div.article-list', 'div.article-list'),
            ('ul.news li', 'ul.news li'),
            ('div.list-item', 'div.list-item'),
        ]
        
        print("\n🔍 测试常见选择器:")
        for selector, desc in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✅ {desc}: 找到 {len(elements)} 个元素")
        
        return {
            'status': 'success',
            'status_code': response.status_code,
            'content_length': len(response.text),
            'news_links': len(news_links),
            'encoding': response.encoding
        }
        
    except requests.exceptions.Timeout:
        print("❌ 超时：网站响应时间过长")
        return {'status': 'timeout'}
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误：无法连接到网站")
        return {'status': 'connection_error'}
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def main():
    """测试所有目标网站"""
    print("="*70)
    print("  能源新闻网站可访问性测试")
    print("="*70)
    
    sites = [
        {
            'name': '国家能源局',
            'url': 'https://www.nea.gov.cn/xwzx/nyyw.htm',
            'description': '能源要闻'
        },
        {
            'name': '国家发改委',
            'url': 'https://www.ndrc.gov.cn/fggz/fgzy/',
            'description': '发展改革工作'
        },
        {
            'name': '人民网能源',
            'url': 'http://energy.people.com.cn/',
            'description': '人民网能源频道'
        },
        {
            'name': '新华网能源',
            'url': 'http://www.news.cn/energy/',
            'description': '新华网能源频道（已验证可用）'
        },
        {
            'name': '中国能源网',
            'url': 'http://www.cnenergy.org/',
            'description': '综合能源资讯'
        },
        {
            'name': '北极星电力网',
            'url': 'https://news.bjx.com.cn/list/power.html',
            'description': '电力新闻'
        },
        {
            'name': '中国煤炭网',
            'url': 'http://www.coalchina.org.cn/',
            'description': '煤炭行业资讯'
        },
        {
            'name': '中国电力网',
            'url': 'http://www.chinapower.com.cn/',
            'description': '电力行业资讯'
        },
        {
            'name': '光伏们',
            'url': 'https://www.pvmen.com/',
            'description': '光伏行业资讯'
        },
        {
            'name': '风能专委会',
            'url': 'http://www.cwea.org.cn/',
            'description': '风电行业资讯'
        },
    ]
    
    results = {}
    
    for site in sites:
        result = test_site(site['name'], site['url'], site['description'])
        results[site['name']] = result
        time.sleep(2)  # 礼貌延迟
    
    # 总结
    print(f"\n{'='*70}")
    print("  测试总结")
    print(f"{'='*70}")
    
    success_sites = [name for name, result in results.items() if result.get('status') == 'success']
    failed_sites = [name for name, result in results.items() if result.get('status') != 'success']
    
    print(f"\n✅ 可访问网站 ({len(success_sites)}):")
    for name in success_sites:
        result = results[name]
        print(f"  - {name}: {result.get('news_links', 0)} 个新闻链接")
    
    if failed_sites:
        print(f"\n❌ 无法访问网站 ({len(failed_sites)}):")
        for name in failed_sites:
            result = results[name]
            print(f"  - {name}: {result.get('status', 'unknown')}")
    
    print(f"\n{'='*70}")
    print("  推荐方案")
    print(f"{'='*70}")
    
    print("""
1. 新华网能源 ✅ - 使用 Scrapy（已实现）
   - 网站结构清晰
   - 无需JavaScript渲染
   - 推荐作为主要数据源

2. 人民网能源 - 使用 Scrapy + 特殊处理
   - 可能需要处理重定向
   - 建议使用Selenium备用

3. 北极星电力网 - 使用 Scrapy
   - 行业专业网站
   - 内容丰富

4. 国家能源局/发改委 - 使用 Playwright/Selenium
   - 动态渲染网站
   - 需要JavaScript支持

5. 其他网站 - 根据测试结果选择方案
   - 优先使用Scrapy
   - 必要时使用Playwright
    """)

if __name__ == '__main__':
    main()
