"""
创建数字分身沙盘相关数据表
"""
import mysql.connector
from mysql.connector import Error

def create_simulation_tables():
    """创建模拟场景相关的数据表"""
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='jinchun123',
            database='energy_station'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("成功连接到MySQL数据库")
            
            # 创建 simulation_scenarios 表
            create_scenarios_table = """
            CREATE TABLE IF NOT EXISTS simulation_scenarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                company_id INT NOT NULL,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                time_range INT DEFAULT 3 COMMENT '模拟年限',
                config JSON NOT NULL COMMENT '场景配置',
                status VARCHAR(20) DEFAULT 'draft' COMMENT 'draft, running, completed, failed',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_company_id (company_id),
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模拟场景表';
            """
            
            cursor.execute(create_scenarios_table)
            print("✓ 创建 simulation_scenarios 表成功")
            
            # 创建 simulation_results 表
            create_results_table = """
            CREATE TABLE IF NOT EXISTS simulation_results (
                id INT PRIMARY KEY AUTO_INCREMENT,
                scenario_id INT NOT NULL,
                base_case JSON NOT NULL COMMENT '基准情况',
                simulated_case JSON NOT NULL COMMENT '模拟情况',
                impact JSON NOT NULL COMMENT '影响分析',
                time_series JSON NOT NULL COMMENT '时间序列数据',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES simulation_scenarios(id) ON DELETE CASCADE,
                INDEX idx_scenario_id (scenario_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模拟结果表';
            """
            
            cursor.execute(create_results_table)
            print("✓ 创建 simulation_results 表成功")
            
            # 提交更改
            connection.commit()
            print("\n✅ 所有表创建成功！")
            
            # 显示表结构
            print("\n" + "="*60)
            print("simulation_scenarios 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE simulation_scenarios")
            for row in cursor.fetchall():
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10} {row[3]:<10}")
            
            print("\n" + "="*60)
            print("simulation_results 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE simulation_results")
            for row in cursor.fetchall():
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10} {row[3]:<10}")
            
    except Error as e:
        print(f"❌ 错误: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == '__main__':
    print("开始创建数字分身沙盘数据表...")
    print("="*60)
    create_simulation_tables()
