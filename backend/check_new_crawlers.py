"""
检查新增爬虫的数据
"""
from app import create_app, db
from app.models import Article, Source
from sqlalchemy import func
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 60)
    print("新增爬虫数据统计")
    print("=" * 60)
    print()
    
    # 新增的数据源
    new_sources = [
        '全国温室气体自愿减排交易系统',
        '我的钢铁网',
        '中国有色金属报',
        '上海有色金属网'
    ]
    
    # 新增的类目
    new_categories = ['carbon_trading', 'steel', 'nonferrous_metals']
    
    print("1. 新增数据源状态")
    print("-" * 60)
    for source_name in new_sources:
        source = Source.query.filter_by(name=source_name).first()
        if source:
            print(f"✓ {source.name}")
            print(f"  状态: {source.status}")
            print(f"  类型: {source.type}")
            print(f"  最后抓取: {source.last_crawl_at or '未运行'}")
        else:
            print(f"✗ {source_name} - 未找到")
        print()
    
    print("\n2. 新增类目文章统计")
    print("-" * 60)
    for category in new_categories:
        count = Article.query.filter_by(category=category).count()
        print(f"{category}: {count}篇")
        
        if count > 0:
            # 显示最新的3篇
            articles = Article.query.filter_by(category=category)\
                .order_by(Article.created_at.desc()).limit(3).all()
            for article in articles:
                print(f"  - {article.title[:50]}... ({article.source})")
    
    print("\n3. 今日新增文章")
    print("-" * 60)
    today = datetime.utcnow().date()
    today_articles = Article.query.filter(
        func.date(Article.created_at) == today
    ).all()
    
    print(f"今日共新增: {len(today_articles)}篇")
    
    # 按来源统计
    source_stats = {}
    for article in today_articles:
        source_stats[article.source] = source_stats.get(article.source, 0) + 1
    
    print("\n按来源统计:")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}篇")
    
    print("\n4. 总体统计")
    print("-" * 60)
    total = Article.query.count()
    print(f"数据库总文章数: {total}篇")
    
    # 按类目统计
    category_stats = db.session.query(
        Article.category,
        func.count(Article.id).label('count')
    ).group_by(Article.category).all()
    
    print("\n按类目统计:")
    for category, count in category_stats:
        print(f"  {category or '未分类'}: {count}篇")
    
    print("\n" + "=" * 60)
    print("统计完成！")
    print("=" * 60)
