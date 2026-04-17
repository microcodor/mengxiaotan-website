-- 添加用户表的企业相关字段
ALTER TABLE users 
ADD COLUMN position VARCHAR(100) COMMENT '职位',
ADD COLUMN company_id INT COMMENT '所属企业',
ADD INDEX idx_company_id (company_id);

-- 添加外键约束（如果需要）
-- ALTER TABLE users ADD CONSTRAINT fk_users_company FOREIGN KEY (company_id) REFERENCES companies(id);
