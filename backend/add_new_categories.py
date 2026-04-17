"""
添加新的行业类目到数据库
"""
from app import create_app, db
from app.models import Source
from datetime import datetime

app = create_app()

with app.app_context():
    print("开始添加新的行业类目...")
    
    # 定义新的数据源
    new_sources = [
        # 碳交易
        {
            'name': '全国温室气体自愿减排交易系统',
            'url': 'https://www.ccer.com.cn/',
            'type': 'government',
            'priority': 'P0',
            'crawl_interval': 43200,  # 12小时
            'status': 'active'
        },
        # 钢铁行业
        {
            'name': '我的钢铁网',
            'url': 'https://www.mysteel.com/',
            'type': 'industry',
            'priority': 'P0',
            'crawl_interval': 28800,  # 8小时
            'status': 'active'
        },
        # 有色金属
        {
            'name': '中国有色金属报',
            'url': 'https://paper.cnmn.com.cn/',
            'type': 'media',
            'priority': 'P0',
            'crawl_interval': 43200,  # 12小时
            'status': 'active'
        },
        {
            'name': '上海有色金属网',
            'url': 'https://www.metal.com/',
            'type': 'industry',
            'priority': 'P0',
            'crawl_interval': 43200,  # 12小时
            'status': 'active'
        },
    ]
    
    added_count = 0
    for source_data in new_sources:
        # 检查是否已存在
        existing = Source.query.filter_by(name=source_data['name']).first()
        if not existing:
            source = Source(**source_data)
            db.session.add(source)
            added_count += 1
            print(f"✓ 添加数据源: {source_data['name']}")
        else:
            print(f"- 数据源已存在: {source_data['name']}")
    
    if added_count > 0:
        db.session.commit()
        print(f"\n✓ 成功添加 {added_count} 个新数据源")
    else:
        print("\n- 没有新数据源需要添加")
    
    # 显示所有数据源
    print("\n当前所有数据源:")
    all_sources = Source.query.all()
    for i, source in enumerate(all_sources, 1):
        print(f"{i}. {source.name} ({source.type}) - {source.status}")
    
    print(f"\n总计: {len(all_sources)} 个数据源")
    print("\n✓ 类目添加完成！")
