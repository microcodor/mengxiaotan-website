"""
网站结构分析工具
用于快速分析网站的HTML结构，找到正确的CSS选择器
"""
import requests
from bs4 import BeautifulSoup
import sys

def analyze_website(url):
    """分析网站结构"""
    print(f"\n{'='*60}")
    print(f"分析网站: {url}")
    print(f"{'='*60}\n")
    
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # 尝试多种编码
        encodings = ['utf-8', 'gb2312', 'gbk']
        for encoding in encodings:
            try:
                response.encoding = encoding
                soup = BeautifulSoup(response.text, 'html.parser')
                break
            except:
                continue
        
        print("✅ 页面加载成功\n")
        
        # 分析列表页选择器
        print("="*60)
        print("常见列表选择器分析")
        print("="*60)
        
        list_selectors = [
            'ul.list li',
            'ul.list_14 li',
            'div.list li',
            'ul.news li',
            'div.news-list li',
            'ul.news-list li',
            'div.list-item',
            'ul li a[href]',
        ]
        
        found_list = False
        for selector in list_selectors:
            items = soup.select(selector)
            if items and len(items) > 3:
                print(f"\n✅ {selector}")
                print(f"   找到: {len(items)} 个元素")
                
                # 显示前3个
                for i, item in enumerate(items[:3], 1):
                    link = item.find('a')
                    if link:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        if title and len(title) > 5:
                            print(f"   {i}. {title[:50]}")
                            print(f"      URL: {href}")
                
                found_list = True
                break
        
        if not found_list:
            print("\n⚠️  未找到常见的列表选择器")
            print("   建议：查看页面源代码，手动查找列表容器")
        
        # 分析内容页选择器
        print(f"\n{'='*60}")
        print("常见内容选择器分析")
        print("="*60)
        
        content_selectors = [
            'div.content p',
            'div.rm_txt_con p',
            'div.article p',
            'div.article-content p',
            'div.text p',
            'div#content p',
            'div.main-content p',
            'article p',
            'div.TRS_Editor p',
        ]
        
        found_content = False
        for selector in content_selectors:
            paragraphs = soup.select(selector)
            if paragraphs and len(paragraphs) > 2:
                print(f"\n✅ {selector}")
                print(f"   找到: {len(paragraphs)} 个段落")
                
                # 显示第一段
                first_p = paragraphs[0].get_text(strip=True)
                if first_p:
                    print(f"   第一段: {first_p[:100]}...")
                
                found_content = True
                break
        
        if not found_content:
            print("\n⚠️  未找到常见的内容选择器")
            print("   建议：访问一篇文章，查看源代码，手动查找内容容器")
        
        # 分析日期选择器
        print(f"\n{'='*60}")
        print("常见日期选择器分析")
        print("="*60)
        
        date_selectors = [
            '.date',
            '.time',
            'span.date',
            'span.time',
            'div.time',
            'div.date',
            'div.info span',
            'div.box01 div.fl',
        ]
        
        found_date = False
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                if date_text and len(date_text) > 5:
                    print(f"\n✅ {selector}")
                    print(f"   日期: {date_text}")
                    found_date = True
                    break
        
        if not found_date:
            print("\n⚠️  未找到常见的日期选择器")
            print("   建议：日期可能在文章内容中，使用正则表达式提取")
        
        # 生成爬虫代码模板
        print(f"\n{'='*60}")
        print("建议的爬虫代码")
        print("="*60)
        
        if found_list:
            print(f"""
# 列表页选择器
self.list_schema = {{
    "name": "Articles",
    "baseSelector": "{selector}",  # 使用上面找到的选择器
    "fields": [
        {{
            "name": "title",
            "selector": "a",
            "type": "text",
        }},
        {{
            "name": "url",
            "selector": "a",
            "type": "attribute",
            "attribute": "href"
        }},
        {{
            "name": "published_date",
            "selector": ".date, .time",
            "type": "text",
        }}
    ]
}}
""")
        
        if found_content:
            print(f"""
# 详情页选择器
self.detail_schema = {{
    "name": "Article",
    "baseSelector": "body",
    "fields": [
        {{
            "name": "content",
            "selector": "{selector}",  # 使用上面找到的选择器
            "type": "text",
            "all": True
        }}
    ]
}}
""")
        
        print(f"\n{'='*60}")
        print("分析完成")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("\n用法: python analyze_website.py <URL>")
        print("\n示例:")
        print("  python analyze_website.py http://finance.people.com.cn/")
        print("  python analyze_website.py https://www.nea.gov.cn/xwzx/nyyw.htm")
        print("  python analyze_website.py https://www.china5e.com/news/\n")
        sys.exit(1)
    
    url = sys.argv[1]
    analyze_website(url)

if __name__ == "__main__":
    main()
