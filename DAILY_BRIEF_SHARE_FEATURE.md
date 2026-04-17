# 蒙小碳早报分享功能实现文档

## 功能概述

为蒙小碳早报添加唯一链接分享功能，支持两个版本（标准版和高级版），用户可以通过链接随时查看历史简报。

## 核心特性

### 1. 唯一分享链接
- 每份简报生成唯一的 `share_token`（32位MD5哈希）
- 链接格式：`https://domain.com/briefs/{share_token}?v={version}`
- 支持公开访问，无需登录

### 2. 两个版本支持
- **标准版**：包含文章摘要和AI概览
- **高级版**：额外包含AI决策建议

### 3. 数据统计
- 浏览次数统计
- 分享次数统计

## 数据库设计

### DailyBrief 模型新增字段

```python
class DailyBrief(db.Model):
    # 原有字段
    id = db.Column(db.Integer, primary_key=True)
    brief_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    content = db.Column(db.JSON)  # 原始完整内容
    ai_suggestion = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 新增字段
    share_token = db.Column(db.String(32), unique=True, nullable=False, index=True)
    standard_content = db.Column(db.JSON)  # 标准版内容
    premium_content = db.Column(db.JSON)   # 高级版内容
    view_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
```

### 数据库迁移

```sql
-- 添加新字段
ALTER TABLE daily_briefs ADD COLUMN share_token VARCHAR(32) UNIQUE;
ALTER TABLE daily_briefs ADD COLUMN standard_content JSON;
ALTER TABLE daily_briefs ADD COLUMN premium_content JSON;
ALTER TABLE daily_briefs ADD COLUMN view_count INT DEFAULT 0;
ALTER TABLE daily_briefs ADD COLUMN share_count INT DEFAULT 0;

-- 创建索引
CREATE INDEX idx_daily_briefs_share_token ON daily_briefs(share_token);

-- 为已存在的简报生成token
UPDATE daily_briefs 
SET share_token = MD5(CONCAT(brief_date, UUID()))
WHERE share_token IS NULL;

-- 复制内容到版本字段
UPDATE daily_briefs 
SET standard_content = content,
    premium_content = content
WHERE standard_content IS NULL;
```

## API接口

### 1. 获取简报列表
```http
GET /api/briefs
Authorization: Bearer <token>
```

**响应**：
```json
{
  "items": [
    {
      "id": 1,
      "brief_date": "2026-04-17",
      "content": {...},
      "ai_suggestion": "...",  // 仅高级版
      "generated_at": "2026-04-17T09:00:00",
      "share_url": "http://localhost:5173/briefs/abc123?v=standard",
      "view_count": 150,
      "share_count": 25
    }
  ],
  "total": 30,
  "user_version": "standard"
}
```

### 2. 通过Token获取简报（公开访问）
```http
GET /api/briefs/{share_token}?v=standard
```

**参数**：
- `share_token`: 简报的唯一标识
- `v`: 版本（standard/premium），可选

**响应**：
```json
{
  "id": 1,
  "brief_date": "2026-04-17",
  "content": {
    "ai_summary": "今日能源行业...",
    "content": {
      "ndrc": [...],
      "coal": [...],
      "power": [...],
      "new_energy": [...]
    },
    "generated_at": "2026-04-17T09:00:00",
    "article_count": 30
  },
  "ai_suggestion": "...",  // 仅高级版
  "share_url": "http://localhost:5173/briefs/abc123?v=standard",
  "view_count": 150,
  "share_count": 25
}
```

### 3. 记录分享
```http
POST /api/briefs/{share_token}/share
```

**响应**：
```json
{
  "message": "分享成功",
  "share_count": 26
}
```

### 4. 获取今日简报
```http
GET /api/briefs/today
Authorization: Bearer <token>
```

### 5. 根据日期获取简报
```http
GET /api/briefs/date/2026-04-17
Authorization: Bearer <token>
```

## 前端实现

### 简报详情页面
- 路径：`/briefs/:shareToken`
- 组件：`frontend/src/pages/BriefDetail.tsx`

### 功能特性
1. **响应式设计**：适配移动端和桌面端
2. **版本识别**：根据URL参数和用户权限显示对应版本
3. **分享功能**：一键复制链接到剪贴板
4. **统计记录**：自动记录浏览和分享次数
5. **分类展示**：按行业分类展示文章
6. **美观界面**：使用渐变色和玻璃态效果

### 界面结构
```
┌─────────────────────────────────────────┐
│ 头部（渐变背景）                          │
│ - 标题：蒙小碳·每日简报                   │
│ - 版本标识：标准版/高级版                 │
│ - 日期、浏览数、分享数                    │
│ - 分享按钮                               │
└─────────────────────────────────────────┘
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📊 今日概览                          │ │
│ │ AI生成的行业摘要...                  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 💡 决策建议（仅高级版）               │ │
│ │ AI生成的决策建议...                  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📋 发改委动态 (5篇)                  │ │
│ │ - 文章1                              │ │
│ │ - 文章2                              │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ ⚫ 煤炭行业 (8篇)                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ ⚡ 电力行业 (10篇)                    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🌱 新能源 (7篇)                      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 页脚信息                                 │
└─────────────────────────────────────────┘
```

## 生成流程

### 1. 简报生成时
```python
# 在 AIBriefGenerator.generate_daily_brief() 中
daily_brief = DailyBrief(
    brief_date=target_date,
    content=brief_content,  # 原始完整内容
    ai_suggestion=ai_suggestion,
    generated_at=datetime.utcnow()
)

# 生成唯一token
daily_brief.share_token = daily_brief.generate_share_token()

# 生成标准版内容（不含决策建议）
daily_brief.standard_content = brief_content.copy()

# 生成高级版内容（含决策建议）
premium_content = brief_content.copy()
premium_content['ai_suggestion'] = ai_suggestion
daily_brief.premium_content = premium_content

db.session.add(daily_brief)
db.session.commit()
```

### 2. 推送消息时
```python
# 标准版用户
standard_url = brief.get_share_url('standard')
message = f"[点击查看完整简报]({standard_url})"

# 高级版用户
premium_url = brief.get_share_url('premium')
message = f"[点击查看完整简报]({premium_url})"
```

## 使用场景

### 场景1：用户查看历史简报
1. 用户登录系统
2. 访问 `/briefs` 查看简报列表
3. 点击某个简报，跳转到详情页
4. 根据用户订阅等级显示对应版本

### 场景2：分享简报给他人
1. 用户打开简报详情页
2. 点击"分享"按钮
3. 链接复制到剪贴板
4. 发送给其他人
5. 接收者无需登录即可查看

### 场景3：推送消息中的链接
1. 系统生成每日简报
2. 推送给订阅用户
3. 消息中包含查看链接
4. 用户点击链接查看完整内容

## 权限控制

### 版本访问规则
1. **公开访问**：任何人都可以通过链接访问简报
2. **版本限制**：
   - 标准版链接：所有人都可以查看标准版内容
   - 高级版链接：需要验证用户订阅等级
   - 未登录用户：只能查看标准版内容
   - 标准版用户：只能查看标准版内容
   - 高级版用户：可以查看高级版内容（含决策建议）

### JWT验证（可选）
```python
try:
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()
    
    if user_id:
        # 验证用户订阅等级
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if subscription and subscription.plan.name == '高级版':
            include_suggestion = True
except:
    # JWT验证失败，按公开访问处理
    pass
```

## 统计功能

### 浏览统计
- 每次访问简报详情页，`view_count` 自动 +1
- 用于分析简报受欢迎程度

### 分享统计
- 用户点击分享按钮，`share_count` 自动 +1
- 用于分析简报传播效果

### 数据分析
可以基于这些统计数据进行：
- 热门简报排行
- 用户活跃度分析
- 内容质量评估
- 推送效果评估

## 配置说明

### 环境变量
```bash
# 前端基础URL（用于生成分享链接）
VITE_APP_BASE_URL=http://localhost:5173

# 后端API URL
VITE_API_BASE_URL=http://localhost:5001
```

### 路由配置
```typescript
// frontend/src/App.tsx
import BriefDetail from '@/pages/BriefDetail'

<Route path="/briefs/:shareToken" element={<BriefDetail />} />
```

## 测试建议

### 功能测试
1. **生成简报**
   - [ ] 验证生成时创建唯一token
   - [ ] 验证标准版和高级版内容正确分离
   - [ ] 验证统计字段初始化为0

2. **访问简报**
   - [ ] 未登录用户访问标准版链接
   - [ ] 未登录用户访问高级版链接（应降级为标准版）
   - [ ] 标准版用户访问高级版链接（应降级为标准版）
   - [ ] 高级版用户访问高级版链接（应显示完整内容）

3. **分享功能**
   - [ ] 点击分享按钮复制链接
   - [ ] 分享次数正确增加
   - [ ] 链接可以正常访问

4. **统计功能**
   - [ ] 浏览次数正确增加
   - [ ] 分享次数正确增加

### 性能测试
- [ ] 大量并发访问时的响应时间
- [ ] 数据库查询性能
- [ ] 缓存策略（可选）

### 安全测试
- [ ] Token唯一性验证
- [ ] SQL注入防护
- [ ] XSS攻击防护

## 后续优化建议

### 短期（1-2周）
1. ✅ 实现基础分享功能（已完成）
2. ⏳ 添加二维码分享
3. ⏳ 添加社交媒体分享按钮

### 中期（1个月）
1. ⏳ 简报列表页面优化
2. ⏳ 添加简报搜索功能
3. ⏳ 添加简报收藏功能
4. ⏳ 简报评论功能

### 长期（3个月）
1. ⏳ 简报订阅推送优化
2. ⏳ 个性化简报推荐
3. ⏳ 简报数据分析看板
4. ⏳ 简报导出功能（PDF/Word）

## 文件清单

### 后端文件
- `backend/app/models.py` - 数据模型（已修改）
- `backend/app/services/ai_brief_generator.py` - 简报生成服务（已修改）
- `backend/app/api/brief.py` - 简报API接口（新增）
- `backend/migrations/add_brief_share_fields.sql` - 数据库迁移脚本（新增）

### 前端文件
- `frontend/src/pages/BriefDetail.tsx` - 简报详情页面（新增）

### 文档文件
- `DAILY_BRIEF_SHARE_FEATURE.md` - 功能实现文档（本文档）

## 总结

本次实现为蒙小碳早报添加了完整的分享功能，包括：
1. ✅ 唯一分享链接生成
2. ✅ 两个版本内容支持
3. ✅ 公开访问能力
4. ✅ 浏览和分享统计
5. ✅ 美观的详情页面
6. ✅ 完整的API接口

用户现在可以：
- 通过链接随时查看历史简报
- 分享简报给其他人
- 根据订阅等级查看对应版本
- 在推送消息中直接点击链接查看

这大大提升了简报的传播性和用户体验！
