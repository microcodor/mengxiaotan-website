#!/usr/bin/env python3
"""
初始化分类数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category
from datetime import datetime

def init_categories():
    """初始化分类数据"""
    app = create_app()
    
    with app.app_context():
        # 创建分类表
        db.create_all()
        
        # 定义分类数据
        categories_data = [
            # 政府机构
            {'code': 'ndrc', 'name': '发改委', 'description': '国家发展和改革委员会政策文件', 'icon': 'government', 'sort_order': 1},
            {'code': 'nea', 'name': '能源局', 'description': '国家能源局政策和工作动态', 'icon': 'government', 'sort_order': 2},
            
            # 能源行业
            {'code': 'energy', 'name': '能源', 'description': '综合能源行业资讯', 'icon': 'energy', 'sort_order': 10},
            {'code': 'power', 'name': '电力', 'description': '电力行业新闻和政策', 'icon': 'power', 'sort_order': 11},
            {'code': 'coal', 'name': '煤炭', 'description': '煤炭行业资讯和价格信息', 'icon': 'coal', 'sort_order': 12},
            {'code': 'new_energy', 'name': '新能源', 'description': '新能源技术和产业动态', 'icon': 'renewable', 'sort_order': 13},
            
            # 碳排放相关行业
            {'code': 'carbon_trading', 'name': '碳交易', 'description': '碳排放权交易和CCER相关资讯', 'icon': 'carbon', 'sort_order': 20},
            {'code': 'steel', 'name': '钢铁', 'description': '钢铁行业资讯和碳排放信息', 'icon': 'steel', 'sort_order': 21},
            {'code': 'nonferrous_metals', 'name': '有色金属', 'description': '有色金属行业动态', 'icon': 'metal', 'sort_order': 22},
            {'code': 'chemical', 'name': '化工', 'description': '化工行业资讯', 'icon': 'chemical', 'sort_order': 23},
            {'code': 'textile', 'name': '纺织', 'description': '纺织行业动态', 'icon': 'textile', 'sort_order': 24},
            {'code': 'paper', 'name': '造纸', 'description': '造纸行业资讯', 'icon': 'paper', 'sort_order': 25},
            {'code': 'pharmaceutical', 'name': '医药', 'description': '医药行业动态', 'icon': 'pharma', 'sort_order': 26},
            {'code': 'cement', 'name': '水泥', 'description': '水泥建材行业资讯', 'icon': 'cement', 'sort_order': 27},
            {'code': 'machinery', 'name': '机械制造', 'description': '机械制造行业动态', 'icon': 'machinery', 'sort_order': 28},
            
            # 媒体
            {'code': 'media', 'name': '媒体资讯', 'description': '主流媒体能源报道', 'icon': 'news', 'sort_order': 90},
            
            # 其他
            {'code': 'test', 'name': '测试', 'description': '测试数据', 'icon': 'test', 'sort_order': 99},
        ]
        
        # 插入分类数据
        added_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            existing = Category.query.filter_by(code=cat_data['code']).first()
            
            if existing:
                # 更新现有分类
                existing.name = cat_data['name']
                existing.description = cat_data['description']
                existing.icon = cat_data['icon']
                existing.sort_order = cat_data['sort_order']
                existing.updated_at = datetime.utcnow()
                updated_count += 1
                print(f"✓ 更新分类: {cat_data['code']} - {cat_data['name']}")
            else:
                # 创建新分类
                category = Category(**cat_data)
                db.session.add(category)
                added_count += 1
                print(f"✓ 添加分类: {cat_data['code']} - {cat_data['name']}")
        
        db.session.commit()
        
        print(f"\n分类初始化完成！")
        print(f"新增: {added_count} 个")
        print(f"更新: {updated_count} 个")
        print(f"总计: {Category.query.count()} 个分类")
        
        # 显示所有分类
        print("\n当前所有分类:")
        categories = Category.query.order_by(Category.sort_order).all()
        for cat in categories:
            print(f"  {cat.code:20s} - {cat.name:10s} (排序: {cat.sort_order})")

if __name__ == '__main__':
    init_categories()
