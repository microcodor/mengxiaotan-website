#!/bin/bash
# 企业信息功能数据库迁移脚本

echo "=========================================="
echo "企业信息功能数据库迁移"
echo "=========================================="
echo ""

# 检查 Docker 容器是否运行
if ! docker ps | grep -q energy_mysql; then
    echo "❌ MySQL容器未运行，请先启动容器"
    exit 1
fi

echo "✓ MySQL容器正在运行"
echo ""

# 执行迁移
echo "正在添加 users 表字段..."
docker exec energy_mysql mysql -u root -ppassword energy_station -e "
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS position VARCHAR(100) COMMENT '职位',
ADD COLUMN IF NOT EXISTS company_id INT COMMENT '所属企业',
ADD INDEX IF NOT EXISTS idx_company_id (company_id);
"

if [ $? -eq 0 ]; then
    echo "✓ users 表字段添加成功"
else
    echo "❌ users 表字段添加失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "迁移完成！"
echo "=========================================="
echo ""
echo "现在可以使用企业信息管理功能了："
echo "  - 用户侧：/dashboard/company（企业信息）"
echo "  - 用户侧：/dashboard/company/business（主营业务）"
echo "  - 管理员：/admin/companies（企业管理）"
echo ""
