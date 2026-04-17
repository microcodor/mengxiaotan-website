# 蒙小碳推送机制说明

**文档版本**: 1.0  
**更新时间**: 2026-04-16

---

## 📊 推送系统架构

### 系统组成

```
┌─────────────────────────────────────────────────────────────┐
│                      定时任务调度器                           │
│                   (APScheduler)                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 每日9:00     │  │ 每日8:00     │  │ 凌晨1:00     │     │
│  │ 生成AI简报   │  │ 试用期提醒   │  │ 处理过期订阅 │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI简报生成器                              │
│              (AIBriefGenerator)                              │
│                                                              │
│  1. 查询昨日文章数据                                         │
│  2. 调用MiniMax AI生成简报                                   │
│  3. 保存到数据库                                             │
│  4. 调用推送服务                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  多渠道推送器                                │
│              (MultiChannelPusher)                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 企业微信推送 │  │ 邮件推送     │  │ 短信推送     │     │
│  │ (待实现)     │  │ (已实现)     │  │ (已实现)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        用户                                  │
│                                                              │
│  免费订阅：企业微信                                          │
│  基础版：企业微信 + 邮件                                     │
│  高级版：企业微信 + 邮件 + 短信                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🕐 推送时间表

### 定时任务

| 时间 | 任务 | 说明 |
|------|------|------|
| **每日 01:00** | 处理过期订阅 | 将已过期的试用订阅标记为过期状态 |
| **每日 08:00** | 爬虫采集 + 试用期提醒 | 采集最新资讯，检查即将到期的试用订阅 |
| **每日 09:00** | **生成并推送AI简报** | 生成昨日简报并推送给所有订阅用户 |
| **每日 12:00** | 爬虫采集 | 采集午间资讯 |
| **每日 18:00** | 爬虫采集 | 采集晚间资讯 |

### 推送流程（每日9:00）

```
1. 定时任务触发 (scheduler.py)
   ↓
2. 调用 generate_daily_brief()
   ↓
3. AIBriefGenerator.generate_daily_brief()
   - 查询昨日文章（按分类）
   - 调用MiniMax AI生成简报
   - 保存到 daily_briefs 表
   ↓
4. AIBriefGenerator.push_brief_to_users()
   - 查询所有活跃订阅用户
   - 区分免费/基础版/高级版
   - 格式化推送内容
   ↓
5. MultiChannelPusher.push()
   - 根据订阅等级选择推送渠道
   - 并行推送到各个渠道
   ↓
6. 用户接收推送
```

---

## 📱 推送渠道

### 1. 企业微信推送（待实现）

**状态**: ⏳ 待实现  
**适用**: 所有订阅用户（免费/基础版/高级版）  
**配置**: 用户需要在个人设置中配置企业微信ID

**实现位置**:
- `backend/app/services/multi_channel_pusher.py` - `_push_wechat()` 方法

**待实现功能**:
- 集成企业微信API
- 发送文本/Markdown消息
- 发送图文消息
- 消息模板管理

### 2. 邮件推送（已实现）

**状态**: ✅ 已实现  
**适用**: 基础版、高级版用户  
**配置**: 用户需要在个人设置中配置邮箱地址

**实现位置**:
- `backend/app/services/email_push_service.py` - 邮件发送服务
- `backend/app/services/multi_channel_pusher.py` - `_push_email()` 方法

**功能特性**:
- 支持HTML格式邮件
- 支持纯文本邮件
- 邮箱格式验证
- SMTP发送

**环境配置**:
```python
# .env 文件
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=蒙小碳 <noreply@mengxiaotan.com>
```

### 3. 短信推送（已实现）

**状态**: ✅ 已实现  
**适用**: 高级版用户  
**配置**: 用户需要在个人设置中配置手机号

**实现位置**:
- `backend/app/services/sms_push_service.py` - 短信发送服务
- `backend/app/services/multi_channel_pusher.py` - `_push_sms()` 方法

**功能特性**:
- 支持阿里云短信
- 支持腾讯云短信
- 手机号格式验证（中国大陆11位）
- 内容截断（超过70字提供链接）

**环境配置**:
```python
# .env 文件
SMS_PROVIDER=aliyun  # 或 tencent
SMS_ACCESS_KEY_ID=your-access-key
SMS_ACCESS_KEY_SECRET=your-secret
SMS_SIGN_NAME=蒙小碳
SMS_TEMPLATE_CODE=SMS_123456789
```

---

## 👥 用户如何接收推送

### 当前实现状态

#### ✅ 已实现的功能

1. **定时任务系统**
   - 每日9:00自动生成AI简报
   - 每日8:00检查试用期到期
   - 凌晨1:00处理过期订阅

2. **推送服务架构**
   - 多渠道推送器（MultiChannelPusher）
   - 邮件推送服务（EmailPushService）
   - 短信推送服务（SMSPushService）

3. **权限控制**
   - 免费订阅：仅企业微信
   - 基础版：企业微信 + 邮件
   - 高级版：企业微信 + 邮件 + 短信

4. **推送内容差异化**
   - 免费订阅：基础简报（~500字）
   - 基础版：基础简报 + 企业定制内容（~1500字）
   - 高级版：完整简报 + 决策建议

#### ⏳ 待实现的功能

1. **企业微信推送**
   - 需要集成企业微信API
   - 需要配置企业微信应用
   - 需要用户绑定企业微信ID

2. **用户推送设置页面**
   - 前端页面：配置推送渠道
   - 前端页面：设置推送时间偏好
   - 前端页面：选择推送内容类型

3. **推送历史记录**
   - 记录每次推送的结果
   - 用户可查看推送历史
   - 管理员可查看推送统计

---

## 🔧 用户配置推送渠道

### 数据库结构

推送渠道配置存储在 `subscriptions` 表的 `push_channels` 字段（JSON类型）：

```json
{
  "enterprise_wechat": "user_wechat_id",
  "email": "user@example.com",
  "sms": "13800138000"
}
```

### API接口（待实现）

#### 1. 获取推送配置
```http
GET /api/users/push-settings
Authorization: Bearer <token>

Response:
{
  "subscription_level": "standard",
  "allowed_channels": ["enterprise_wechat", "email"],
  "configured_channels": {
    "enterprise_wechat": "user123",
    "email": "user@example.com",
    "sms": null
  }
}
```

#### 2. 更新推送配置
```http
PUT /api/users/push-settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "enterprise_wechat": "user123",
  "email": "user@example.com"
}

Response:
{
  "message": "推送配置已更新",
  "channels": {
    "enterprise_wechat": "user123",
    "email": "user@example.com"
  }
}
```

#### 3. 测试推送
```http
POST /api/users/test-push
Authorization: Bearer <token>
Content-Type: application/json

{
  "channel": "email",
  "message": "这是一条测试消息"
}

Response:
{
  "success": true,
  "message": "测试推送已发送"
}
```

---

## 📝 推送内容格式

### 免费订阅推送（企业微信）

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌅 蒙小碳早报 | 2026-04-16 周三
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 政策速览
• 晋城市召开煤炭与新能源融合发展现场会
• 黑龙江鸡西启动30万吨绿氢醇航油项目

📈 市场行情
• 光伏组件：隆基荣获SolarQuotes品牌榜TOP1
• 新能源发电：中节能上半年发电量同比增长22.40%

🔥 热点聚焦
• 钙钛矿太阳能电池技术突破
• 协鑫集团探索链上能源新生态

💬 蒙小碳简评
今日重点关注：
1️⃣ 煤炭与新能源融合成为转型新方向
2️⃣ 光伏技术持续创新
3️⃣ 政策支持力度加大

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 查看更多：www.mengxiaotan.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 基础版推送（企业微信 + 邮件）

在免费订阅内容基础上，增加：

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 【专属】测试能源集团 定制内容
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 企业画像更新
✅ 竞争力分析
⚠️ 风险提示
💡 机会识别

⚡ 实时预警（2条）
🔴 高级预警：煤炭与新能源融合政策
🟡 中级预警：钙钛矿太阳能电池技术突破

📈 数字沙盘提醒
• 您创建的"双碳政策影响"场景模拟已完成

📝 定制报告进度
• 您申请的"绿氢产业投资可行性分析"报告
  当前状态：✍️ 编写中

🎓 行业洞察
基于贵司画像，为您推荐：
1️⃣ 《传统能源企业转型路径研究》
2️⃣ 《绿氢产业链深度报告》

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 邮件推送格式（HTML）

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>蒙小碳早报</title>
  <style>
    body { font-family: Arial, sans-serif; }
    .header { background: #1e40af; color: white; padding: 20px; }
    .section { margin: 20px 0; }
    .alert { padding: 10px; border-left: 4px solid #ef4444; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🌅 蒙小碳早报</h1>
    <p>2026-04-16 周三</p>
  </div>
  
  <div class="section">
    <h2>📋 政策速览</h2>
    <ul>
      <li>晋城市召开煤炭与新能源融合发展现场会</li>
      <li>黑龙江鸡西启动30万吨绿氢醇航油项目</li>
    </ul>
  </div>
  
  <!-- 更多内容... -->
</body>
</html>
```

### 短信推送格式（高级版）

```
【蒙小碳】今日要闻：晋城煤炭新能源融合、鸡西绿氢项目启动、钙钛矿电池突破。您的企业有2条预警待查看。详情：https://mengxiaotan.com/brief/20260416
```

---

## 🚀 如何启用推送功能

### 步骤1：配置环境变量

编辑 `backend/.env` 文件：

```bash
# MiniMax AI配置（用于生成简报）
MINIMAX_API_KEY=your-minimax-api-key
MINIMAX_GROUP_ID=your-group-id
MINIMAX_API_URL=https://api.minimax.chat/v1/text/chatcompletion_v2

# 邮件服务配置
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=蒙小碳 <noreply@mengxiaotan.com>

# 短信服务配置（可选）
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY_ID=your-access-key
SMS_ACCESS_KEY_SECRET=your-secret
SMS_SIGN_NAME=蒙小碳
SMS_TEMPLATE_CODE=SMS_123456789

# 启用定时任务
ENABLE_SCHEDULER=True
```

### 步骤2：启动后端服务

```bash
cd backend
python run_backend.py
```

定时任务会自动启动，日志会显示：

```
✓ 添加任务: 每日AI简报生成 (每天 09:00)
✓ 添加任务: 检查试用期到期 (每天 08:00)
✓ 添加任务: 处理过期试用订阅 (每天 01:00)
✓ 定时任务调度器启动成功
```

### 步骤3：用户配置推送渠道（待实现前端页面）

用户登录后，在个人设置中配置：

1. **企业微信ID**（所有用户）
2. **邮箱地址**（基础版、高级版）
3. **手机号码**（高级版）

### 步骤4：等待推送

- 每天9:00会自动生成并推送简报
- 试用期到期前1天会收到提醒
- 监测预警会实时推送（基础版、高级版）

---

## 🧪 测试推送功能

### 手动触发简报生成

```bash
cd backend
python -c "
from app import create_app
from app.services.ai_brief_generator import AIBriefGenerator
from config import Config
from datetime import date, timedelta

app = create_app()
with app.app_context():
    generator = AIBriefGenerator(
        api_key=Config.MINIMAX_API_KEY,
        group_id=Config.MINIMAX_GROUP_ID,
        api_url=Config.MINIMAX_API_URL
    )
    
    # 生成昨天的简报
    target_date = date.today() - timedelta(days=1)
    result = generator.generate_daily_brief(target_date)
    
    if result:
        print(f'简报生成成功: {result}')
        
        # 推送简报
        push_result = generator.push_brief_to_users(result['brief_id'])
        print(f'推送结果: {push_result}')
    else:
        print('简报生成失败')
"
```

### 测试邮件推送

```bash
cd backend
python -c "
from app import create_app
from app.services.multi_channel_pusher import MultiChannelPusher

app = create_app()
with app.app_context():
    pusher = MultiChannelPusher()
    
    # 假设用户ID为1
    result = pusher.push(
        user_id=1,
        subject='测试推送',
        content='这是一条测试消息',
        channels=['email']
    )
    
    print(f'推送结果: {result}')
"
```

---

## 📊 推送统计（待实现）

### 数据库表设计

```sql
CREATE TABLE push_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    channel VARCHAR(50) NOT NULL,
    content_type VARCHAR(50),
    content_id INT,
    status VARCHAR(20),
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 统计指标

- 推送总数
- 成功率
- 各渠道使用率
- 用户打开率（需要前端埋点）
- 用户点击率（需要前端埋点）

---

## 🔍 常见问题

### Q1: 为什么我没有收到推送？

**可能原因**:
1. 订阅已过期
2. 未配置推送渠道（邮箱/手机号）
3. 推送渠道配置错误（邮箱格式、手机号格式）
4. 邮件被拦截（检查垃圾邮件箱）
5. 定时任务未启动（检查后端日志）

**解决方法**:
1. 检查订阅状态
2. 在个人设置中配置推送渠道
3. 使用测试推送功能验证配置
4. 将发件人添加到白名单
5. 检查环境变量配置

### Q2: 企业微信推送什么时候可用？

企业微信推送功能待实现，需要：
1. 注册企业微信应用
2. 获取企业微信API凭证
3. 实现企业微信推送服务
4. 用户绑定企业微信ID

预计开发时间：1-2周

### Q3: 可以自定义推送时间吗？

当前推送时间固定为每日9:00。

未来计划支持：
- 用户自定义推送时间
- 推送频率设置（每日/每周）
- 推送内容类型选择

### Q4: 推送内容可以定制吗？

当前推送内容根据订阅等级自动生成：
- 免费订阅：基础简报
- 基础版：基础简报 + 企业定制
- 高级版：完整简报 + 决策建议

未来计划支持：
- 用户选择关注的行业
- 用户选择关注的主题
- 用户自定义关键词监测

---

## 📚 相关文档

- [订阅系统开发进度](SUBSCRIPTION_DEVELOPMENT_PROGRESS.md)
- [推送报告示例](SAMPLE_PUSH_REPORTS.md)
- [项目完成报告](PROJECT_COMPLETE_FINAL_REPORT.md)
- [测试指南](TESTING_SUMMARY.md)

---

**文档状态**: ✅ 完整  
**最后更新**: 2026-04-16  
**维护者**: 开发团队
