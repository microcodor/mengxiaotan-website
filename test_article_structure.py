#!/usr/bin/env python3
"""
测试文章页面结构
"""
import requests
from bs4 import BeautifulSoup

url = 'http://paper.cnmn.com.cn/Content.aspx?id=198770&q=5269&v=1'

print(f"正在访问: {url}")
response = requests.get(url, timeout=10, allow_redirects=True)
print(f"最终URL: {response.url}")
print(f"状态码: {response.status_code}")

# 尝试不同的编码
for encoding in ['gbk', 'gb2312', 'utf-8']:
    try:
        response.encoding = encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 测试编码是否正确
        test_text = soup.get_text()[:200]
        if '�' in test_text or len(test_text) < 50:
            continue  # 编码错误，尝试下一个
        
        # 查找所有可能包含标题的标签
        print(f"\n=== 使用编码: {encoding} ===")
        
        # 查找 h1-h3
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                print(f"\n{tag.upper()} 标签:")
                for elem in elements[:3]:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        print(f"  {text[:100]}")
        
        # 查找包含 title 的 class 或 id
        for attr in ['class', 'id']:
            elements = soup.find_all(attrs={attr: lambda x: x and 'title' in str(x).lower()})
            if elements:
                print(f"\n包含 'title' 的 {attr}:")
                for elem in elements[:3]:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        print(f"  {elem.name}.{elem.get(attr)}: {text[:100]}")
        
        # 查找 table 中的内容（数字报常用表格布局）
        tables = soup.find_all('table')
        if tables:
            print(f"\n找到 {len(tables)} 个表格")
            for i, table in enumerate(tables[:2]):
                tds = table.find_all('td')
                for td in tds[:5]:
                    text = td.get_text(strip=True)
                    if text and 10 < len(text) < 200:
                        print(f"  表格{i+1} TD: {text[:100]}")
        
        break  # 如果成功解析就退出
        
    except Exception as e:
        print(f"编码 {encoding} 失败: {e}")
        continue
