# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import User, SubscriptionPlan, Article, Source, Category
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    print("✓ 数据库表创建成功")
    
    # 创建分类
    if Category.query.count() == 0:
        categories = [
            Category(
                code='power',
                name='电力',
                icon='power',
                sort_order=1,
                is_active=True
            ),
            Category(
                code='energy',
                name='能源',
                icon='energy',
                sort_order=2,
                is_active=True
            ),
            Category(
                code='coal',
                name='煤炭',
                icon='coal',
                sort_order=3,
                is_active=True
            ),
            Category(
                code='steel',
                name='钢铁',
                icon='steel',
                sort_order=4,
                is_active=True
            ),
            Category(
                code='new_energy',
                name='新能源',
                icon='renewable',
                sort_order=5,
                is_active=True
            ),
            Category(
                code='ndrc',
                name='政策',
                icon='government',
                sort_order=6,
                is_active=True
            ),
        ]
        db.session.add_all(categories)
        db.session.commit()
        print("✓ 分类创建成功")
    
    # 创建管理员用户
    admin = User.query.filter_by(phone='13800138000').first()
    if not admin:
        admin = User(
            phone='13800138000',
            nickname='管理员',
            role='admin',
            status='active'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✓ 管理员账号创建成功 (13800138000 / admin123)")
    
    # 创建测试用户
    test_user = User.query.filter_by(phone='13900139000').first()
    if not test_user:
        test_user = User(
            phone='13900139000',
            nickname='测试用户',
            role='user',
            status='active'
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        print("✓ 测试用户创建成功 (13900139000 / test123)")
    
    # 创建订阅套餐
    if SubscriptionPlan.query.count() == 0:
        plans = [
            SubscriptionPlan(
                name='免费订阅',
                price=0,
                duration_days=7,  # 限时7天试用
                features={
                    '政策速览': '发改委最新通知、能源行业解读、双碳政策动向',
                    '市场行情': '煤炭价格指数、油气期货走势、新能源装机数据',
                    '热点聚焦': 'AI算力需求下的能源转型、储能技术突破、国际能源博弈',
                    '蒙小碳简评': '3分钟提炼核心，关键数据标注，快速抓住重点',
                    '推送时间': '每日9:00',
                    '推送渠道': '企业微信/微信',
                    '试用期限': '7天免费体验'
                },
                sort_order=1,
                is_active=True
            ),
            SubscriptionPlan(
                name='基础版',
                price=39,
                duration_days=30,  # 按月订阅
                features={
                    '免费版全部功能': '包含所有免费订阅内容',
                    '企业画像构建': '基于官网、财报、招投标信息，自动生成企业核心竞争力分析',
                    '风险与机会识别': '环保处罚、产能过剩风险预警；政策适配性机会分析',
                    '战略级内参': '定制报告2份/月（技术路线优化、区域市场布局建议）',
                    '动态监测': '实时推送企业相关政策、价格波动预警',
                    '数字分身沙盘': '模拟政策、价格波动对企业利润的影响，生成可视化报告',
                    '订阅优惠': '按年订阅赠1个月（468元/年，相当于36元/月）',
                    '推送渠道': '企业微信/微信'
                },
                sort_order=2,
                is_active=True
            ),
        ]
        db.session.add_all(plans)
        print("✓ 订阅套餐创建成功")
    
    # 创建抓取源
    if Source.query.count() == 0:
        sources = [
            Source(
                name='国家发改委',
                url='https://www.ndrc.gov.cn',
                type='government',
                priority='P0',
                crawl_interval=43200,
                status='active'
            ),
            Source(
                name='国家能源局',
                url='https://www.nea.gov.cn',
                type='government',
                priority='P0',
                crawl_interval=43200,
                status='active'
            ),
            Source(
                name='中国煤炭工业协会',
                url='http://www.coalchina.org.cn',
                type='industry',
                priority='P0',
                crawl_interval=86400,
                status='active'
            ),
            Source(
                name='北极星电力网',
                url='https://news.bjx.com.cn',
                type='media',
                priority='P0',
                crawl_interval=86400,
                status='active'
            ),
        ]
        db.session.add_all(sources)
        print("✓ 抓取源配置成功")
    
    # 创建示例文章
    if Article.query.count() == 0:
        categories = ['ndrc', 'coal', 'power', 'new_energy']
        sources_list = ['国家发改委', '国家能源局', '中国煤炭工业协会', '北极星电力网']
        
        sample_articles = [
            {
                'title': '国家发改委发布2026年能源工作指导意见',
                'summary': '为深入贯彻党的二十大精神，推动能源高质量发展，国家发改委发布2026年能源工作指导意见，明确了全年能源工作的主要目标和重点任务。',
                'category': 'ndrc',
                'source': '国家发改委'
            },
            {
                'title': '全国煤炭产量稳步增长 保供能力持续增强',
                'summary': '2026年一季度，全国煤炭产量达到11.2亿吨，同比增长3.5%。煤炭供应保障能力持续增强，为经济社会发展提供了坚实的能源支撑。',
                'category': 'coal',
                'source': '中国煤炭工业协会'
            },
            {
                'title': '电力市场化改革深入推进 交易规模创新高',
                'summary': '2026年3月，全国电力市场交易电量达到4500亿千瓦时，同比增长15%。电力市场化改革持续深化，市场配置资源的决定性作用进一步发挥。',
                'category': 'power',
                'source': '北极星电力网'
            },
            {
                'title': '新能源装机规模突破15亿千瓦 占比超过50%',
                'summary': '截至2026年3月底，全国新能源装机规模达到15.2亿千瓦，占总装机容量的52%。其中，风电装机4.8亿千瓦，光伏装机10.4亿千瓦。',
                'category': 'new_energy',
                'source': '国家能源局'
            },
            {
                'title': '碳达峰碳中和行动方案发布 明确时间表路线图',
                'summary': '国家发改委、能源局联合发布碳达峰碳中和行动方案，明确了2030年前碳达峰、2060年前碳中和的时间表和路线图。',
                'category': 'ndrc',
                'source': '国家发改委'
            },
        ]
        
        articles = []
        for i, data in enumerate(sample_articles):
            article = Article(
                title=data['title'],
                summary=data['summary'],
                content=data['summary'] + '\n\n' + '这是文章的详细内容。' * 20,
                source=data['source'],
                source_url=f'https://example.com/article/{i+1}',
                category=data['category'],
                tags=['政策', '能源', '发展'],
                view_count=random.randint(100, 1000),
                like_count=random.randint(10, 100),
                is_reviewed=True,
                is_top=(i < 2),
                is_carousel=(i < 3),
                published_at=datetime.now() - timedelta(days=i),
                created_at=datetime.now() - timedelta(days=i)
            )
            articles.append(article)
        
        db.session.add_all(articles)
        print(f"✓ 创建了 {len(articles)} 篇示例文章")
    
    db.session.commit()
    print("\n✓ 数据库初始化完成！")
    print("\n登录信息：")
    print("管理员: 13800138000 / admin123")
    print("测试用户: 13900139000 / test123")
