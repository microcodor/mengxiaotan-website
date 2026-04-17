#!/usr/bin/env python3
"""
快速测试 cnmn_paper 爬虫修复
"""
import requests
from bs4 import BeautifulSoup

url = 'https://paper.cnmn.com.cn/'

print(f"正在访问: {url}")
response = requests.get(url, timeout=10)
response.encoding = 'gb2312'

soup = BeautifulSoup(response.text, 'html.parser')

# 查找 AREA 标签
area_tags = soup.find_all('area', href=True)
print(f"\n找到 {len(area_tags)} 个 AREA 标签")

content_links = []
for area in area_tags:
    href = area.get('href', '')
    if 'Content.aspx' in href:
        content_links.append(href)
        print(f"  ✓ {href}")

print(f"\n总共找到 {len(content_links)} 个文章链接")

if content_links:
    print("\n✅ 修复成功！爬虫应该能够抓取文章了")
    print(f"\n测试访问第一篇文章: {content_links[0]}")
    
    try:
        article_response = requests.get(content_links[0], timeout=10)
        article_response.encoding = 'gb2312'
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        
        # 尝试提取标题
        title = None
        for tag in ['h1', 'h2']:
            title_tag = article_soup.find(tag)
            if title_tag:
                title = title_tag.get_text(strip=True)
                break
        
        if title:
            print(f"  标题: {title}")
        else:
            print("  ⚠️  未找到标题，可能需要进一步调整解析逻辑")
            
    except Exception as e:
        print(f"  ❌ 访问文章失败: {e}")
else:
    print("\n❌ 未找到文章链接，需要进一步检查")
