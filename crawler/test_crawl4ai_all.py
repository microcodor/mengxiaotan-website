"""
批量测试所有Crawl4AI爬虫
"""
import asyncio
from datetime import datetime

# 导入所有爬虫
from crawl4ai_ndrc import NdrcCrawler
from crawl4ai_peopledaily import PeopleDailyCrawler
from crawl4ai_cnenergy import CnEnergyCrawler
from crawl4ai_cnenergynews import CnEnergyNewsCrawler
from crawl4ai_smm_metal import SmmMetalCrawler
from crawl4ai_cnmn_paper import CnmnPaperCrawler
from crawl4ai_ccer import CcerCrawler

async def test_all_crawlers():
    """测试所有爬虫"""
    print("\n" + "="*80)
    print("🚀 开始测试所有Crawl4AI爬虫")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # 定义所有爬虫
    crawlers = [
        ("国家发改委", NdrcCrawler()),
        ("人民网", PeopleDailyCrawler()),
        ("中国能源网", CnEnergyCrawler()),
        ("中国能源报", CnEnergyNewsCrawler()),
        ("上海有色金属网", SmmMetalCrawler()),
        ("中国有色金属报", CnmnPaperCrawler()),
        ("CCER碳交易", CcerCrawler()),
    ]
    
    results = []
    
    for name, crawler in crawlers:
        print("\n" + "="*80)
        print(f"📍 测试爬虫: {name}")
        print("="*80 + "\n")
        
        start_time = datetime.now()
        
        try:
            count = await crawler.crawl(max_articles=5)  # 每个爬虫测试5篇
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.append({
                'name': name,
                'status': '✅ 成功' if count > 0 else '⚠️  无数据',
                'count': count,
                'duration': duration
            })
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.append({
                'name': name,
                'status': '❌ 失败',
                'count': 0,
                'duration': duration,
                'error': str(e)
            })
            
            print(f"\n❌ 测试失败: {str(e)}\n")
    
    # 打印总结
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80 + "\n")
    
    print(f"{'爬虫名称':<20} {'状态':<15} {'文章数':<10} {'耗时(秒)':<10}")
    print("-" * 80)
    
    total_count = 0
    success_count = 0
    
    for result in results:
        print(f"{result['name']:<20} {result['status']:<15} {result['count']:<10} {result['duration']:<10.1f}")
        total_count += result['count']
        if result['count'] > 0:
            success_count += 1
    
    print("-" * 80)
    print(f"\n总计:")
    print(f"  测试爬虫数: {len(results)}")
    print(f"  成功爬虫数: {success_count}")
    print(f"  总文章数: {total_count}")
    print(f"  成功率: {success_count/len(results)*100:.1f}%")
    
    print("\n" + "="*80)
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_crawlers())
