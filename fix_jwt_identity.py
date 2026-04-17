#!/usr/bin/env python3
"""
批量修复 get_jwt_identity() 返回值类型问题
将所有需要整数的地方添加 int() 转换
"""

import re
import os

files_to_fix = [
    'backend/app/api/push.py',
    'backend/app/api/subscriptions.py',
    'backend/app/api/users.py',
]

# 需要转换为int的模式
patterns = [
    (r'user_id = get_jwt_identity\(\)', 'user_id = int(get_jwt_identity())'),
    (r'current_user_id = get_jwt_identity\(\)', 'current_user_id = int(get_jwt_identity())'),
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复: {filepath}")
    else:
        print(f"⏭️  无需修改: {filepath}")

print("\n✅ 修复完成！")
