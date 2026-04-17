"""
测试日期检测功能（简化版，不依赖crawl4ai）
验证日期提取逻辑
"""
import re
from datetime import datetime, date, timedelta
import pytz

class SimpleDateTester:
    """简化的日期测试类"""
    
    def __init__(self):
        self.china_tz = pytz.timezone('Asia/Shanghai')
    
    def get_today_date(self):
        """获取今天的日期（中国时区）"""
        return datetime.now(self.china_tz).date()
    
    def extract_date_from_content(self, content, title=''):
        """从内容中提取发布日期"""
        if not content:
            return None
        
        # 合并标题和内容前2000字符用于日期提取
        text = (title + '\n' + content[:2000])
        
        today = self.get_today_date()
        
        # 日期格式模式（按优先级排序）
        date_patterns = [
            # ISO格式: 2026-04-16
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 中文格式: 2026年04月16日
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 斜杠格式: 2026/04/16
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 点号格式: 2026.04.16
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 今天、今日
            (r'今[天日]', lambda m: today),
            
            # 时间戳格式: 2026-04-16 10:30:00
            (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+\d{1,2}:\d{1,2}', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        ]
        
        # 尝试匹配各种日期格式
        for pattern, converter in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    extracted_date = converter(match)
                    # 验证日期是否合理（不能是未来日期，不能太久远）
                    if extracted_date <= today and (today - extracted_date).days < 365:
                        return extracted_date
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    def is_today_article(self, content, title=''):
        """检查是否是今天的文章"""
        extracted_date = self.extract_date_from_content(content, title)
        today = self.get_today_date()
        
        if extracted_date:
            is_today = extracted_date == today
            return is_today, extracted_date
        
        # 如果无法提取日期，返回None表示不确定
        return None, None

def test_date_extraction():
    """测试日期提取功能"""
    print("="*60)
    print("测试日期提取功能")
    print("="*60)
    
    # 创建测试实例
    tester = SimpleDateTester()
    
    # 获取今天和昨天的日期
    today = tester.get_today_date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n今天日期（中国时区）: {today}")
    print(f"昨天日期: {yesterday}\n")
    
    # 测试用例
    test_cases = [
        # (内容, 标题, 期望日期, 描述)
        (
            f"发布时间：{today.strftime('%Y-%m-%d')} 10:30:00\n这是一篇测试文章",
            "测试文章",
            today,
            "ISO格式日期"
        ),
        (
            f"发布时间：{today.strftime('%Y年%m月%d日')}\n这是一篇测试文章",
            "测试文章",
            today,
            "中文格式日期"
        ),
        (
            f"发布时间：{today.strftime('%Y/%m/%d')}\n这是一篇测试文章",
            "测试文章",
            today,
            "斜杠格式日期"
        ),
        (
            f"发布时间：{today.strftime('%Y.%m.%d')}\n这是一篇测试文章",
            "测试文章",
            today,
            "点号格式日期"
        ),
        (
            "发布时间：今天 10:30\n这是一篇测试文章",
            "测试文章",
            today,
            "今天关键词"
        ),
        (
            "发布时间：今日 10:30\n这是一篇测试文章",
            "测试文章",
            today,
            "今日关键词"
        ),
        (
            f"发布时间：{yesterday.strftime('%Y-%m-%d')} 10:30:00\n这是一篇测试文章",
            "测试文章",
            yesterday,
            "昨天的文章"
        ),
        (
            "这是一篇没有日期的文章内容",
            "测试文章",
            None,
            "无日期信息"
        ),
        (
            f"标题中的日期：{today.strftime('%Y-%m-%d')}",
            f"测试文章 {today.strftime('%Y-%m-%d')}",
            today,
            "标题中的日期"
        ),
        (
            f"""
            <div class="article-info">
                <span class="author">作者：张三</span>
                <span class="date">{today.strftime('%Y-%m-%d')} 15:30</span>
            </div>
            <div class="content">
                这是文章正文内容...
            </div>
            """,
            "测试文章",
            today,
            "HTML格式中的日期"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for i, (content, title, expected_date, description) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {description}")
        print(f"  内容预览: {content[:50]}...")
        
        extracted_date = tester.extract_date_from_content(content, title)
        
        if extracted_date == expected_date:
            print(f"  ✅ 通过 - 提取日期: {extracted_date}")
            passed += 1
        else:
            print(f"  ❌ 失败 - 期望: {expected_date}, 实际: {extracted_date}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"日期提取测试结果: {passed}/{len(test_cases)} 通过")
    print(f"{'='*60}\n")
    
    return passed, failed

def test_today_article_detection():
    """测试当日文章检测功能"""
    print("="*60)
    print("测试当日文章检测功能")
    print("="*60)
    
    # 创建测试实例
    tester = SimpleDateTester()
    
    # 获取今天和昨天的日期
    today = tester.get_today_date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n今天日期（中国时区）: {today}\n")
    
    # 测试用例
    test_cases = [
        # (内容, 标题, 期望结果, 描述)
        (
            f"发布时间：{today.strftime('%Y-%m-%d')} 10:30:00\n这是一篇测试文章",
            "测试文章",
            True,
            "今天的文章"
        ),
        (
            f"发布时间：{yesterday.strftime('%Y-%m-%d')} 10:30:00\n这是一篇测试文章",
            "测试文章",
            False,
            "昨天的文章"
        ),
        (
            "发布时间：今天 10:30\n这是一篇测试文章",
            "测试文章",
            True,
            "今天关键词"
        ),
        (
            "这是一篇没有日期的文章内容",
            "测试文章",
            None,
            "无日期信息（不确定）"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for i, (content, title, expected_result, description) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {description}")
        
        is_today, article_date = tester.is_today_article(content, title)
        
        if is_today == expected_result:
            print(f"  ✅ 通过 - 是否当日: {is_today}, 文章日期: {article_date}")
            passed += 1
        else:
            print(f"  ❌ 失败 - 期望: {expected_result}, 实际: {is_today}, 文章日期: {article_date}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"当日文章检测测试结果: {passed}/{len(test_cases)} 通过")
    print(f"{'='*60}\n")
    
    return passed, failed

def test_real_article_samples():
    """测试真实文章样本"""
    print("="*60)
    print("测试真实文章样本")
    print("="*60)
    
    tester = SimpleDateTester()
    today = tester.get_today_date()
    
    # 真实文章样本（模拟）
    samples = [
        {
            "title": "国家能源局：2026年一季度全国能源消费稳步增长",
            "content": """
            来源：人民网-能源频道
            2026年04月16日08:30
            
            人民网北京4月16日电 (记者杜燕飞)国家能源局近日发布数据显示，
            2026年一季度，全国能源消费稳步增长，能源供应保障有力...
            """,
            "expected": True,
            "description": "人民网今日文章"
        },
        {
            "title": "中国能源报：新能源汽车产业发展迅速",
            "content": """
            发布时间：2026-04-16 09:15:00
            来源：中国能源报
            
            本报讯（记者 李明）随着技术进步和政策支持，
            我国新能源汽车产业发展迅速...
            """,
            "expected": True,
            "description": "中国能源报今日文章"
        },
        {
            "title": "昨日能源市场回顾",
            "content": """
            发布时间：2026-04-15 18:00:00
            
            昨日，国际原油价格小幅上涨...
            """,
            "expected": False,
            "description": "昨天的文章"
        },
        {
            "title": "能源数据中心",
            "content": """
            欢迎访问能源数据中心
            
            这里提供最新的能源统计数据、市场行情等信息。
            请选择您需要查询的数据类型...
            """,
            "expected": None,
            "description": "无日期的导航页"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, sample in enumerate(samples, 1):
        print(f"\n测试 {i}: {sample['description']}")
        print(f"  标题: {sample['title']}")
        
        is_today, article_date = tester.is_today_article(
            sample['content'],
            sample['title']
        )
        
        expected = sample['expected']
        
        if is_today == expected:
            print(f"  ✅ 通过 - 是否当日: {is_today}, 文章日期: {article_date}")
            passed += 1
        else:
            print(f"  ❌ 失败 - 期望: {expected}, 实际: {is_today}, 文章日期: {article_date}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"真实样本测试结果: {passed}/{len(samples)} 通过")
    print(f"{'='*60}\n")
    
    return passed, failed

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("日期检测功能测试套件")
    print("="*60 + "\n")
    
    total_passed = 0
    total_failed = 0
    
    # 测试1: 日期提取
    passed, failed = test_date_extraction()
    total_passed += passed
    total_failed += failed
    
    # 测试2: 当日文章检测
    passed, failed = test_today_article_detection()
    total_passed += passed
    total_failed += failed
    
    # 测试3: 真实文章样本
    passed, failed = test_real_article_samples()
    total_passed += passed
    total_failed += failed
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"✅ 通过: {total_passed}")
    print(f"❌ 失败: {total_failed}")
    print(f"📊 通过率: {total_passed/(total_passed+total_failed)*100:.1f}%")
    print("="*60 + "\n")
    
    return total_failed == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
