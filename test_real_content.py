#!/usr/bin/env python3
"""
测试真实的文章内容提取
"""
import sys
sys.path.insert(0, 'crawler')

from energy_crawler.content_extractor import extractor

def test_real_article():
    """测试真实文章"""
    # 模拟一个真实的新闻页面
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>国家能源局召开能源领域氢能区域试点工作推进会</title>
        <meta name="keywords" content="能源,氢能,试点">
    </head>
    <body>
        <header>
            <nav>
                <a href="/">首页</a>
                <a href="/news">新闻</a>
                <a href="/about">关于我们</a>
            </nav>
        </header>
        
        <div class="sidebar">
            <h3>热门文章</h3>
            <ul>
                <li><a href="/article1">文章1</a></li>
                <li><a href="/article2">文章2</a></li>
            </ul>
        </div>
        
        <article>
            <h1>国家能源局召开能源领域氢能区域试点工作推进会</h1>
            <div class="meta">
                <span>来源: 国家能源局</span>
                <span>时间: 2024-04-16</span>
            </div>
            
            <div class="content">
                <p>4月15日,国家能源局在北京召开能源领域氢能区域试点工作推进会,深入学习贯彻习近平总书记关于能源安全新战略的重要论述,落实党中央、国务院决策部署,总结交流试点工作进展,研究部署下一步重点任务。</p>
                
                <p>会议指出,氢能是未来国家能源体系的重要组成部分,是用能终端实现绿色低碳转型的重要载体。开展能源领域氢能区域试点,是推动氢能产业高质量发展的重要举措。</p>
                
                <p>会议强调,各试点地区要坚持问题导向、目标导向,聚焦氢能制储运用全链条,加快突破关键核心技术,完善产业链供应链,探索形成可复制可推广的经验模式。</p>
                
                <p>会议要求,要加强组织领导,压实工作责任,强化政策支持,优化营商环境,确保试点工作取得实效。国家能源局将加强统筹协调和跟踪指导,及时总结推广试点经验。</p>
                
                <p>相关省份能源主管部门、试点地区政府负责同志,以及有关企业代表参加会议。</p>
            </div>
        </article>
        
        <div class="related">
            <h3>相关链接</h3>
            <ul>
                <li><a href="https://www.nea.gov.cn">国家能源局官网</a></li>
                <li><a href="https://www.gov.cn">中国政府网</a></li>
            </ul>
        </div>
        
        <footer>
            <p>版权所有 © 2024 国家能源局</p>
            <p>主管: 国家能源局 | 主办: 能源信息中心</p>
            <p>备案号: 京ICP备12345678号</p>
            <p><a href="/contact">联系我们</a> | <a href="/sitemap">网站地图</a></p>
        </footer>
    </body>
    </html>
    """
    
    print("="*80)
    print("测试真实文章内容提取")
    print("="*80)
    
    result = extractor.extract_content(html)
    
    print(f"\n提取结果:")
    print(f"- 成功: {result['success']}")
    print(f"- 内容长度: {len(result['content'])} 字符")
    print(f"\n提取的内容:")
    print("-"*80)
    print(result['content'])
    print("-"*80)
    
    content = result['content']
    
    # 检查链接移除
    print(f"\n✅ 链接移除检查:")
    link_checks = [
        ('http://', 'http://'),
        ('https://', 'https://'),
        ('www.', 'www.'),
        ('href=', 'href='),
        ('<a ', 'HTML链接标签'),
    ]
    
    all_clean = True
    for pattern, desc in link_checks:
        if pattern in content:
            print(f"  ❌ 仍包含 {desc}")
            all_clean = False
        else:
            print(f"  ✅ 已移除 {desc}")
    
    # 检查无关内容移除
    print(f"\n✅ 无关内容移除检查:")
    unwanted_checks = [
        ('首页', '导航-首页'),
        ('关于我们', '导航-关于我们'),
        ('热门文章', '侧边栏'),
        ('版权所有', '页脚-版权'),
        ('备案号', '页脚-备案'),
        ('主管', '页脚-主管'),
        ('主办', '页脚-主办'),
        ('联系我们', '页脚-联系'),
        ('网站地图', '页脚-网站地图'),
    ]
    
    for pattern, desc in unwanted_checks:
        if pattern in content:
            print(f"  ❌ 仍包含 {desc}")
            all_clean = False
        else:
            print(f"  ✅ 已移除 {desc}")
    
    # 检查正文保留
    print(f"\n✅ 正文内容检查:")
    wanted_checks = [
        ('4月15日', '时间信息'),
        ('国家能源局', '机构名称'),
        ('氢能', '关键词'),
        ('试点工作', '主题'),
        ('习近平总书记', '领导人'),
        ('绿色低碳', '政策方向'),
    ]
    
    for pattern, desc in wanted_checks:
        if pattern in content:
            print(f"  ✅ 保留 {desc}")
        else:
            print(f"  ⚠️  缺少 {desc}")
    
    print("\n" + "="*80)
    if all_clean and len(content) > 200:
        print("✅ 测试通过: 内容提取质量良好")
    else:
        print("⚠️  测试结果: 需要检查")
    print("="*80)

if __name__ == '__main__':
    test_real_article()
