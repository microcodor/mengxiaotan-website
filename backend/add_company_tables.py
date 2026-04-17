#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加企业信息相关表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Company, CompanyBusiness, User

def add_company_tables():
    """添加企业信息相关表"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("添加企业信息相关表")
        print("=" * 60)
        
        # 创建表
        print("\n创建数据表...")
        db.create_all()
        print("✓ 数据表创建成功")
        
        # 检查表是否存在
        print("\n检查表结构:")
        
        # 检查 companies 表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'companies' in inspector.get_table_names():
            print("✓ companies 表已创建")
            columns = [col['name'] for col in inspector.get_columns('companies')]
            print(f"  字段数: {len(columns)}")
            print(f"  主要字段: {', '.join(columns[:10])}")
        
        if 'company_businesses' in inspector.get_table_names():
            print("✓ company_businesses 表已创建")
            columns = [col['name'] for col in inspector.get_columns('company_businesses')]
            print(f"  字段数: {len(columns)}")
        
        # 检查 users 表是否有新字段
        if 'users' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'position' in columns:
                print("✓ users.position 字段已添加")
            else:
                print("⚠ users.position 字段未添加，需要手动添加")
            
            if 'company_id' in columns:
                print("✓ users.company_id 字段已添加")
            else:
                print("⚠ users.company_id 字段未添加，需要手动添加")
        
        print("\n" + "=" * 60)
        print("表结构添加完成！")
        print("=" * 60)
        
        # 显示统计信息
        print("\n当前数据统计:")
        print(f"  企业数量: {Company.query.count()}")
        print(f"  业务数量: {CompanyBusiness.query.count()}")
        print(f"  用户数量: {User.query.count()}")

if __name__ == '__main__':
    add_company_tables()
