#!/usr/bin/env python3
"""
修复articles表的content字段长度
"""
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3307,
    user='root',
    password='password',
    database='energy_station',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("正在修改content字段类型...")

try:
    # 将content字段改为LONGTEXT类型（最大4GB）
    cursor.execute("""
        ALTER TABLE articles 
        MODIFY COLUMN content LONGTEXT
    """)
    
    conn.commit()
    print("✅ content字段已修改为LONGTEXT类型")
    
    # 检查修改结果
    cursor.execute("SHOW COLUMNS FROM articles LIKE 'content'")
    result = cursor.fetchone()
    print(f"当前content字段类型: {result[1]}")
    
except Exception as e:
    print(f"❌ 修改失败: {str(e)}")
    conn.rollback()

cursor.close()
conn.close()
