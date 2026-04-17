"""
测试文章数少于10的平台爬虫
抓取本月所有文章并检查爬虫状态
"""
import asyncio
import sys
from datetime import datetime

# 需要测试的爬虫（文章数 < 10）
CRAWLERS_TO_TEST = [
    {
        'name': '中国能源报',
        'module': 'crawl4ai_cnenergynews',
        'class': 'CnEnergyNewsCrawler',
        'type': 'crawl4ai',
        'current_count': 0
    },
    {
        'name': '国家能源局',
        'module': 'nea',
        'class': None,
        'type': 'scrapy',
        'current_count': 4
    },
    {
        'name': '中国有色金属报',
        'module': 'nonferrous',
        'class': None,
        'type': 'scrapy',
        'current_count': 3
    },
    {
        'name': '北极星电力网',
        'module': 'bjx_power',
        'class': None,
        'type': 'scrapy',
        'current_count': 3
    },
    {
        'name': '中国新能源网',
        'module': 'newenergy',
        'class': None,
        'type': 'scrapy',
        'current_count': 2
    },
    {
        'name': '中国煤炭市场网',
        'module': 'coal',
        'class': None,
        'type': 'scrapy',
        'current_count': 2
    },
    {
        'name': '国家发改委',
        'module': 'ndrc',
        'class': None,
        'type': 'scrapy',
        'current_count': 2
    },
    {
        'name': '中国煤炭工业协会',
        'module': 'coal_association',
        'class': None,
        'type': 'scrapy',
        'current_count': 1
    },
    {
        'name': '中国能源网',
        'module': 'crawl4ai_cnenergy',
        'class': 'CnEnergyCrawler',
        'type': 'crawl4ai',
        'current_count': 1
    }
]

async def test_crawl4ai_crawler(crawler_info):
    """测试Crawl4AI爬虫"""
    print(f"\n{'='*80}")
    print(f"测试爬虫: {crawler_info['name']}")
    print(f"类型: Crawl4AI")
    print(f"当前文章数: {crawler_info['current_count']}")
    print(f"{'='*80}\n")
    
    try:
        # 动态导入模块
        module = __import__(crawler_info['module'])
        crawler_class = getattr(module, crawler_info['class'])
        
        # 创建爬虫实例
        crawler = crawler_class()
        
        # 抓取本月所有文章（不限制数量）
        print(f"开始抓取本月所有文章...")
        await crawler.crawl(max_articles=100, date_filter='this_month')
        
        print(f"\n✅ {crawler_info['name']} 测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ {crawler_info['name']} 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_scrapy_crawler(crawler_info):
    """测试Scrapy爬虫"""
    print(f"\n{'='*80}")
    print(f"测试爬虫: {crawler_info['name']}")
    print(f"类型: Scrapy")
    print(f"当前文章数: {crawler_info['current_count']}")
    print(f"{'='*80}\n")
    
    import subprocess
    
    try:
        # 运行Scrapy爬虫
        print(f"开始抓取本月所有文章...")
        result = subprocess.run(
            ['scrapy', 'crawl', crawler_info['module']],
            cwd='.',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"\n✅ {crawler_info['name']} 测试完成")
            print(f"输出: {result.stdout[-500:]}")  # 显示最后500字符
            return True
        else:
            print(f"\n❌ {crawler_info['name']} 测试失败")
            print(f"错误: {result.stderr[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⚠️ {crawler_info['name']} 超时（5分钟）")
        return False
    except Exception as e:
        print(f"\n❌ {crawler_info['name']} 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print(f"\n{'#'*80}")
    print(f"# 测试文章数少于10的平台爬虫")
    print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# 目标: 抓取本月所有文章")
    print(f"{'#'*80}\n")
    
    results = {
        'success': [],
        'failed': [],
        'total': len(CRAWLERS_TO_TEST)
    }
    
    # 测试所有爬虫
    for crawler_info in CRAWLERS_TO_TEST:
        if crawler_info['type'] == 'crawl4ai':
            success = await test_crawl4ai_crawler(crawler_info)
        else:
            success = test_scrapy_crawler(crawler_info)
        
        if success:
            results['success'].append(crawler_info['name'])
        else:
            results['failed'].append(crawler_info['name'])
    
    # 打印总结
    print(f"\n{'#'*80}")
    print(f"# 测试总结")
    print(f"{'#'*80}\n")
    print(f"总计: {results['total']} 个爬虫")
    print(f"成功: {len(results['success'])} 个")
    print(f"失败: {len(results['failed'])} 个")
    
    if results['success']:
        print(f"\n✅ 成功的爬虫:")
        for name in results['success']:
            print(f"  - {name}")
    
    if results['failed']:
        print(f"\n❌ 失败的爬虫:")
        for name in results['failed']:
            print(f"  - {name}")
    
    # 查询数据库统计
    print(f"\n{'='*80}")
    print(f"查询数据库统计...")
    print(f"{'='*80}\n")
    
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='jinchun123',
            database='energy_station'
        )
        cursor = conn.cursor()
        
        # 查询本月各平台文章数
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM articles 
            WHERE DATE_FORMAT(created_at, '%Y-%m') = '2026-04'
            GROUP BY source 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        print(f"本月各平台文章数:")
        print(f"{'平台':<20} {'文章数':>10}")
        print(f"{'-'*32}")
        for row in results:
            print(f"{row[0]:<20} {row[1]:>10}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库查询失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
