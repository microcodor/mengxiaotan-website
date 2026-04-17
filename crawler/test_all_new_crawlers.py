"""
测试所有新迁移的Crawl4AI爬虫
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入所有新爬虫
from crawl4ai_nea import NeaCrawler
from crawl4ai_xinhua import XinhuaCrawler
from crawl4ai_chinapower import ChinaPowerCrawler
from crawl4ai_bjx_power import BjxPowerCrawler
from crawl4ai_coal import CoalCrawler
from crawl4ai_newenergy import NewEnergyCrawler

async def test_crawler(crawler_class, name, max_articles=3):
    """测试单个爬虫"""
    print(f"\n{'='*60}")
    print(f"测试爬虫: {name}")
    print(f"{'='*60}")
    
    try:
        crawler = crawler_class()
        saved_count = await crawler.crawl(max_articles=max_articles)
        
        print(f"\n✅ {name} 测试完成")
        print(f"   保存文章数: {saved_count}")
        
        return True, saved_count
    except Exception as e:
        print(f"\n❌ {name} 测试失败")
        print(f"   错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("批量测试新迁移的Crawl4AI爬虫")
    print("="*60)
    print("\n测试配置:")
    print("  - 每个爬虫限制: 3篇文章")
    print("  - 自动日期检测: 开启")
    print("  - 内容验证: 开启")
    print("")
    
    # 定义要测试的爬虫
    crawlers = [
        (NeaCrawler, "国家能源局"),
        (XinhuaCrawler, "新华网"),
        (ChinaPowerCrawler, "中国电力网"),
        (BjxPowerCrawler, "北极星电力网"),
        (CoalCrawler, "中国煤炭市场网"),
        (NewEnergyCrawler, "中国新能源网"),
    ]
    
    results = []
    total_saved = 0
    
    for crawler_class, name in crawlers:
        success, saved_count = await test_crawler(crawler_class, name, max_articles=3)
        results.append((name, success, saved_count))
        total_saved += saved_count
        
        # 避免请求过快
        await asyncio.sleep(2)
    
    # 输出测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    success_count = sum(1 for _, success, _ in results if success)
    
    print(f"\n测试爬虫数: {len(crawlers)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(crawlers) - success_count}")
    print(f"总保存文章数: {total_saved}")
    print(f"\n详细结果:")
    
    for name, success, saved_count in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {status} - {name}: {saved_count}篇")
    
    print("\n" + "="*60)
    
    if success_count == len(crawlers):
        print("🎉 所有爬虫测试通过！")
    else:
        print(f"⚠️  {len(crawlers) - success_count} 个爬虫测试失败")
    
    print("="*60 + "\n")
    
    return success_count == len(crawlers)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
