#!/usr/bin/env python3
"""
RequestManager 一键安装和启动脚本
"""
import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    return True


def check_config():
    """检查配置文件"""
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ 配置文件 config.json 不存在")
        print("📝 请先复制 config.json 到 backend 目录")
        return False
    
    print("✅ 配置文件存在")
    return True


def test_mysql_connection():
    """测试MySQL连接"""
    print("🔗 测试MySQL连接...")
    try:
        import pymysql
        import json
        
        # 读取配置
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        db_config = config["database"]
        
        # 测试连接
        connection = pymysql.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["username"],
            password=db_config["password"],
            charset=db_config["charset"]
        )
        connection.close()
        print("✅ MySQL连接测试成功")
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("请检查配置文件中的数据库配置")
        return False


def start_server():
    """启动服务器"""
    print("🚀 启动RequestManager服务...")
    try:
        subprocess.run([
            sys.executable, "start.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("🎯 RequestManager 安装和启动向导")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 工作目录: {script_dir}")
    
    # 步骤1：检查配置文件
    if not check_config():
        sys.exit(1)
    
    # 步骤2：安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 步骤3：测试数据库连接
    if not test_mysql_connection():
        print("⚠️ 数据库连接失败，但仍可以启动服务")
        input("按回车键继续...")
    
    # 步骤4：启动服务
    start_server()


if __name__ == "__main__":
    main() 