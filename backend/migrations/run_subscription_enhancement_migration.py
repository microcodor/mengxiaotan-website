#!/usr/bin/env python3
"""
订阅系统完善 - 数据库迁移脚本
功能: 扩展订单表字段，创建退款申请表
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始执行订阅系统完善数据库迁移...")
            
            # 1. 扩展 orders 表
            logger.info("步骤 1/3: 扩展 orders 表...")
            
            # 添加 payment_info 字段
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD COLUMN payment_info JSON COMMENT 'OCR提取的支付信息'
                """))
                logger.info("  ✓ 添加 payment_info 字段")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    logger.info("  - payment_info 字段已存在，跳过")
                else:
                    raise
            
            # 添加退款相关字段
            refund_fields = [
                ("refund_reason", "TEXT", "退款原因"),
                ("refund_status", "VARCHAR(20)", "退款状态: null, pending, approved, rejected"),
                ("refund_applied_at", "DATETIME", "退款申请时间"),
                ("refund_processed_at", "DATETIME", "退款处理时间"),
                ("refund_processed_by", "INT", "退款处理人ID")
            ]
            
            for field_name, field_type, comment in refund_fields:
                try:
                    db.session.execute(text(f"""
                        ALTER TABLE orders 
                        ADD COLUMN {field_name} {field_type} COMMENT '{comment}'
                    """))
                    logger.info(f"  ✓ 添加 {field_name} 字段")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        logger.info(f"  - {field_name} 字段已存在，跳过")
                    else:
                        raise
            
            # 添加索引
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD INDEX idx_refund_status (refund_status)
                """))
                logger.info("  ✓ 添加 idx_refund_status 索引")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    logger.info("  - idx_refund_status 索引已存在，跳过")
                else:
                    raise
            
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD INDEX idx_refund_applied_at (refund_applied_at)
                """))
                logger.info("  ✓ 添加 idx_refund_applied_at 索引")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    logger.info("  - idx_refund_applied_at 索引已存在，跳过")
                else:
                    raise
            
            # 添加外键约束
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD CONSTRAINT fk_orders_refund_processor 
                    FOREIGN KEY (refund_processed_by) REFERENCES users(id)
                """))
                logger.info("  ✓ 添加 fk_orders_refund_processor 外键")
            except Exception as e:
                if "Duplicate foreign key constraint name" in str(e) or "already exists" in str(e):
                    logger.info("  - fk_orders_refund_processor 外键已存在，跳过")
                else:
                    raise
            
            # 更新 payment_status 字段注释
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    MODIFY COLUMN payment_status VARCHAR(20) DEFAULT 'pending' 
                    COMMENT '支付状态: pending, paid, cancelled, refunded, refund_pending'
                """))
                logger.info("  ✓ 更新 payment_status 字段注释")
            except Exception as e:
                logger.warning(f"  ! 更新 payment_status 注释失败: {e}")
            
            db.session.commit()
            logger.info("步骤 1/3 完成: orders 表扩展成功")
            
            # 2. 创建 refund_applications 表
            logger.info("步骤 2/3: 创建 refund_applications 表...")
            
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS refund_applications (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        order_id INT NOT NULL COMMENT '订单ID',
                        user_id INT NOT NULL COMMENT '申请用户ID',
                        reason TEXT NOT NULL COMMENT '退款原因',
                        status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending, approved, rejected',
                        applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
                        processed_by INT COMMENT '处理人ID',
                        processed_at DATETIME COMMENT '处理时间',
                        reject_reason TEXT COMMENT '拒绝原因',
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        
                        FOREIGN KEY (order_id) REFERENCES orders(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (processed_by) REFERENCES users(id),
                        
                        INDEX idx_order_id (order_id),
                        INDEX idx_user_id (user_id),
                        INDEX idx_status (status),
                        INDEX idx_applied_at (applied_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='退款申请表'
                """))
                db.session.commit()
                logger.info("  ✓ refund_applications 表创建成功")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("  - refund_applications 表已存在，跳过")
                else:
                    raise
            
            logger.info("步骤 2/3 完成: refund_applications 表创建成功")
            
            # 3. 验证迁移结果
            logger.info("步骤 3/3: 验证迁移结果...")
            
            # 检查 orders 表的新字段
            result = db.session.execute(text("DESCRIBE orders"))
            orders_columns = [row[0] for row in result]
            
            required_order_fields = [
                'payment_info', 'refund_reason', 'refund_status',
                'refund_applied_at', 'refund_processed_at', 'refund_processed_by'
            ]
            
            for field in required_order_fields:
                if field in orders_columns:
                    logger.info(f"  ✓ orders.{field} 字段存在")
                else:
                    logger.error(f"  ✗ orders.{field} 字段不存在")
                    raise Exception(f"迁移失败: orders.{field} 字段未创建")
            
            # 检查 refund_applications 表
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'refund_applications'
            """))
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                logger.info("  ✓ refund_applications 表存在")
            else:
                logger.error("  ✗ refund_applications 表不存在")
                raise Exception("迁移失败: refund_applications 表未创建")
            
            logger.info("步骤 3/3 完成: 验证成功")
            
            logger.info("=" * 60)
            logger.info("✓ 数据库迁移成功完成!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"迁移失败: {e}")
            db.session.rollback()
            raise


def rollback_migration():
    """回滚数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始回滚订阅系统完善数据库迁移...")
            
            # 删除 refund_applications 表
            logger.info("删除 refund_applications 表...")
            db.session.execute(text("DROP TABLE IF EXISTS refund_applications"))
            logger.info("  ✓ refund_applications 表已删除")
            
            # 删除 orders 表的外键约束
            try:
                db.session.execute(text("""
                    ALTER TABLE orders 
                    DROP FOREIGN KEY fk_orders_refund_processor
                """))
                logger.info("  ✓ 删除 fk_orders_refund_processor 外键")
            except Exception as e:
                logger.info(f"  - 外键不存在或已删除: {e}")
            
            # 删除索引
            try:
                db.session.execute(text("ALTER TABLE orders DROP INDEX idx_refund_status"))
                logger.info("  ✓ 删除 idx_refund_status 索引")
            except Exception as e:
                logger.info(f"  - 索引不存在或已删除: {e}")
            
            try:
                db.session.execute(text("ALTER TABLE orders DROP INDEX idx_refund_applied_at"))
                logger.info("  ✓ 删除 idx_refund_applied_at 索引")
            except Exception as e:
                logger.info(f"  - 索引不存在或已删除: {e}")
            
            # 删除 orders 表的新字段
            refund_fields = [
                'payment_info', 'refund_reason', 'refund_status',
                'refund_applied_at', 'refund_processed_at', 'refund_processed_by'
            ]
            
            for field in refund_fields:
                try:
                    db.session.execute(text(f"ALTER TABLE orders DROP COLUMN {field}"))
                    logger.info(f"  ✓ 删除 orders.{field} 字段")
                except Exception as e:
                    logger.info(f"  - 字段不存在或已删除: {e}")
            
            db.session.commit()
            logger.info("✓ 回滚成功完成!")
            
            return True
            
        except Exception as e:
            logger.error(f"回滚失败: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='订阅系统完善数据库迁移脚本')
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='回滚迁移'
    )
    
    args = parser.parse_args()
    
    try:
        if args.rollback:
            rollback_migration()
        else:
            run_migration()
    except Exception as e:
        logger.error(f"执行失败: {e}")
        sys.exit(1)
