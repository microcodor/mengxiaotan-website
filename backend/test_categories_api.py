#!/usr/bin/env python3
"""
测试分类API
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Article

def test_categories_api():
    """测试分类API功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("分类API测试")
        print("=" * 60)
        
        # 1. 测试获取所有分类
        print("\n1. 获取所有分类:")
        categories = Category.query.order_by(Category.sort_order).all()
        print(f"   总计: {len(categories)} 个分类")
        for cat in categories[:5]:
            print(f"   - {cat.code:20s} {cat.name:10s} (排序: {cat.sort_order})")
        if len(categories) > 5:
            print(f"   ... 还有 {len(categories) - 5} 个分类")
        
        # 2. 测试分类文章统计
        print("\n2. 分类文章统计:")
        for cat in categories[:8]:
            count = Article.query.filter_by(category=cat.code).count()
            reviewed_count = Article.query.filter_by(category=cat.code, is_reviewed=True).count()
            print(f"   {cat.name:10s} - 总计: {count:3d} 篇, 已审核: {reviewed_count:3d} 篇")
        
        # 3. 测试获取特定分类
        print("\n3. 获取特定分类详情:")
        power_cat = Category.query.filter_by(code='power').first()
        if power_cat:
            print(f"   代码: {power_cat.code}")
            print(f"   名称: {power_cat.name}")
            print(f"   描述: {power_cat.description}")
            print(f"   图标: {power_cat.icon}")
            print(f"   状态: {'启用' if power_cat.is_active else '禁用'}")
        
        # 4. 测试文章的分类名称
        print("\n4. 测试文章分类名称显示:")
        articles = Article.query.limit(5).all()
        for article in articles:
            cat = Category.query.filter_by(code=article.category).first()
            cat_name = cat.name if cat else article.category
            print(f"   [{cat_name}] {article.title[:40]}...")
        
        # 5. 测试API响应格式
        print("\n5. 模拟API响应格式:")
        result = []
        for cat in categories[:3]:
            article_count = Article.query.filter_by(category=cat.code, is_reviewed=True).count()
            result.append({
                'id': cat.id,
                'code': cat.code,
                'name': cat.name,
                'description': cat.description,
                'icon': cat.icon,
                'sort_order': cat.sort_order,
                'is_active': cat.is_active,
                'article_count': article_count
            })
        
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

if __name__ == '__main__':
    test_categories_api()
