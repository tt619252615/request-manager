#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试setup.py打包配置
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def test_setup_py():
    """测试setup.py是否正确配置"""
    print("🧪 测试setup.py打包配置...")
    
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    
    try:
        # 测试1: 检查setup.py语法
        print("\n📋 1. 检查setup.py语法...")
        result = subprocess.run([
            sys.executable, "setup.py", "check"
        ], cwd=current_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ setup.py语法检查通过")
        else:
            print("❌ setup.py语法检查失败:")
            print(result.stderr)
            return False
        
        # 测试2: 构建源码分发包
        print("\n📦 2. 构建源码分发包...")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run([
                sys.executable, "setup.py", "sdist", "--dist-dir", tmpdir
            ], cwd=current_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 检查生成的文件
                dist_files = list(Path(tmpdir).glob("*.tar.gz"))
                if dist_files:
                    print(f"✅ 源码分发包构建成功: {dist_files[0].name}")
                    print(f"   大小: {dist_files[0].stat().st_size / 1024:.1f} KB")
                else:
                    print("❌ 没有找到生成的分发包")
                    return False
            else:
                print("❌ 源码分发包构建失败:")
                print(result.stderr)
                return False
        
        # 测试3: 构建wheel包
        print("\n🎡 3. 构建wheel包...")
        try:
            import wheel
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run([
                    sys.executable, "setup.py", "bdist_wheel", "--dist-dir", tmpdir
                ], cwd=current_dir, capture_output=True, text=True)
                
                if result.returncode == 0:
                    wheel_files = list(Path(tmpdir).glob("*.whl"))
                    if wheel_files:
                        print(f"✅ wheel包构建成功: {wheel_files[0].name}")
                        print(f"   大小: {wheel_files[0].stat().st_size / 1024:.1f} KB")
                    else:
                        print("❌ 没有找到生成的wheel包")
                        return False
                else:
                    print("❌ wheel包构建失败:")
                    print(result.stderr)
                    return False
        except ImportError:
            print("⚠️  wheel包未安装，跳过wheel构建测试")
        
        # 测试4: 检查包信息
        print("\n📊 4. 检查包信息...")
        result = subprocess.run([
            sys.executable, "setup.py", "--name", "--version", "--description"
        ], cwd=current_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                print(f"✅ 包名: {lines[0]}")
                print(f"   版本: {lines[1]}")
                print(f"   描述: {lines[2]}")
            else:
                print("❌ 包信息获取不完整")
                return False
        else:
            print("❌ 包信息获取失败:")
            print(result.stderr)
            return False
        
        # 测试5: 检查依赖
        print("\n📋 5. 检查依赖配置...")
        try:
            from setup import read_requirements
            requirements = read_requirements()
            print(f"✅ 依赖包数量: {len(requirements)}")
            for req in requirements[:5]:  # 只显示前5个
                print(f"   - {req}")
            if len(requirements) > 5:
                print(f"   ... 还有 {len(requirements) - 5} 个依赖")
        except Exception as e:
            print(f"❌ 依赖检查失败: {e}")
            return False
        
        print("\n🎉 所有测试通过！setup.py配置正确。")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

def print_usage_info():
    """打印使用说明"""
    print("\n📚 使用说明:")
    print("1. 构建源码包: python setup.py sdist")
    print("2. 构建wheel包: python setup.py bdist_wheel")
    print("3. 安装到本地: pip install -e .")
    print("4. 发布到PyPI: python setup.py sdist bdist_wheel && twine upload dist/*")
    print("5. 使用nix构建: nix-build nix/backend/")

if __name__ == "__main__":
    if test_setup_py():
        print_usage_info()
        sys.exit(0)
    else:
        print("\n❌ 测试失败，请检查setup.py配置")
        sys.exit(1) 