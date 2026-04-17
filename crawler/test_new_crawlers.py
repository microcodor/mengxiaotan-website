"""
批量测试新爬虫
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

async def test_crawler(crawler_class, name):
    """测试单个爬虫"""
    print(f"\n{'='*60}")
    print(f"测试 {name}")
    print(f"{'='*60}")
    
    try:
        crawler = crawler_class()
        # 只抓取3篇文章进行测试
        count = await crawler.crawl(max_articles=3, date_filter='this_month')
        
        if count > 0:
            print(f"✅ {name}: 成功抓取 {count} 篇文章")
            return True, count
        else:
            print(f"⚠️  {name}: 未抓取到文章")
            return False, 0
    except Exception as e:
        print(f"❌ {name}: 测试失败 - {str(e)}")
        return False, 0

async def main():
    """主函数"""
    results = []
    
    # 测试中国电力新闻网
    try:
        from crawl4ai_cpnn import CPNNCrawler
        success, count = await test_crawler(CPNNCrawler, "中国电力新闻网")
        results.append(("中国电力新闻网", success, count))
    except Exception as e:
        print(f"❌ 中国电力新闻网: 导入失败 - {str(e)}")
        results.append(("中国电力新闻网", False, 0))
    
    # 测试能源界
    try:
        from crawl4ai_energyworld import EnergyWorldCrawler
        success, count = await test_crawler(EnergyWorldCrawler, "能源界")
        results.append(("能源界", success, count))
    except Exception as e:
        print(f"❌ 能源界: 导入失败 - {str(e)}")
        results.append(("能源界", False, 0))
    
    # 测试Solarbe光伏网
    try:
        from crawl4ai_solarbe import SolarbeCrawler
        success, count = await test_crawler(SolarbeCrawler, "Solarbe光伏网")
        results.append(("Solarbe光伏网", success, count))
    except Exception as e:
        print(f"❌ Solarbe光伏网: 导入失败 - {str(e)}")
        results.append(("Solarbe光伏网", False, 0))
    
    # 打印总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    success_count = 0
    total_articles = 0
    
    for name, success, count in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name:20s} {status:10s} {count}篇")
        if success:
            success_count += 1
            total_articles += count
    
    print(f"{'='*60}")
    print(f"成功: {success_count}/{len(results)} 个爬虫")
    print(f"总文章数: {total_articles} 篇")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
