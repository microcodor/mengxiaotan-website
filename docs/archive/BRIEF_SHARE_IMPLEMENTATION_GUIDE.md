# 蒙小碳早报分享功能 - 快速实施指南

## 实施步骤

### 步骤1：数据库迁移（5分钟）

```bash
# 连接到MySQL数据库
mysql -u root -p mengxiaotan

# 执行迁移脚本
source backend/migrations/add_brief_share_fields.sql

# 或者直接执行SQL
mysql -u root -p mengxiaotan < backend/migrations/add_brief_share_fields.sql
```

**验证**：
```sql
-- 检查字段是否添加成功
DESC daily_briefs;

-- 应该看到以下新字段：
-- share_token VARCHAR(32)
-- standard_content JSON
-- premium_content JSON
-- view_count INT
-- share_count INT
```

### 步骤2：注册API路由（2分钟）

编辑 `backend/app/api/__init__.py`，添加简报API：

```python
from flask import Blueprint
from flask_smorest import Api

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
push_bp = Blueprint('push', __name__, url_prefix='/api')

# 导入路由
from app.api import articles, auth, subscription, push, brief  # 添加 brief

def init_api(app):
    """初始化API"""
    api = Api(app)
    api.register_blueprint(api_bp)
    api.register_blueprint(admin_bp)
    api.register_blueprint(push_bp)
```

### 步骤3：添加前端路由（2分钟）

编辑 `frontend/src/App.tsx` 或路由配置文件：

```typescript
import BriefDetail from '@/pages/BriefDetail'

// 在路由配置中添加
<Route path="/briefs/:shareToken" element={<BriefDetail />} />
```

### 步骤4：重启服务（1分钟）

```bash
# 重启后端
cd backend
python run_backend.py

# 重启前端（如果需要）
cd frontend
npm run dev
```

### 步骤5：测试功能（5分钟）

#### 5.1 生成测试简报

```bash
# 方法1：通过API生成
curl -X POST http://localhost:5001/api/admin/daily-brief \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"

# 方法2：通过定时任务（等待晚上8点自动执行）
# 或手动触发定时任务
```

#### 5.2 获取简报列表

```bash
curl http://localhost:5001/api/briefs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应**：
```json
{
  "items": [
    {
      "id": 1,
      "brief_date": "2026-04-17",
      "share_url": "http://localhost:5173/briefs/abc123def456?v=standard",
      "view_count": 0,
      "share_count": 0
    }
  ],
  "total": 1,
  "user_version": "standard"
}
```

#### 5.3 访问分享链接

在浏览器中打开：
```
http://localhost:5173/briefs/abc123def456?v=standard
```

应该看到简报详情页面。

#### 5.4 测试分享功能

1. 在简报详情页点击"分享"按钮
2. 链接应该被复制到剪贴板
3. 刷新页面，分享次数应该增加

## 常见问题排查

### 问题1：数据库迁移失败

**错误**：`ERROR 1060: Duplicate column name 'share_token'`

**解决**：字段已存在，跳过此步骤或删除字段后重新添加
```sql
ALTER TABLE daily_briefs DROP COLUMN share_token;
-- 然后重新执行迁移脚本
```

### 问题2：简报没有share_token

**原因**：旧数据没有token

**解决**：
```sql
UPDATE daily_briefs 
SET share_token = MD5(CONCAT(brief_date, UUID()))
WHERE share_token IS NULL OR share_token = '';
```

### 问题3：访问简报返回404

**检查清单**：
- [ ] API路由是否正确注册
- [ ] share_token是否存在于数据库
- [ ] 前端路由是否配置
- [ ] 后端服务是否重启

**调试**：
```bash
# 检查数据库中的token
mysql -u root -p mengxiaotan -e "SELECT id, brief_date, share_token FROM daily_briefs;"

# 测试API
curl http://localhost:5001/api/briefs/YOUR_SHARE_TOKEN
```

### 问题4：高级版用户看不到决策建议

**检查清单**：
- [ ] 用户订阅状态是否为active
- [ ] 订阅套餐名称是否包含"高级"或"premium"
- [ ] JWT token是否有效
- [ ] premium_content字段是否有数据

**调试**：
```sql
-- 检查用户订阅
SELECT u.id, u.phone, s.status, sp.name 
FROM users u
JOIN subscriptions s ON u.id = s.user_id
JOIN subscription_plans sp ON s.plan_id = sp.id
WHERE u.id = YOUR_USER_ID;
```

### 问题5：前端页面样式异常

**检查清单**：
- [ ] Tailwind CSS是否正确配置
- [ ] 图标库是否安装（lucide-react）
- [ ] 玻璃态样式类是否定义

**解决**：
```bash
# 安装依赖
cd frontend
npm install lucide-react

# 重新构建
npm run dev
```

## 功能验证清单

### 基础功能
- [ ] 简报生成时自动创建share_token
- [ ] 简报生成时创建standard_content和premium_content
- [ ] 可以通过share_token访问简报
- [ ] 浏览次数正确统计
- [ ] 分享次数正确统计

### 版本控制
- [ ] 未登录用户只能看标准版
- [ ] 标准版用户只能看标准版
- [ ] 高级版用户可以看高级版（含决策建议）
- [ ] URL参数v=premium对非高级版用户无效

### 推送功能
- [ ] 推送消息包含查看链接
- [ ] 标准版用户收到标准版链接
- [ ] 高级版用户收到高级版链接
- [ ] 链接可以正常访问

### 界面功能
- [ ] 简报详情页正常显示
- [ ] 分享按钮可以复制链接
- [ ] 分类文章正确展示
- [ ] 响应式布局正常

## 性能优化建议

### 1. 添加缓存（可选）

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@api_bp.route('/briefs/<string:share_token>')
@cache.cached(timeout=300)  # 缓存5分钟
def get_brief(share_token):
    # ...
```

### 2. 数据库索引优化

```sql
-- 已创建的索引
CREATE INDEX idx_daily_briefs_share_token ON daily_briefs(share_token);
CREATE INDEX idx_daily_briefs_brief_date ON daily_briefs(brief_date);

-- 可选：复合索引
CREATE INDEX idx_daily_briefs_date_token ON daily_briefs(brief_date, share_token);
```

### 3. CDN加速（生产环境）

- 将静态资源（图片、CSS、JS）部署到CDN
- 使用CDN加速简报页面访问

## 监控建议

### 1. 访问日志

```python
@api_bp.route('/briefs/<string:share_token>')
def get_brief(share_token):
    logger.info(f"Brief accessed: {share_token}, IP: {request.remote_addr}")
    # ...
```

### 2. 统计分析

```sql
-- 最受欢迎的简报
SELECT brief_date, view_count, share_count
FROM daily_briefs
ORDER BY view_count DESC
LIMIT 10;

-- 分享率分析
SELECT 
    brief_date,
    view_count,
    share_count,
    ROUND(share_count * 100.0 / NULLIF(view_count, 0), 2) as share_rate
FROM daily_briefs
WHERE view_count > 0
ORDER BY brief_date DESC;
```

### 3. 错误监控

使用Sentry或类似工具监控错误：
```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)
```

## 上线检查清单

### 部署前
- [ ] 数据库迁移已执行
- [ ] 所有测试通过
- [ ] 代码已提交到版本控制
- [ ] 配置文件已更新（生产环境URL）
- [ ] 依赖包已安装

### 部署后
- [ ] 服务正常启动
- [ ] API接口可访问
- [ ] 前端页面正常显示
- [ ] 推送功能正常
- [ ] 监控系统正常

### 回滚计划
如果出现问题，可以快速回滚：
```sql
-- 回滚数据库（如果需要）
ALTER TABLE daily_briefs DROP COLUMN share_token;
ALTER TABLE daily_briefs DROP COLUMN standard_content;
ALTER TABLE daily_briefs DROP COLUMN premium_content;
ALTER TABLE daily_briefs DROP COLUMN view_count;
ALTER TABLE daily_briefs DROP COLUMN share_count;
```

## 总结

按照以上步骤，你应该能在15分钟内完成蒙小碳早报分享功能的部署。

**关键点**：
1. 数据库迁移是第一步
2. 确保API路由正确注册
3. 测试各个版本的访问权限
4. 验证推送消息中的链接

如有问题，请参考 `DAILY_BRIEF_SHARE_FEATURE.md` 获取详细文档。
