"""
全面测试内容验证规则（使用真实长度的内容）
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from crawl4ai_base import Crawl4AIBase

def test_comprehensive_validation():
    """测试各种无效内容的识别（真实长度）"""
    
    base = Crawl4AIBase("测试", "http://test.com", "test")
    
    print("="*80)
    print("全面内容验证规则测试")
    print("="*80)
    
    # 测试用例（使用真实长度的内容）
    test_cases = [
        # 1. 404页面测试（真实长度）
        {
            "name": "404页面 - HTTP Status 404（真实）",
            "content": "# HTTP Status 404 - /fggz/fgzy/202307/t20230728_1358914.html\n\n* * *\n\n**type** Status report\n\n**message** _/fggz/fgzy/202307/t20230728_1358914.html_\n\n**description** _The requested resource is not available._\n\n* * *",
            "url": "http://test.com/article/123",
            "title": "数据概览：2023年上半年就业相关数据",
            "expected": False,
            "expected_reason": "404页面"
        },
        
        # 2. 反爬验证页面测试（真实长度）
        {
            "name": "反爬验证 - 验证码（真实）",
            "content": "为了保护网站安全，请完成以下验证。\n\n请输入验证码以继续访问。\n\n" + "验证码图片显示区域\n" * 20 + "\n请在下方输入框中输入您看到的验证码。\n\n如果您无法看清验证码，请点击刷新按钮。",
            "url": "http://test.com/verify",
            "title": "安全验证",
            "expected": False,
            "expected_reason": "反爬验证"
        },
        {
            "name": "反爬验证 - Access Denied（真实）",
            "content": "Access Denied\n\nYou don't have permission to access this resource.\n\n" + "Error details:\n" * 20 + "\nPlease contact the administrator if you believe this is an error.\n\nError code: 403\nTimestamp: 2026-04-16 05:00:00",
            "url": "http://test.com/forbidden",
            "title": "Access Denied",
            "expected": False,
            "expected_reason": "反爬验证"
        },
        
        # 3. 非详情页测试（真实长度）
        {
            "name": "非详情页 - 交易数据（真实）",
            "content": "交易数据\n\n最新交易数据统计\n\n" + "日期 | 成交量 | 成交额\n2026-04-15 | 1000 | 50000\n" * 50 + "\n数据更新时间：2026-04-16 05:00:00\n\n注：以上数据仅供参考",
            "url": "http://test.com/data/trade",
            "title": "交易数据",
            "expected": False,
            "expected_reason": "非详情页"
        },
        {
            "name": "非详情页 - 市场动态（真实）",
            "content": "市场动态\n\n最新市场动态信息\n\n" + "1. 市场行情分析\n2. 价格走势预测\n3. 交易统计数据\n" * 30 + "\n更多信息请访问详情页面。",
            "url": "http://test.com/market/news",
            "title": "市场动态",
            "expected": False,
            "expected_reason": "非详情页"
        },
        
        # 4. 全是链接的页面测试（真实长度）
        {
            "name": "全是链接 - 导航页（真实）",
            "content": "网站导航\n\n" + "\n".join([f"分类{i}：http://test.com/category/{i}" for i in range(1, 21)]) + "\n\n更多链接请查看网站地图。",
            "url": "http://test.com/nav",
            "title": "网站导航",
            "expected": False,
            "expected_reason": "链接过多"
        },
        
        # 5. 正常文章测试（真实长度）
        {
            "name": "正常文章 - 能源新闻（真实）",
            "content": """国家能源局发布2026年能源工作指导意见

2026年4月15日，国家能源局正式发布《2026年能源工作指导意见》，明确了今年能源工作的总体要求和重点任务。

一、总体要求

坚持稳中求进工作总基调，完整、准确、全面贯彻新发展理念，加快构建新发展格局，着力推动高质量发展。

二、重点任务

1. 保障能源安全稳定供应
   - 加强煤炭清洁高效利用
   - 提升油气勘探开发力度
   - 优化电力供应结构

2. 推进能源绿色低碳转型
   - 大力发展可再生能源
   - 积极安全有序发展核电
   - 加快建设新型电力系统

3. 深化能源体制改革
   - 完善能源市场体系
   - 深化电力体制改革
   - 推进油气体制改革

三、保障措施

加强组织领导，完善政策支持，强化监督考核，确保各项任务落实到位。

专家表示，这些政策将对未来能源结构产生深远影响，有助于实现碳达峰碳中和目标。

（记者 张三 报道）
""",
            "url": "http://test.com/article/energy-policy-2026",
            "title": "国家能源局发布2026年能源工作指导意见",
            "expected": True,
            "expected_reason": "有效"
        },
        {
            "name": "正常文章 - 包含数字404（真实）",
            "content": """重大建设项目启动 总投资超4000万元

本报讯 4月15日，某重大建设项目正式启动。该项目总建筑面积达到174041.45平方米，预计总投资4049万元。

项目概况：
- 建筑面积：174041.45平方米
- 总投资：4049万元
- 建设周期：18个月
- 预计就业：创造404个就业岗位

项目负责人表示，该项目将采用最新的建筑技术和环保材料，力争打造成为区域标杆工程。

建设内容包括：
1. 主体建筑工程
2. 配套设施建设
3. 景观绿化工程
4. 智能化系统安装

项目建成后，将极大改善当地基础设施条件，为区域经济发展注入新动力。

当地政府高度重视该项目，多次召开专题会议研究推进工作，确保项目按期完成。

（记者 李四 报道）
""",
            "url": "http://test.com/article/construction-project",
            "title": "重大建设项目启动",
            "expected": True,
            "expected_reason": "有效"
        },
    ]
    
    # 执行测试
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print("-" * 80)
        print(f"内容长度: {len(test_case['content'])} 字符")
        
        is_valid, reason = base.is_valid_article_content(
            test_case['content'],
            test_case['url'],
            test_case['title']
        )
        
        expected = test_case['expected']
        
        if is_valid == expected:
            print(f"✅ 通过 - 验证结果: {is_valid}, 原因: {reason}")
            passed += 1
        else:
            print(f"❌ 失败 - 期望: {expected}, 实际: {is_valid}, 原因: {reason}")
            print(f"   期望原因: {test_case['expected_reason']}")
            failed += 1
    
    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"总测试数: {len(test_cases)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        print("\n验证规则已成功集成到爬虫基类中，可以在源头过滤无效数据。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
    
    return failed == 0

if __name__ == "__main__":
    success = test_comprehensive_validation()
    sys.exit(0 if success else 1)
