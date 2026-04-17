# 企业信息管理功能设计

## 一、数据模型设计

### 1. User 用户表（扩展字段）

在现有 User 模型基础上增加：

```python
class User(db.Model):
    # ... 现有字段 ...
    
    # 新增字段
    position = db.Column(db.String(100))  # 职位
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # 所属企业
    
    # 关系
    company = db.relationship('Company', backref='employees')
```

**新增字段说明：**
- `position`: 用户职位（如：总经理、采购经理、技术总监等）
- `company_id`: 关联企业ID（外键）

---

### 2. Company 企业信息表（新建）

```python
class Company(db.Model):
    __tablename__ = 'companies'
    
    # 基础信息
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 企业名称
    short_name = db.Column(db.String(100))  # 企业简称
    unified_social_credit_code = db.Column(db.String(50), unique=True)  # 统一社会信用代码
    legal_representative = db.Column(db.String(50))  # 法定代表人
    registered_capital = db.Column(db.String(50))  # 注册资本
    establishment_date = db.Column(db.Date)  # 成立日期
    
    # 联系信息
    contact_person = db.Column(db.String(50))  # 联系人
    contact_phone = db.Column(db.String(20))  # 联系电话
    contact_email = db.Column(db.String(100))  # 联系邮箱
    
    # 地址信息
    province = db.Column(db.String(50))  # 省份
    city = db.Column(db.String(50))  # 城市
    district = db.Column(db.String(50))  # 区县
    address = db.Column(db.String(255))  # 详细地址
    
    # 企业规模
    employee_count = db.Column(db.String(50))  # 员工人数（如：50-100人、100-500人）
    annual_revenue = db.Column(db.String(50))  # 年营业额（如：1000万-5000万）
    
    # 行业信息
    industry = db.Column(db.String(100))  # 所属行业
    industry_category = db.Column(db.String(50))  # 行业类别（能源/电力/煤炭/钢铁等）
    
    # 企业简介
    description = db.Column(db.Text)  # 企业简介
    website = db.Column(db.String(255))  # 企业网站
    logo = db.Column(db.String(255))  # 企业Logo
    
    # 认证信息
    business_license = db.Column(db.String(255))  # 营业执照图片
    is_verified = db.Column(db.Boolean, default=False)  # 是否认证
    verified_at = db.Column(db.DateTime)  # 认证时间
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 认证人
    
    # 状态
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies')
    verifier = db.relationship('User', foreign_keys=[verified_by])
```

**字段分类：**

#### 基础信息（必填）
- `name`: 企业名称 *
- `short_name`: 企业简称
- `unified_social_credit_code`: 统一社会信用代码 *
- `legal_representative`: 法定代表人
- `registered_capital`: 注册资本
- `establishment_date`: 成立日期

#### 联系信息（必填）
- `contact_person`: 联系人 *
- `contact_phone`: 联系电话 *
- `contact_email`: 联系邮箱 *

#### 地址信息
- `province`: 省份 *
- `city`: 城市 *
- `district`: 区县
- `address`: 详细地址 *

#### 企业规模
- `employee_count`: 员工人数
- `annual_revenue`: 年营业额

#### 行业信息（必填）
- `industry`: 所属行业 *
- `industry_category`: 行业类别 *

#### 其他信息
- `description`: 企业简介
- `website`: 企业网站
- `logo`: 企业Logo
- `business_license`: 营业执照

---

### 3. CompanyBusiness 主营业务表（新建）

```python
class CompanyBusiness(db.Model):
    __tablename__ = 'company_businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # 业务信息
    business_type = db.Column(db.String(50), nullable=False)  # 业务类型
    business_name = db.Column(db.String(200), nullable=False)  # 业务名称
    business_scope = db.Column(db.Text)  # 业务范围描述
    
    # 业务规模
    annual_output = db.Column(db.String(100))  # 年产量/产能
    market_share = db.Column(db.String(50))  # 市场份额
    
    # 业务区域
    service_area = db.Column(db.String(255))  # 服务区域（如：华北地区、全国）
    
    # 业务特点
    core_products = db.Column(db.JSON)  # 核心产品列表
    certifications = db.Column(db.JSON)  # 资质认证列表
    
    # 排序和状态
    sort_order = db.Column(db.Integer, default=0)  # 排序
    is_primary = db.Column(db.Boolean, default=False)  # 是否主营业务
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    company = db.relationship('Company', backref='businesses')
```

**字段说明：**

#### 业务基本信息
- `business_type`: 业务类型（生产、贸易、服务、研发等）
- `business_name`: 业务名称（如：煤炭开采、电力销售、钢材贸易）
- `business_scope`: 业务范围详细描述

#### 业务规模
- `annual_output`: 年产量/产能（如：年产煤炭500万吨）
- `market_share`: 市场份额（如：华北地区15%）
- `service_area`: 服务区域

#### 业务特点
- `core_products`: 核心产品（JSON数组）
- `certifications`: 资质认证（JSON数组）

#### 管理字段
- `sort_order`: 排序
- `is_primary`: 是否主营业务
- `is_active`: 是否启用

---

## 二、业务类型预设值

### 1. 能源行业业务类型
```python
BUSINESS_TYPES = {
    'coal': {
        'name': '煤炭',
        'subtypes': ['煤炭开采', '煤炭洗选', '煤炭贸易', '煤炭运输', '煤炭深加工']
    },
    'power': {
        'name': '电力',
        'subtypes': ['火力发电', '水力发电', '风力发电', '光伏发电', '电力销售', '电力工程']
    },
    'oil_gas': {
        'name': '油气',
        'subtypes': ['石油开采', '天然气开采', '油气炼化', '油气贸易', '油气储运']
    },
    'new_energy': {
        'name': '新能源',
        'subtypes': ['光伏组件', '风电设备', '储能系统', '新能源汽车', '氢能']
    },
    'steel': {
        'name': '钢铁',
        'subtypes': ['钢铁冶炼', '钢材加工', '钢材贸易', '废钢回收']
    },
    'chemical': {
        'name': '化工',
        'subtypes': ['基础化工', '精细化工', '化工贸易', '化工设备']
    },
    'equipment': {
        'name': '设备制造',
        'subtypes': ['能源设备', '环保设备', '自动化设备', '设备维修']
    },
    'service': {
        'name': '服务',
        'subtypes': ['技术咨询', '工程设计', '项目管理', '检测认证', '培训教育']
    },
    'trade': {
        'name': '贸易',
        'subtypes': ['能源贸易', '大宗商品', '进出口贸易', '供应链管理']
    },
    'other': {
        'name': '其他',
        'subtypes': ['其他业务']
    }
}
```

### 2. 企业规模选项
```python
EMPLOYEE_COUNT_OPTIONS = [
    '1-50人',
    '51-100人',
    '101-500人',
    '501-1000人',
    '1001-5000人',
    '5000人以上'
]

ANNUAL_REVENUE_OPTIONS = [
    '100万以下',
    '100万-500万',
    '500万-1000万',
    '1000万-5000万',
    '5000万-1亿',
    '1亿-10亿',
    '10亿以上'
]
```

### 3. 行业类别选项
```python
INDUSTRY_CATEGORIES = [
    {'code': 'coal', 'name': '煤炭'},
    {'code': 'power', 'name': '电力'},
    {'code': 'oil_gas', 'name': '油气'},
    {'code': 'new_energy', 'name': '新能源'},
    {'code': 'steel', 'name': '钢铁'},
    {'code': 'nonferrous_metals', 'name': '有色金属'},
    {'code': 'chemical', 'name': '化工'},
    {'code': 'cement', 'name': '水泥建材'},
    {'code': 'equipment', 'name': '设备制造'},
    {'code': 'service', 'name': '技术服务'},
    {'code': 'trade', 'name': '贸易流通'},
    {'code': 'other', 'name': '其他'}
]
```

---

## 三、API 接口设计

### 1. 企业信息管理

#### 获取企业信息
```
GET /api/users/company
```

#### 创建/更新企业信息
```
POST /api/users/company
PUT /api/users/company
```

#### 上传企业Logo
```
POST /api/users/company/logo
```

#### 上传营业执照
```
POST /api/users/company/business-license
```

### 2. 主营业务管理

#### 获取业务列表
```
GET /api/users/company/businesses
```

#### 创建业务
```
POST /api/users/company/businesses
```

#### 更新业务
```
PUT /api/users/company/businesses/:id
```

#### 删除业务
```
DELETE /api/users/company/businesses/:id
```

#### 设置主营业务
```
POST /api/users/company/businesses/:id/set-primary
```

### 3. 用户信息管理

#### 更新用户职位
```
PUT /api/users/profile
Body: { "position": "总经理" }
```

### 4. 管理员接口

#### 企业认证审核
```
POST /api/admin/companies/:id/verify
```

#### 企业列表
```
GET /api/admin/companies
```

---

## 四、前端页面设计

### 1. 用户侧页面

#### 企业信息页面 (`/dashboard/company`)

**页面结构：**
```
┌─────────────────────────────────────┐
│ 企业基础信息                          │
├─────────────────────────────────────┤
│ 企业名称: [__________]               │
│ 统一社会信用代码: [__________]        │
│ 法定代表人: [__________]             │
│ 注册资本: [__________]               │
│ 成立日期: [__________]               │
│                                     │
│ 联系信息                             │
│ 联系人: [__________]                 │
│ 联系电话: [__________]               │
│ 联系邮箱: [__________]               │
│                                     │
│ 地址信息                             │
│ 省份: [下拉] 城市: [下拉] 区县: [下拉] │
│ 详细地址: [__________]               │
│                                     │
│ 企业规模                             │
│ 员工人数: [下拉]                     │
│ 年营业额: [下拉]                     │
│                                     │
│ 行业信息                             │
│ 所属行业: [__________]               │
│ 行业类别: [下拉多选]                  │
│                                     │
│ 企业简介                             │
│ [文本框]                             │
│                                     │
│ 企业Logo: [上传]                     │
│ 营业执照: [上传]                     │
│                                     │
│ [保存] [取消]                        │
└─────────────────────────────────────┘
```

#### 主营业务页面 (`/dashboard/company/businesses`)

**页面结构：**
```
┌─────────────────────────────────────┐
│ 主营业务管理          [+ 添加业务]    │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 业务1: 煤炭开采        [主营]    │ │
│ │ 年产量: 500万吨                  │ │
│ │ 服务区域: 华北地区                │ │
│ │ [编辑] [删除] [设为主营]          │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 业务2: 煤炭贸易                  │ │
│ │ 年产量: 200万吨                  │ │
│ │ 服务区域: 全国                   │ │
│ │ [编辑] [删除] [设为主营]          │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### 个人信息页面（扩展）

在现有个人信息页面增加：
```
职位: [__________]
所属企业: [显示企业名称]
```

### 2. 管理员侧页面

#### 企业管理页面 (`/admin/companies`)

**功能：**
- 企业列表展示
- 企业认证审核
- 企业信息查看
- 企业状态管理

---

## 五、数据库迁移脚本

```python
# backend/migrations/add_company_info.py

def upgrade():
    # 1. 创建 companies 表
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        # ... 其他字段
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. 创建 company_businesses 表
    op.create_table('company_businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        # ... 其他字段
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 3. 扩展 users 表
    op.add_column('users', sa.Column('position', sa.String(100)))
    op.add_column('users', sa.Column('company_id', sa.Integer()))
    op.create_foreign_key('fk_users_company', 'users', 'companies', ['company_id'], ['id'])

def downgrade():
    # 回滚操作
    pass
```

---

## 六、实施步骤

### 第一步：数据库模型
1. 创建 Company 模型
2. 创建 CompanyBusiness 模型
3. 扩展 User 模型（添加 position 和 company_id）
4. 运行数据库迁移

### 第二步：后端API
1. 创建企业信息管理API
2. 创建主营业务管理API
3. 扩展用户信息API
4. 创建管理员审核API

### 第三步：前端页面
1. 创建企业信息页面
2. 创建主营业务页面
3. 更新个人信息页面
4. 创建管理员企业管理页面

### 第四步：测试验证
1. 功能测试
2. 数据验证
3. 权限测试
4. 用户体验测试

---

## 七、权限控制

### 用户权限
- 只能查看和编辑自己所属企业的信息
- 只能管理自己企业的主营业务
- 可以更新自己的职位信息

### 管理员权限
- 可以查看所有企业信息
- 可以审核企业认证
- 可以管理企业状态
- 可以查看企业统计数据

---

## 八、注意事项

### 数据安全
1. 营业执照等敏感信息需要加密存储
2. 统一社会信用代码需要唯一性验证
3. 企业信息修改需要记录操作日志

### 用户体验
1. 表单填写提供智能提示
2. 地址信息支持级联选择
3. 文件上传支持预览
4. 保存前进行数据验证

### 业务逻辑
1. 一个用户只能关联一个企业
2. 一个企业可以有多个员工
3. 企业信息修改后需要重新认证
4. 主营业务至少保留一个

---

## 九、扩展功能（可选）

### 1. 企业认证等级
- 基础认证：提交基本信息
- 实名认证：上传营业执照
- 高级认证：提供更多资质证明

### 2. 企业标签
- 行业标签
- 规模标签
- 区域标签
- 特色标签

### 3. 企业关系
- 上下游企业关联
- 合作伙伴关系
- 竞争对手分析

### 4. 数据统计
- 企业数量统计
- 行业分布统计
- 区域分布统计
- 规模分布统计

---

## 总结

本设计方案提供了完整的企业信息管理功能，包括：
- ✅ 企业基础信息（20+字段）
- ✅ 主营业务管理（支持多个业务）
- ✅ 用户职位字段
- ✅ 完整的API接口
- ✅ 前端页面设计
- ✅ 权限控制方案

可以根据实际需求进行调整和扩展。
