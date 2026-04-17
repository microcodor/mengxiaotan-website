#!/usr/bin/env python3
"""
测试智能内容提取器 - 验证链接过滤
"""
import sys
sys.path.insert(0, 'crawler')

from energy_crawler.content_extractor import extractor

def test_link_removal():
    """测试链接移除功能"""
    # 包含各种链接的HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>测试文章</title>
    </head>
    <body>
        <nav>
            <a href="/">首页</a>
            <a href="/about">关于我们</a>
        </nav>
        <article>
            <h1>这是文章标题</h1>
            <div class="content">
                <p>这是文章的第一段内容。访问我们的网站 https://www.example.com 了解更多。</p>
                <p>这是第二段。<a href="https://link.com">点击这里</a>查看详情。</p>
                <p>这是第三段。更多信息请访问 www.example.com 或发送邮件。</p>
                <p>这是第四段。[查看详情](https://www.example.com/detail) 了解更多。</p>
                <p>这是第五段正常内容,没有任何链接。</p>
                <img src="https://example.com/image.jpg" alt="图片">
                <p>这是第六段正常内容。</p>
            </div>
        </article>
        <footer>
            <p>版权所有 © 2024 | <a href="/contact">联系我们</a></p>
            <p>备案号: 京ICP备12345678号</p>
            <p>主管: 人民日报 | 主办: 某某有限公司</p>
        </footer>
    </body>
    </html>
    """
    
    print("="*80)
    print("测试链接移除功能")
    print("="*80)
    
    result = extractor.extract_content(html)
    
    print(f"\n提取结果:")
    print(f"- 成功: {result['success']}")
    print(f"- 内容长度: {len(result['content'])} 字符")
    print(f"\n提取的内容:")
    print("-"*80)
    print(result['content'])
    print("-"*80)
    
    # 检查是否移除了链接
    content = result['content']
    
    print(f"\n链接移除检查:")
    link_patterns = ['http://', 'https://', 'www.', 'href=', '<a ', '</a>', '[', '](']
    
    all_clean = True
    for pattern in link_patterns:
        if pattern in content:
            print(f"  ❌ 仍包含: {pattern}")
            all_clean = False
        else:
            print(f"  ✅ 已移除: {pattern}")
    
    # 检查是否移除了无关内容
    print(f"\n无关内容移除检查:")
    unwanted = ['首页', '关于我们', '版权所有', '备案号', '主管', '主办', '联系我们']
    
    for text in unwanted:
        if text in content:
            print(f"  ❌ 仍包含: {text}")
            all_clean = False
        else:
            print(f"  ✅ 已移除: {text}")
    
    # 检查是否保留了正文
    print(f"\n正文保留检查:")
    wanted = ['第一段内容', '第二段', '第三段', '第四段', '第五段', '第六段']
    
    for text in wanted:
        if text in content:
            print(f"  ✅ 保留: {text}")
        else:
            print(f"  ❌ 丢失: {text}")
            all_clean = False
    
    print("\n" + "="*80)
    if all_clean:
        print("✅ 测试通过: 所有链接和无关内容已移除,正文完整保留")
    else:
        print("❌ 测试失败: 仍有问题需要修复")
    print("="*80)

if __name__ == '__main__':
    test_link_removal()
