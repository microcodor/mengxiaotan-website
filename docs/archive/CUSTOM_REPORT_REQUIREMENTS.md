# 定制报告功能需求文档

**版本**: 1.0  
**创建时间**: 2026-04-16  
**功能**: 第五阶段 - 定制报告申请流程

---

## 📋 功能概述

定制报告功能允许基础版用户每月申请2份定制报告，由系统AI辅助生成或人工编写，提供深度的行业分析和战略建议。

---

## 🎯 核心价值

### 用户价值
- **深度分析** - 专业的行业分析报告
- **定制化** - 针对企业特定需求
- **战略指导** - 提供可执行的建议
- **专家服务** - AI+人工的双重保障

### 业务价值
- **增值服务** - 提升订阅价值
- **用户粘性** - 增强用户依赖
- **数据积累** - 积累行业知识
- **差异化** - 区别于竞品

---

## 👥 用户故事

### 故事1：申请定制报告
**作为** 基础版订阅用户  
**我想要** 申请一份关于技术路线优化的定制报告  
**以便** 获得专业的技术选型建议

**验收标准**:
- 可以填写报告需求表单
- 可以选择报告类型
- 可以查看剩余配额
- 提交后收到确认通知

### 故事2：查看申请记录
**作为** 基础版订阅用户  
**我想要** 查看我的报告申请历史  
**以便** 了解申请状态和下载已完成的报告

**验收标准**:
- 可以查看所有申请记录
- 可以查看申请状态
- 可以下载已完成的报告
- 可以查看报告详情

### 故事3：管理报告申请
**作为** 管理员  
**我想要** 查看和处理用户的报告申请  
**以便** 及时响应用户需求

**验收标准**:
- 可以查看所有待处理申请
- 可以分配报告给编写人员
- 可以上传完成的报告
- 可以标记申请状态

---

## 🔧 功能需求

### 1. 报告类型

#### 1.1 技术路线优化
**描述**: 分析不同技术方案的经济性和可行性

**内容包括**:
- 技术方案对比
- 经济性分析
- 风险评估
- 实施建议

**示例**:
- 煤制油与绿氢耦合经济性对比
- 光伏+储能vs风电+储能方案对比
- CCUS技术应用可行性分析

#### 1.2 区域市场布局
**描述**: 分析特定区域的市场机会和布局建议

**内容包括**:
- 区域市场分析
- 竞争格局分析
- 进入策略建议
- 风险提示

**示例**:
- 蒙西电网消纳能力分析
- 长三角氢能市场布局建议
- 西北新能源基地投资机会

#### 1.3 政策影响分析
**描述**: 深度解读政策对企业的影响

**内容包括**:
- 政策解读
- 影响评估
- 应对策略
- 机会识别

**示例**:
- 双碳政策对煤化工企业的影响
- 新能源补贴政策变化应对
- 碳交易市场参与策略

#### 1.4 竞争对手分析
**描述**: 分析主要竞争对手的战略和动向

**内容包括**:
- 竞争对手画像
- 战略分析
- 优劣势对比
- 应对建议

#### 1.5 投资决策支持
**描述**: 为重大投资决策提供数据支持

**内容包括**:
- 项目可行性分析
- 财务测算
- 风险评估
- 投资建议

---

### 2. 申请流程

#### 2.1 申请表单
**必填字段**:
- 报告类型（下拉选择）
- 报告标题（文本输入）
- 需求描述（富文本编辑器）
- 期望交付时间（日期选择）
- 附加说明（可选）

**配额检查**:
- 显示本月剩余配额
- 配额不足时禁止提交
- 配额每月1号重置

**提交确认**:
- 显示申请摘要
- 确认消耗配额
- 提交后发送通知

#### 2.2 申请状态
- **pending** - 待处理
- **assigned** - 已分配
- **in_progress** - 进行中
- **completed** - 已完成
- **rejected** - 已拒绝

#### 2.3 状态流转
```
pending → assigned → in_progress → completed
   ↓
rejected
```

---

### 3. 报告生成

#### 3.1 AI辅助生成
**使用场景**:
- 标准化报告类型
- 数据驱动的分析
- 快速响应需求

**生成流程**:
1. 提取申请需求
2. 收集相关数据
3. 调用AI模型生成
4. 人工审核修改
5. 交付用户

#### 3.2 人工编写
**使用场景**:
- 复杂定制需求
- 需要深度调研
- 战略级建议

**编写流程**:
1. 需求分析
2. 资料收集
3. 报告编写
4. 内部审核
5. 交付用户

---

### 4. 报告交付

#### 4.1 交付方式
- **在线查看** - 网页版报告
- **PDF下载** - 可打印版本
- **Word下载** - 可编辑版本

#### 4.2 交付通知
- 企业微信通知
- 邮件通知
- 站内消息

#### 4.3 报告格式
**标准结构**:
1. 封面（标题、日期、企业名称）
2. 目录
3. 执行摘要
4. 正文内容
5. 数据附录
6. 免责声明

---

## 📊 数据库设计

### report_requests 表（报告申请）
```sql
CREATE TABLE report_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    expected_delivery_date DATE,
    additional_notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_to INT,
    assigned_at DATETIME,
    completed_at DATETIME,
    rejected_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_company_id (company_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### report_files 表（报告文件）
```sql
CREATE TABLE report_files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size INT NOT NULL,
    uploaded_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES report_requests(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    INDEX idx_request_id (request_id)
);
```

### report_quota_usage 表（配额使用记录）
```sql
CREATE TABLE report_quota_usage (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    used_quota INT DEFAULT 0,
    total_quota INT DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_user_year_month (user_id, year, month),
    INDEX idx_user_id (user_id)
);
```

---

## 🔐 权限控制

### 访问权限
- **免费订阅**: 无法访问
- **基础版**: 可以申请（2份/月）
- **管理员**: 可以管理所有申请

### 配额限制
- 每月2份报告
- 每月1号重置配额
- 配额不累积到下月

---

## 🎨 UI/UX设计要点

### 1. 申请页面
- 清晰的表单布局
- 实时配额显示
- 报告类型说明
- 示例参考

### 2. 申请列表
- 卡片式展示
- 状态标识
- 快速操作
- 筛选和搜索

### 3. 报告详情
- 申请信息展示
- 状态时间线
- 报告预览
- 下载按钮

---

## 📈 成功指标

### 功能指标
- 申请提交成功率 > 95%
- 报告交付及时率 > 90%
- 用户满意度 > 4.0/5.0

### 业务指标
- 月均申请量 > 50份
- 配额使用率 > 60%
- 报告下载率 > 80%

---

## 🚀 开发计划

### 阶段1：后端开发（2天）
- [ ] 数据库表设计
- [ ] 报告申请API
- [ ] 配额管理逻辑
- [ ] 文件上传下载

### 阶段2：前端开发（2天）
- [ ] 申请表单页面
- [ ] 申请列表页面
- [ ] 报告详情页面
- [ ] 管理后台页面

### 阶段3：测试优化（1天）
- [ ] 功能测试
- [ ] 配额测试
- [ ] 文件测试
- [ ] 用户体验优化

**总计**: 5天

---

## 💡 未来扩展

### 短期扩展
1. **报告模板** - 预设报告模板
2. **AI生成** - 接入大模型自动生成
3. **报告评价** - 用户评价和反馈
4. **报告分享** - 团队内部分享

### 长期扩展
1. **报告订阅** - 定期生成报告
2. **报告市场** - 报告交易平台
3. **专家咨询** - 一对一咨询服务
4. **行业报告库** - 通用行业报告

---

**文档版本**: 1.0  
**最后更新**: 2026-04-16  
**负责人**: 开发团队
