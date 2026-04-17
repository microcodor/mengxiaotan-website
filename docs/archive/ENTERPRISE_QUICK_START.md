# 企业信息管理功能 - 快速开始指南

## 一、执行数据库迁移

### 方式1：使用迁移脚本（推荐）

```bash
cd backend
./run_company_migration.sh
```

### 方式2：手动执行SQL

```bash
docker exec energy_mysql mysql -u root -ppassword energy_station -e "
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS position VARCHAR(100) COMMENT '职位',
ADD COLUMN IF NOT EXISTS company_id INT COMMENT '所属企业',
ADD INDEX IF NOT EXISTS idx_company_id (company_id);
"
```

### 方式3：使用SQL文件

```bash
docker exec -i energy_mysql mysql -u root -ppassword energy_station < backend/migrations/add_user_company_fields.sql
```

## 二、功能访问路径

### 用户侧（需要登录）

1. **企业信息管理**
   - 路径：`http://localhost:5173/dashboard/company`
   - 功能：创建和编辑企业基础信息

2. **主营业务管理**
   - 路径：`http://localhost:5173/dashboard/company/business`
   - 功能：添加、编辑、删除企业主营业务

3. **个人信息**
   - 路径：`http://localhost:5173/dashboard/profile`
   - 功能：更新个人昵称和职位

### 管理员侧（需要管理员权限）

1. **企业管理**
   - 路径：`http://localhost:5173/admin/companies`
   - 功能：查看企业列表、审核企业认证

## 三、使用流程

### 用户操作流程

1. **登录系统**
   - 使用手机号和密码登录

2. **填写个人信息**
   - 进入"个人信息"页面
   - 填写昵称和职位
   - 点击"保存修改"

3. **创建企业信息**
   - 进入"企业信息"页面
   - 填写企业基础信息（必填项：企业名称、联系人、联系电话）
   - 填写其他可选信息
   - 点击"创建企业"

4. **添加主营业务**
   - 进入"主营业务"页面
   - 点击"添加业务"按钮
   - 填写业务信息（必填项：业务类型、业务名称）
   - 添加核心产品和资质认证
   - 勾选"设为主营业务"（可选）
   - 点击"创建"

5. **管理业务**
   - 编辑业务：点击编辑按钮
   - 删除业务：点击删除按钮
   - 设为主营：点击星标按钮

### 管理员操作流程

1. **登录管理后台**
   - 使用管理员账号登录（13800138000 / admin123）
   - 进入管理后台

2. **查看企业列表**
   - 进入"企业管理"页面
   - 查看所有企业信息
   - 使用状态筛选（全部/待审核/已认证/未通过）

3. **审核企业**
   - 点击"查看详情"按钮查看企业完整信息
   - 点击"通过认证"（绿色按钮）通过审核
   - 点击"拒绝认证"（红色按钮）拒绝审核

## 四、API接口说明

### 企业信息接口

```
GET    /api/company/options              # 获取选项数据（公开）
GET    /api/company/my                   # 获取我的企业信息
POST   /api/company/my                   # 创建企业信息
PUT    /api/company/my                   # 更新企业信息
```

### 主营业务接口

```
GET    /api/company/my/businesses        # 获取业务列表
POST   /api/company/my/businesses        # 创建业务
PUT    /api/company/my/businesses/:id    # 更新业务
DELETE /api/company/my/businesses/:id    # 删除业务
POST   /api/company/my/businesses/:id/set-primary  # 设为主营
```

### 管理员接口

```
GET    /api/company/admin/list           # 获取企业列表
GET    /api/company/admin/:id            # 获取企业详情
POST   /api/company/admin/:id/verify     # 审核企业
```

### 用户接口

```
GET    /api/users/profile                # 获取个人信息
PUT    /api/users/profile                # 更新个人信息（支持position字段）
```

## 五、数据字段说明

### 企业信息字段

**基础信息**
- 企业名称 *（必填）
- 企业简称
- 统一社会信用代码
- 法定代表人
- 注册资本
- 成立日期

**联系信息**
- 联系人 *（必填）
- 联系电话 *（必填）
- 联系邮箱

**地址信息**
- 省份
- 城市
- 区县
- 详细地址

**企业规模**
- 员工人数（下拉选择）
- 年营业额（下拉选择）

**行业信息**
- 所属行业
- 行业类别（下拉选择）

**企业简介**
- 企业描述
- 企业网站

### 主营业务字段

**业务信息**
- 业务类型 *（必填，下拉选择）
- 业务名称 *（必填）
- 业务范围描述

**业务规模**
- 年产量/产能
- 市场份额
- 服务区域

**业务特点**
- 核心产品列表（动态添加）
- 资质认证列表（动态添加）

**状态**
- 是否主营业务
- 是否启用

### 业务类型选项

1. **煤炭**：煤炭开采、煤炭洗选、煤炭贸易、煤炭运输、煤炭深加工
2. **电力**：火力发电、水力发电、风力发电、光伏发电、电力销售、电力工程
3. **油气**：石油开采、天然气开采、油气炼化、油气贸易、油气储运
4. **新能源**：光伏组件、风电设备、储能系统、新能源汽车、氢能
5. **钢铁**：钢铁冶炼、钢材加工、钢材贸易、废钢回收
6. **化工**：基础化工、精细化工、化工贸易、化工设备
7. **设备制造**：能源设备、环保设备、自动化设备、设备维修
8. **服务**：技术咨询、工程设计、项目管理、检测认证、培训教育
9. **贸易**：能源贸易、大宗商品、进出口贸易、供应链管理
10. **其他**：其他业务

## 六、常见问题

### Q1: 数据库迁移失败怎么办？

**A**: 检查以下几点：
1. MySQL容器是否正在运行：`docker ps | grep mysql`
2. 数据库连接信息是否正确（端口3307，密码123456）
3. 手动登录数据库检查：`docker exec -it mengxiaotan-mysql mysql -u root -p123456`

### Q2: 创建企业信息时提示"统一社会信用代码已被使用"？

**A**: 该信用代码已被其他企业使用，请检查是否重复创建或使用正确的信用代码。

### Q3: 如何修改企业信息？

**A**: 进入"企业信息"页面，修改相应字段后点击"更新信息"按钮。

### Q4: 如何设置主营业务？

**A**: 在"主营业务"页面，点击业务卡片右上角的星标按钮即可设为主营业务。

### Q5: 管理员如何查看企业详情？

**A**: 在企业列表中点击"查看详情"（眼睛图标）按钮。

### Q6: 企业认证状态有哪些？

**A**: 
- **待审核**（pending）：企业刚创建，等待管理员审核
- **已认证**（active）：管理员已通过认证
- **未通过**（inactive）：管理员拒绝认证

## 七、测试数据示例

### 企业信息示例

```json
{
  "name": "山西煤炭集团有限公司",
  "short_name": "山西煤炭",
  "unified_social_credit_code": "91140000123456789X",
  "legal_representative": "张三",
  "registered_capital": "50000万元",
  "establishment_date": "2010-01-15",
  "contact_person": "李四",
  "contact_phone": "13900000001",
  "contact_email": "contact@sxcoal.com",
  "province": "山西省",
  "city": "太原市",
  "district": "小店区",
  "address": "煤炭大厦18层",
  "employee_count": "1001-5000人",
  "annual_revenue": "10亿以上",
  "industry": "煤炭开采和洗选业",
  "industry_category": "coal",
  "description": "山西省大型煤炭企业，主营煤炭开采、洗选和销售业务。",
  "website": "https://www.sxcoal.com"
}
```

### 主营业务示例

```json
{
  "business_type": "coal",
  "business_name": "煤炭开采与洗选",
  "business_scope": "主要从事优质动力煤和炼焦煤的开采、洗选和销售业务，年产能1000万吨。",
  "annual_output": "年产煤炭1000万吨",
  "market_share": "山西省市场占有率8%",
  "service_area": "华北地区、华东地区",
  "core_products": ["动力煤", "炼焦煤", "洗精煤"],
  "certifications": ["安全生产标准化一级企业", "ISO9001质量管理体系认证"],
  "is_primary": true,
  "is_active": true
}
```

## 八、技术支持

如有问题，请查看：
- 设计文档：`ENTERPRISE_INFO_DESIGN.md`
- 实施总结：`ENTERPRISE_IMPLEMENTATION_SUMMARY.md`
- 后端API代码：`backend/app/api/company.py`
- 前端页面代码：`frontend/src/pages/CompanyInfo.tsx`、`frontend/src/pages/CompanyBusiness.tsx`
