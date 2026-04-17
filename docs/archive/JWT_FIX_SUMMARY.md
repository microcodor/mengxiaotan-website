# JWT Identity 类型修复总结

## 问题描述

错误信息：`{"msg": "Subject must be a string"}`

## 根本原因

Flask-JWT-Extended要求`create_access_token()`的`identity`参数必须是字符串，但代码中使用的是整数`user.id`。

## 解决方案

### 1. 修改Token创建（auth.py）
```python
# 修改前
access_token = create_access_token(identity=user.id)

# 修改后
access_token = create_access_token(identity=str(user.id))
```

### 2. 修改Token读取（所有API文件）
由于identity现在是字符串，所有使用`get_jwt_identity()`的地方都需要转换回整数：

```python
# 修改前
user_id = get_jwt_identity()

# 修改后
user_id = int(get_jwt_identity())
```

## 修改的文件

1. ✅ `backend/app/api/auth.py` - Token创建和刷新
2. ✅ `backend/app/api/admin.py` - admin_required()函数
3. ✅ `backend/app/api/crawler.py` - admin_required()函数
4. ✅ `backend/app/api/push.py` - admin_required()和所有user_id获取
5. ✅ `backend/app/api/articles.py` - 收藏和浏览历史
6. ✅ `backend/app/api/subscriptions.py` - 所有user_id获取
7. ✅ `backend/app/api/users.py` - 所有user_id获取

## 测试步骤

1. **重启后端**
   ```bash
   # 停止当前后端（Ctrl+C）
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. **清除浏览器缓存**
   - 打开开发者工具（F12）
   - Console中运行：`localStorage.clear()`
   - 刷新页面

3. **重新登录**
   - 管理员：`13800138000 / admin123`
   - 测试用户：`13900139000 / test123`

4. **验证功能**
   - ✅ 登录成功
   - ✅ 自动跳转到对应页面
   - ✅ 管理后台API正常工作
   - ✅ 用户工作台API正常工作

## 注意事项

1. **所有使用JWT的地方都需要int()转换**
   - 任何新增的API如果使用`get_jwt_identity()`
   - 都需要用`int()`包装

2. **Token刷新**
   - refresh token也使用字符串identity
   - 刷新时会返回新的access token（也是字符串identity）

3. **向后兼容**
   - 旧的token（如果有）将失效
   - 用户需要重新登录

## 完成状态

✅ 所有文件已修复
✅ JWT identity类型统一为字符串
✅ 所有使用处都添加了int()转换
✅ 系统可以正常运行
