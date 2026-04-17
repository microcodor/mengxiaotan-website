"""
测试内容验证规则
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from crawl4ai_base import Crawl4AIBase

def test_validation():
    """测试各种无效内容的识别"""
    
    # 创建基类实例用于测试
    base = Crawl4AIBase("测试", "http://test.com", "test")
    
    print("="*80)
    print("内容验证规则测试")
    print("="*80)
    
    # 测试用例
    test_cases = [
        # 1. 404页面测试
        {
            "name": "404页面 - HTTP Status 404",
            "content": "# HTTP Status 404 - /fggz/fgzy/202307/t20230728_1358914.html\n**type** Status report\n**message** _/fggz/fgzy/202307/t20230728_1358914.html_\n**description** _The requested resource is not available._",
            "url": "http://test.com/article/123",
            "title": "数据概览：2023年上半年就业相关数据",
            "expected": False
        },
        {
            "name": "404页面 - 页面不存在",
            "content": "抱歉，您访问的页面不存在。404 Not Found。请返回首页。",
            "url": "http://test.com/article/456",
            "title": "测试文章",
            "expected": False
        },
        
        # 2. 反爬验证页面测试
        {
            "name": "反爬验证 - 验证码",
            "content": "请输入验证码以继续访问。为了保护网站安全，请完成以下验证。",
            "url": "http://test.com/article/789",
            "title": "测试文章",
            "expected": False
        },
        {
            "name": "反爬验证 - Access Denied",
            "content": "Access Denied. You don't have permission to access this resource. Please contact administrator.",
            "url": "http://test.com/article/101",
            "title": "测试文章",
            "expected": False
        },
        {
            "name": "反爬验证 - CAPTCHA",
            "content": "Please complete the CAPTCHA below to verify you are a human and not a robot.",
            "url": "http://test.com/article/102",
            "title": "测试文章",
            "expected": False
        },
        
        # 3. 非详情页测试
        {
            "name": "非详情页 - 交易数据",
            "content": "交易数据\n最新交易数据统计\n日期 | 成交量 | 成交额\n2026-04-15 | 1000 | 50000",
            "url": "http://test.com/data/trade",
            "title": "交易数据",
            "expected": False
        },
        {
            "name": "非详情页 - 市场动态",
            "content": "市场动态\n最新市场动态信息\n1. 市场行情\n2. 价格走势\n3. 交易统计",
            "url": "http://test.com/market/news",
            "title": "市场动态",
            "expected": False
        },
        {
            "name": "非详情页 - 关于我们",
            "content": "关于我们\n公司简介\n联系方式\n地址：北京市朝阳区\n电话：010-12345678",
            "url": "http://test.com/about",
            "title": "关于我们",
            "expected": False
        },
        
        # 4. 全是链接的页面测试
        {
            "name": "全是链接 - 导航页",
            "content": "导航\nhttp://test.com/1\nhttp://test.com/2\nhttp://test.com/3\nhttp://test.com/4\nhttp://test.com/5\nhttp://test.com/6\nhttp://test.com/7\nhttp://test.com/8\nhttp://test.com/9\nhttp://test.com/10\nhttp://test.com/11\nhttp://test.com/12",
            "url": "http://test.com/nav",
            "title": "导航页",
            "expected": False
        },
        
        # 5. 内容太短测试
        {
            "name": "内容太短",
            "content": "这是一篇很短的文章。",
            "url": "http://test.com/article/short",
            "title": "短文章",
            "expected": False
        },
        
        # 6. 正常文章测试
        {
            "name": "正常文章 - 新闻",
            "content": "这是一篇正常的新闻文章。" * 50 + "\n文章内容详细描述了最新的能源政策变化，包括可再生能源发展规划、碳排放控制目标等重要内容。专家表示，这些政策将对未来能源结构产生深远影响。",
            "url": "http://test.com/article/news123",
            "title": "能源政策重大调整",
            "expected": True
        },
        {
            "name": "正常文章 - 包含数字404但不是错误",
            "content": "该项目总建筑面积达到174041.45平方米，预计投资4049万元。" * 20 + "\n项目建设周期为18个月，将为当地创造大量就业机会。",
            "url": "http://test.com/article/project",
            "title": "重大建设项目启动",
            "expected": True
        },
    ]
    
    # 执行测试
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print("-" * 80)
        
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
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
    
    return failed == 0

if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)
