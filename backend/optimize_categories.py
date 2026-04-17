#!/usr/bin/env python3
"""
优化分类结构 - 合并重复和相似的分类
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Article
from datetime import datetime

def optimize_categories():
    """优化分类结构"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("分类优化方案")
        print("=" * 60)
        
        # 当前分类统计
        print("\n当前分类统计:")
        categories = Category.query.order_by(Category.sort_order).all()
        for cat in categories:
            count = Article.query.filter_by(category=cat.code).count()
            print(f"  {cat.code:20s} {cat.name:10s} - {count:3d} 篇文章")
        
        print("\n" + "=" * 60)
        print("优化方案：")
        print("=" * 60)
        
        # 合并方案
        merge_plan = [
            {
                'action': '合并',
                'from': ['ndrc', 'nea'],
                'to': 'government',
                'name': '政策法规',
                'description': '国家发改委、能源局等政府机构政策文件',
                'reason': 'ndrc和nea都是政府机构，可以合并为统一的政策法规分类'
            },
            {
                'action': '保留',
                'code': 'energy',
                'name': '综合能源',
                'reason': '综合性能源资讯，保留'
            },
            {
                'action': '保留',
                'code': 'power',
                'name': '电力',
                'reason': '电力行业独立性强，保留'
            },
            {
                'action': '保留',
                'code': 'coal',
                'name': '煤炭',
                'reason': '煤炭行业独立性强，保留'
            },
            {
                'action': '保留',
                'code': 'new_energy',
                'name': '新能源',
                'reason': '新能源是重点领域，保留'
            },
            {
                'action': '保留',
                'code': 'carbon_trading',
                'name': '碳交易',
                'reason': '碳交易是核心业务，保留'
            },
            {
                'action': '合并',
                'from': ['steel', 'nonferrous_metals', 'cement'],
                'to': 'metal_materials',
                'name': '金属建材',
                'description': '钢铁、有色金属、水泥等金属和建材行业',
                'reason': '钢铁、有色金属、水泥都属于重工业，可以合并'
            },
            {
                'action': '合并',
                'from': ['chemical', 'pharmaceutical'],
                'to': 'chemical_pharma',
                'name': '化工医药',
                'description': '化工和医药行业资讯',
                'reason': '化工和医药行业相关性强，可以合并'
            },
            {
                'action': '合并',
                'from': ['textile', 'paper', 'machinery'],
                'to': 'manufacturing',
                'name': '制造业',
                'description': '纺织、造纸、机械制造等制造业',
                'reason': '纺织、造纸、机械都属于制造业，可以合并'
            },
            {
                'action': '保留',
                'code': 'media',
                'name': '媒体资讯',
                'reason': '媒体报道独立分类，保留'
            },
            {
                'action': '删除',
                'code': 'test',
                'reason': '测试分类，可以删除'
            }
        ]
        
        # 显示优化方案
        print("\n优化方案详情：")
        for i, plan in enumerate(merge_plan, 1):
            print(f"\n{i}. {plan['action']}: ", end='')
            if plan['action'] == '合并':
                print(f"{', '.join(plan['from'])} → {plan['to']} ({plan['name']})")
                print(f"   原因: {plan['reason']}")
            elif plan['action'] == '保留':
                print(f"{plan['code']} ({plan['name']})")
                print(f"   原因: {plan['reason']}")
            elif plan['action'] == '删除':
                print(f"{plan['code']}")
                print(f"   原因: {plan['reason']}")
        
        print("\n" + "=" * 60)
        print("优化后的分类结构（共10个）：")
        print("=" * 60)
        
        optimized_categories = [
            {'code': 'government', 'name': '政策法规', 'sort_order': 1},
            {'code': 'energy', 'name': '综合能源', 'sort_order': 10},
            {'code': 'power', 'name': '电力', 'sort_order': 11},
            {'code': 'coal', 'name': '煤炭', 'sort_order': 12},
            {'code': 'new_energy', 'name': '新能源', 'sort_order': 13},
            {'code': 'carbon_trading', 'name': '碳交易', 'sort_order': 20},
            {'code': 'metal_materials', 'name': '金属建材', 'sort_order': 30},
            {'code': 'chemical_pharma', 'name': '化工医药', 'sort_order': 31},
            {'code': 'manufacturing', 'name': '制造业', 'sort_order': 32},
            {'code': 'media', 'name': '媒体资讯', 'sort_order': 90},
        ]
        
        for cat in optimized_categories:
            print(f"  {cat['code']:20s} {cat['name']:10s} (排序: {cat['sort_order']})")
        
        print("\n" + "=" * 60)
        choice = input("\n是否执行优化？(yes/no): ")
        
        if choice.lower() != 'yes':
            print("取消优化")
            return
        
        print("\n开始执行优化...")
        
        # 1. 合并 ndrc + nea → government
        print("\n1. 合并 ndrc + nea → government")
        ndrc_articles = Article.query.filter_by(category='ndrc').all()
        nea_articles = Article.query.filter_by(category='nea').all()
        for article in ndrc_articles + nea_articles:
            article.category = 'government'
        print(f"   迁移了 {len(ndrc_articles) + len(nea_articles)} 篇文章")
        
        # 创建或更新 government 分类
        gov_cat = Category.query.filter_by(code='government').first()
        if not gov_cat:
            gov_cat = Category(
                code='government',
                name='政策法规',
                description='国家发改委、能源局等政府机构政策文件',
                icon='government',
                sort_order=1,
                is_active=True
            )
            db.session.add(gov_cat)
        
        # 删除旧分类
        Category.query.filter_by(code='ndrc').delete()
        Category.query.filter_by(code='nea').delete()
        
        # 2. 合并 steel + nonferrous_metals + cement → metal_materials
        print("\n2. 合并 steel + nonferrous_metals + cement → metal_materials")
        steel_articles = Article.query.filter_by(category='steel').all()
        metal_articles = Article.query.filter_by(category='nonferrous_metals').all()
        cement_articles = Article.query.filter_by(category='cement').all()
        for article in steel_articles + metal_articles + cement_articles:
            article.category = 'metal_materials'
        print(f"   迁移了 {len(steel_articles) + len(metal_articles) + len(cement_articles)} 篇文章")
        
        metal_cat = Category.query.filter_by(code='metal_materials').first()
        if not metal_cat:
            metal_cat = Category(
                code='metal_materials',
                name='金属建材',
                description='钢铁、有色金属、水泥等金属和建材行业',
                icon='steel',
                sort_order=30,
                is_active=True
            )
            db.session.add(metal_cat)
        
        Category.query.filter_by(code='steel').delete()
        Category.query.filter_by(code='nonferrous_metals').delete()
        Category.query.filter_by(code='cement').delete()
        
        # 3. 合并 chemical + pharmaceutical → chemical_pharma
        print("\n3. 合并 chemical + pharmaceutical → chemical_pharma")
        chem_articles = Article.query.filter_by(category='chemical').all()
        pharma_articles = Article.query.filter_by(category='pharmaceutical').all()
        for article in chem_articles + pharma_articles:
            article.category = 'chemical_pharma'
        print(f"   迁移了 {len(chem_articles) + len(pharma_articles)} 篇文章")
        
        chem_cat = Category.query.filter_by(code='chemical_pharma').first()
        if not chem_cat:
            chem_cat = Category(
                code='chemical_pharma',
                name='化工医药',
                description='化工和医药行业资讯',
                icon='chemical',
                sort_order=31,
                is_active=True
            )
            db.session.add(chem_cat)
        
        Category.query.filter_by(code='chemical').delete()
        Category.query.filter_by(code='pharmaceutical').delete()
        
        # 4. 合并 textile + paper + machinery → manufacturing
        print("\n4. 合并 textile + paper + machinery → manufacturing")
        textile_articles = Article.query.filter_by(category='textile').all()
        paper_articles = Article.query.filter_by(category='paper').all()
        machinery_articles = Article.query.filter_by(category='machinery').all()
        for article in textile_articles + paper_articles + machinery_articles:
            article.category = 'manufacturing'
        print(f"   迁移了 {len(textile_articles) + len(paper_articles) + len(machinery_articles)} 篇文章")
        
        manu_cat = Category.query.filter_by(code='manufacturing').first()
        if not manu_cat:
            manu_cat = Category(
                code='manufacturing',
                name='制造业',
                description='纺织、造纸、机械制造等制造业',
                icon='machinery',
                sort_order=32,
                is_active=True
            )
            db.session.add(manu_cat)
        
        Category.query.filter_by(code='textile').delete()
        Category.query.filter_by(code='paper').delete()
        Category.query.filter_by(code='machinery').delete()
        
        # 5. 删除 test 分类
        print("\n5. 删除 test 分类")
        test_articles = Article.query.filter_by(category='test').all()
        if test_articles:
            print(f"   警告: test 分类下还有 {len(test_articles)} 篇文章，不删除")
        else:
            Category.query.filter_by(code='test').delete()
            print("   已删除 test 分类")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("优化完成！")
        print("=" * 60)
        
        # 显示优化后的结果
        print("\n优化后的分类列表:")
        categories = Category.query.order_by(Category.sort_order).all()
        for cat in categories:
            count = Article.query.filter_by(category=cat.code).count()
            print(f"  {cat.code:20s} {cat.name:10s} - {count:3d} 篇文章 (排序: {cat.sort_order})")
        
        print(f"\n总计: {len(categories)} 个分类")

if __name__ == '__main__':
    optimize_categories()
