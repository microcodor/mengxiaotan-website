#!/usr/bin/env python3
"""
测试真实爬虫 - 快速检查网站是否可访问
"""
import requests
from bs4 import BeautifulSoup

# 测试网站列表
test_sites = [
    {
        'name': '北极星电力网',
        'url': 'https://news.bjx.com.cn/list/power.html',
        'spider': 'power'
    },
    {
        'name': '中国煤炭网',
        'url': 'https://www.cctd.com.cn/',
        'spider': 'coal'
    },
    {
        'name': '中国新能源网',
        'url': 'https://www.china-nengyuan.com/',
        'spider': 'newenergy'
    },
    {
        'name': '人民网能源',
        'url': 'http://energy.people.com.cn/',
        'spider': 'peopledaily'
    },
    {
        'name': '中国能源网',
        'url': 'http://www.cnenergy.org/',
        'spider': 'cnenergy'
    },
    {
        'name': '国家能源局',
        'url': 'https://www.nea.gov.cn/xwzx/nyyw.htm',
        'spider': 'nea'
    },
    {
        'name': '国家发改委',
        'url': 'https://www.ndrc.gov.cn/fggz/fgzy/',
        'spider': 'ndrc'
    },
]

print("=" * 80)
print("测试真实爬虫 - 网站可访问性检查")
print("=" * 80)
print()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for site in test_sites:
    print(f"测试 {site['name']} ({site['spider']})")
    print(f"URL: {site['url']}")
    
    try:
        response = requests.get(site['url'], headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"编码: {response.encoding}")
        print(f"内容长度: {len(response.text)} 字符")
        
        # 检查是否有链接
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        html_links = [link for link in links if '.html' in link['href'] or '.htm' in link['href']]
        
        print(f"总链接数: {len(links)}")
        print(f"HTML链接数: {len(html_links)}")
        
        if html_links:
            print(f"示例链接:")
            for link in html_links[:3]:
                title = link.get_text().strip()
                href = link['href']
                if title and len(title) > 10:
                    print(f"  - {title[:50]}")
                    print(f"    {href}")
        
        print(f"✅ 可访问")
        
    except requests.exceptions.Timeout:
        print(f"❌ 超时")
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
    
    print()
    print("-" * 80)
    print()

print("测试完成！")
