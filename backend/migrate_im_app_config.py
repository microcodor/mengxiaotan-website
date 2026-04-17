#!/usr/bin/env python3
"""
执行数据库迁移: 添加im_app_config字段
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从DATABASE_URL解析数据库连接信息
database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:jinchun123@localhost:3306/energy_station')

# 解析URL
# mysql+pymysql://root:jinchun123@localhost:3306/energy_station
parts = database_url.replace('mysql+pymysql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')

username = user_pass[0]
password = user_pass[1]
host_port = host_db[0].split(':')
host = host_port[0]
port = int(host_port[1]) if len(host_port) > 1 else 3306
database = host_db[1]

print(f"连接数据库: {host}:{port}/{database}")

try:
    # 连接数据库
    connection = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # 检查字段是否已存在
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'im_app_config'
    """, (database,))
    
    exists = cursor.fetchone()[0]
    
    if exists:
        print("✓ im_app_config字段已存在,跳过迁移")
    else:
        print("添加im_app_config字段...")
        
        # 添加字段
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN im_app_config JSON 
            COMMENT 'IM应用配置(企业微信、钉钉、飞书)'
        """)
        
        connection.commit()
        print("✓ im_app_config字段添加成功")
    
    cursor.close()
    connection.close()
    
    print("\n数据库迁移完成!")
    
except Exception as e:
    print(f"✗ 数据库迁移失败: {e}")
    exit(1)
