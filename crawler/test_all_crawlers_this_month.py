"""
测试所有爬虫 - 抓取本月数据
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

# 导入爬虫
from crawl4ai_peopledaily import PeopleDailyCrawler

async def test_crawl4ai_crawlers():
    """测试Crawl4AI爬虫"""
    print("\n" + "="*60)
    print("测试Crawl4AI爬虫 - 抓取本月数据")
    print("="*60)
    
    results = {}
    
    # 人民网
    print("\n[1/1] 测试人民网...")
    try:
        crawler = PeopleDailyCrawler()
        saved_count = await crawler.crawl(max_articles=20)
        results['人民网'] = {'status': 'success', 'count': saved_count}
        print(f"✅ 人民网完成: {saved_count}篇")
    except Exception as e:
        results['人民网'] = {'status': 'failed', 'error': str(e)}
        print(f"❌ 人民网失败: {str(e)}")
    
    return results

def test_scrapy_crawlers():
    """测试Scrapy爬虫"""
    import subprocess
    
    print("\n" + "="*60)
    print("测试Scrapy爬虫 - 抓取本月数据")
    print("="*60)
    
    results = {}
    
    # 重要的爬虫列表
    scrapy_crawlers = [
        ('国家能源局', 'nea'),
        ('新华网', 'xinhua_energy'),
        ('中国能源网', 'cnenergy'),
        ('国家发改委', 'ndrc'),
        ('有色金属网', 'smm_metal'),
    ]
    
    for i, (name, spider) in enumerate(scrapy_crawlers, 1):
        print(f"\n[{i}/{len(scrapy_crawlers)}] 测试{name}...")
        try:
            # 运行Scrapy爬虫，限制文章数量
            result = subprocess.run(
                ['scrapy', 'crawl', spider, '-s', 'CLOSESPIDER_ITEMCOUNT=20'],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                # 从输出中提取保存的文章数
                output = result.stdout + result.stderr
                # 简单统计（实际应该从日志中解析）
                results[name] = {'status': 'success', 'count': '未知'}
                print(f"✅ {name}完成")
            else:
                results[name] = {'status': 'failed', 'error': 'Scrapy执行失败'}
                print(f"❌ {name}失败")
        except subprocess.TimeoutExpired:
            results[name] = {'status': 'timeout', 'error': '超时'}
            print(f"⏱️  {name}超时")
        except Exception as e:
            results[name] = {'status': 'failed', 'error': str(e)}
            print(f"❌ {name}失败: {str(e)}")
    
    return results

def query_database_stats():
    """查询数据库统计"""
    import pymysql
    
    print("\n" + "="*60)
    print("数据库统计 - 本月数据")
    print("="*60)
    
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'jinchun123',
        'database': 'energy_station',
        'charset': 'utf8mb4'
    }
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 查询本月各来源的文章数量
        print("\n本月各来源文章数量：")
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM articles
            WHERE YEAR(created_at) = YEAR(CURDATE())
            AND MONTH(created_at) = MONTH(CURDATE())
            GROUP BY source
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        total = 0
        for source, count in results:
            print(f"  {source}: {count}篇")
            total += count
        
        print(f"\n总计: {total}篇")
        
        # 查询今天新增的文章数量
        print("\n今天新增文章数量：")
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM articles
            WHERE DATE(created_at) = CURDATE()
            GROUP BY source
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        today_total = 0
        for source, count in results:
            print(f"  {source}: {count}篇")
            today_total += count
        
        print(f"\n今天总计: {today_total}篇")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"\n❌ 数据库查询失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("\n" + "="*60)
    print("爬虫测试 - 抓取本月数据")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 测试Crawl4AI爬虫
    crawl4ai_results = await test_crawl4ai_crawlers()
    
    # 测试Scrapy爬虫
    scrapy_results = test_scrapy_crawlers()
    
    # 查询数据库统计
    query_database_stats()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    print("\nCrawl4AI爬虫:")
    for name, result in crawl4ai_results.items():
        if result['status'] == 'success':
            print(f"  ✅ {name}: {result['count']}篇")
        else:
            print(f"  ❌ {name}: {result.get('error', '失败')}")
    
    print("\nScrapy爬虫:")
    for name, result in scrapy_results.items():
        if result['status'] == 'success':
            print(f"  ✅ {name}: {result['count']}")
        else:
            print(f"  ❌ {name}: {result.get('error', '失败')}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
