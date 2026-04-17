#!/usr/bin/env python3
"""
批量更新所有爬虫,使用智能内容提取器
"""
import os
import re

# 需要更新的爬虫文件
spider_files = [
    'crawler/energy_crawler/spiders/power_spider.py',
    'crawler/energy_crawler/spiders/ndrc_spider.py',
    'crawler/energy_crawler/spiders/peopledaily_spider.py',
    'crawler/energy_crawler/spiders/coal_spider.py',
    'crawler/energy_crawler/spiders/newenergy_spider.py',
    'crawler/energy_crawler/spiders/cnenergy_spider.py',
    'crawler/energy_crawler/spiders/energy_news_spider.py',
    'crawler/energy_crawler/spiders/ccer_spider.py',
    'crawler/energy_crawler/spiders/mysteel_spider.py',
    'crawler/energy_crawler/spiders/cnmn_paper_spider.py',
    'crawler/energy_crawler/spiders/smm_metal_spider.py',
]

def update_spider_file(filepath):
    """更新单个爬虫文件"""
    if not os.path.exists(filepath):
        print(f"⚠️  文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入了content_extractor
    if 'from energy_crawler.content_extractor import extractor' in content:
        print(f"✅ 已更新: {filepath}")
        return True
    
    # 添加导入语句
    import_pattern = r'(from energy_crawler\.items import ArticleItem)'
    import_replacement = r'\1\nfrom energy_crawler.content_extractor import extractor'
    
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, import_replacement, content)
        print(f"✅ 添加导入: {filepath}")
    else:
        print(f"⚠️  未找到导入位置: {filepath}")
        return False
    
    # 查找parse_article方法
    # 这个比较复杂,需要手动处理每个文件
    # 这里只添加导入,具体的parse_article方法需要手动更新
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📝 已更新导入: {filepath}")
    return True

def main():
    print("开始批量更新爬虫文件...")
    print("="*80)
    
    updated = 0
    failed = 0
    
    for filepath in spider_files:
        try:
            if update_spider_file(filepath):
                updated += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 更新失败: {filepath}")
            print(f"   错误: {str(e)}")
            failed += 1
    
    print("="*80)
    print(f"更新完成: 成功 {updated} 个, 失败 {failed} 个")
    print("\n⚠️  注意: 只添加了导入语句,parse_article方法需要手动更新")
    print("请参考 xinhua_real_spider.py 和 chinapower_spider.py 的实现")

if __name__ == '__main__':
    main()
