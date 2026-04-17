# 动态监测预警功能需求文档

**版本**: 1.0  
**创建时间**: 2026-04-16  
**功能**: 第六阶段 - 动态监测预警功能

---

## 📋 功能概述

动态监测预警功能实时监测政策变化、价格波动和行业动态，当触发预警条件时自动推送通知给相关企业用户。

---

## 🎯 核心价值

### 用户价值
- **实时预警** - 第一时间获知重要信息
- **精准推送** - 只推送与企业相关的内容
- **风险防范** - 提前识别潜在风险
- **机会把握** - 及时发现市场机会

### 业务价值
- **增值服务** - 提升订阅价值
- **用户粘性** - 增强用户依赖
- **差异化** - 区别于竞品
- **数据价值** - 积累监测数据

---

## 🔧 功能需求

### 1. 监测类型

#### 1.1 政策监测
**监测内容**:
- 国家政策发布
- 地方政策变化
- 行业标准更新
- 补贴政策调整

**预警条件**:
- 包含企业相关关键词
- 影响企业所在行业
- 影响企业所在地区

#### 1.2 价格监测
**监测内容**:
- 煤炭价格指数
- 油气价格
- 电力价格
- 新能源价格

**预警条件**:
- 价格波动超过阈值（如±10%）
- 连续上涨/下跌
- 突破历史高点/低点

#### 1.3 行业动态监测
**监测内容**:
- 行业新闻
- 技术突破
- 竞争对手动态
- 市场趋势

**预警条件**:
- 包含企业关注的关键词
- 涉及企业主营业务
- 重大行业事件

---

### 2. 监测规则

#### 2.1 规则配置
**规则字段**:
- 规则名称
- 监测类型
- 关键词列表
- 预警阈值
- 预警等级（高/中/低）
- 推送渠道
- 启用状态

**示例规则**:
```json
{
  "name": "煤炭价格预警",
  "type": "price",
  "keywords": ["煤炭", "动力煤"],
  "threshold": 10,
  "level": "high",
  "channels": ["enterprise_wechat", "email"],
  "enabled": true
}
```

#### 2.2 规则匹配
**匹配逻辑**:
1. 获取最新文章/数据
2. 提取关键信息
3. 匹配用户规则
4. 计算预警等级
5. 触发预警推送

---

### 3. 预警系统

#### 3.1 预警等级
- **高** - 重大影响，立即推送
- **中** - 一般影响，汇总推送
- **低** - 参考信息，每日推送

#### 3.2 预警内容
**标准格式**:
- 预警标题
- 预警等级
- 触发原因
- 详细内容
- 建议措施
- 相关链接

#### 3.3 推送策略
- **高等级**: 立即推送
- **中等级**: 每4小时汇总推送
- **低等级**: 每日汇总推送

---

## 📊 数据库设计

### monitoring_rules 表（监测规则）
```sql
CREATE TABLE monitoring_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    keywords JSON NOT NULL,
    threshold DECIMAL(10,2),
    level VARCHAR(20) DEFAULT 'medium',
    channels JSON NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### monitoring_alerts 表（预警记录）
```sql
CREATE TABLE monitoring_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rule_id INT NOT NULL,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    level VARCHAR(20) NOT NULL,
    source_type VARCHAR(50),
    source_id INT,
    status VARCHAR(20) DEFAULT 'pending',
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 UI/UX设计要点

### 1. 规则管理页面
- 规则列表（卡片式）
- 创建规则按钮
- 启用/禁用开关
- 编辑/删除操作

### 2. 预警列表页面
- 预警卡片（按等级分组）
- 时间筛选
- 状态筛选
- 详情查看

### 3. 预警详情页面
- 预警信息展示
- 触发原因说明
- 建议措施
- 相关文章链接

---

## 🚀 开发计划

### 简化实现方案
由于时间限制，采用简化方案：

1. **后端服务**（1小时）
   - 监测规则管理
   - 预警记录管理
   - 基础匹配逻辑

2. **前端界面**（1小时）
   - 规则管理页面
   - 预警列表页面
   - 简化的配置表单

3. **集成测试**（30分钟）
   - 功能验证
   - 文档整理

**总计**: 2.5小时

---

## 💡 未来扩展

### 短期扩展
1. **智能匹配** - AI分析文章相关性
2. **预警分析** - 预警趋势统计
3. **规则模板** - 预设规则模板

### 长期扩展
1. **实时监测** - WebSocket实时推送
2. **智能推荐** - 推荐监测规则
3. **数据分析** - 预警数据分析

---

**文档版本**: 1.0  
**最后更新**: 2026-04-16  
**负责人**: 开发团队
