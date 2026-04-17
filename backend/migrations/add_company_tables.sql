-- 添加企业信息相关表

-- 1. 创建 companies 表
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '企业名称',
    short_name VARCHAR(100) COMMENT '企业简称',
    unified_social_credit_code VARCHAR(50) UNIQUE COMMENT '统一社会信用代码',
    legal_representative VARCHAR(50) COMMENT '法定代表人',
    registered_capital VARCHAR(50) COMMENT '注册资本',
    establishment_date DATE COMMENT '成立日期',
    
    contact_person VARCHAR(50) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    
    province VARCHAR(50) COMMENT '省份',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '区县',
    address VARCHAR(255) COMMENT '详细地址',
    
    employee_count VARCHAR(50) COMMENT '员工人数',
    annual_revenue VARCHAR(50) COMMENT '年营业额',
    
    industry VARCHAR(100) COMMENT '所属行业',
    industry_category VARCHAR(50) COMMENT '行业类别',
    
    description TEXT COMMENT '企业简介',
    website VARCHAR(255) COMMENT '企业网站',
    logo VARCHAR(255) COMMENT '企业Logo',
    
    business_license VARCHAR(255) COMMENT '营业执照图片',
    is_verified BOOLEAN DEFAULT FALSE COMMENT '是否认证',
    verified_at DATETIME COMMENT '认证时间',
    verified_by INT COMMENT '认证人',
    
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by INT COMMENT '创建人',
    
    INDEX idx_unified_social_credit_code (unified_social_credit_code),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (verified_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业信息表';

-- 2. 创建 company_businesses 表
CREATE TABLE IF NOT EXISTS company_businesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL COMMENT '企业ID',
    
    business_type VARCHAR(50) NOT NULL COMMENT '业务类型',
    business_name VARCHAR(200) NOT NULL COMMENT '业务名称',
    business_scope TEXT COMMENT '业务范围描述',
    
    annual_output VARCHAR(100) COMMENT '年产量/产能',
    market_share VARCHAR(50) COMMENT '市场份额',
    service_area VARCHAR(255) COMMENT '服务区域',
    
    core_products JSON COMMENT '核心产品列表',
    certifications JSON COMMENT '资质认证列表',
    
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_primary BOOLEAN DEFAULT FALSE COMMENT '是否主营业务',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_company_id (company_id),
    INDEX idx_is_primary (is_primary),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业主营业务表';

-- 3. 扩展 users 表
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS position VARCHAR(100) COMMENT '职位',
ADD COLUMN IF NOT EXISTS company_id INT COMMENT '所属企业',
ADD INDEX IF NOT EXISTS idx_company_id (company_id),
ADD CONSTRAINT IF NOT EXISTS fk_users_company FOREIGN KEY (company_id) REFERENCES companies(id);

-- 显示结果
SELECT 'Tables created successfully!' AS message;
