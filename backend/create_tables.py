#!/usr/bin/env python3
"""
手动创建数据库表的脚本
"""
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.core.config_manager import init_config, get_config
from app.database import create_database, create_tables


def main():
    """主函数"""
    print("🗄️ RequestManager 数据库初始化")
    print("=" * 50)
    
    try:
        # 1. 初始化配置
        print("📝 加载配置...")
        init_config()
        config = get_config()
        
        print(f"✅ 配置加载成功")
        print(f"📍 数据库类型: {config.database.type}")
        print(f"📍 数据库地址: {config.database.host}:{config.database.port}")
        print(f"📍 数据库名称: {config.database.database}")
        
        # 2. 创建数据库（如果是MySQL）
        if config.database.type == "mysql":
            print("\n🔧 创建MySQL数据库...")
            create_database()
        
        # 3. 创建数据表
        print("\n🔧 创建数据表...")
        create_tables()
        print("✅ 数据表创建成功")
        
        # 4. 验证表是否创建成功
        print("\n🔍 验证数据表...")
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # 检查所有表
            if config.database.type == "mysql":
                result = conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result]
            elif config.database.type == "sqlite":
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
            else:
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                tables = [row[0] for row in result]
            
            print(f"📋 发现表: {tables}")
            
            expected_tables = ['http_requests', 'tasks', 'execution_records']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ 缺少表: {missing_tables}")
                return False
            else:
                print("✅ 所有必需的表都已创建")
                return True
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 数据库初始化完成！")
        print("现在可以启动服务了: python start.py")
    else:
        print("\n💥 数据库初始化失败！")
        sys.exit(1) 