#!/usr/bin/env python3
"""
调试数据库表创建过程
"""
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.core.config_manager import init_config, get_config
from app.database import engine, Base


def main():
    """主函数"""
    print("🔍 调试数据库表创建")
    print("=" * 50)
    
    try:
        # 1. 初始化配置
        print("📝 加载配置...")
        init_config()
        config = get_config()
        print(f"✅ 配置加载成功")
        print(f"📍 数据库URL: {config.database.url}")
        
        # 2. 导入所有模型
        print("\n📦 导入模型...")
        try:
            from app.models.request import HttpRequest
            print(f"✅ HttpRequest 模型导入成功: {HttpRequest.__tablename__}")
        except Exception as e:
            print(f"❌ HttpRequest 模型导入失败: {e}")
            
        try:
            from app.models.task import Task
            print(f"✅ Task 模型导入成功: {Task.__tablename__}")
        except Exception as e:
            print(f"❌ Task 模型导入失败: {e}")
            
        try:
            from app.models.execution import ExecutionRecord
            print(f"✅ ExecutionRecord 模型导入成功: {ExecutionRecord.__tablename__}")
        except Exception as e:
            print(f"❌ ExecutionRecord 模型导入失败: {e}")
        
        # 3. 检查Base.metadata中的表
        print(f"\n📋 Base.metadata 中的表:")
        for table_name, table in Base.metadata.tables.items():
            print(f"  - {table_name}: {table}")
        
        # 4. 手动创建表
        print(f"\n🔧 手动创建表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 表创建命令执行完成")
        
        # 5. 验证表是否存在
        print(f"\n🔍 验证表...")
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"📋 MySQL中的表: {tables}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 