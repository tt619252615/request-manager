#!/bin/bash

# RequestManager 前端启动脚本
echo "🚀 启动 RequestManager 前端开发服务器..."

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm 未安装，请先安装 pnpm"
    echo "安装命令: npm install -g pnpm"
    exit 1
fi

# 进入前端目录
cd "$(dirname "$0")"

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    pnpm install
fi

# 启动开发服务器
echo "✅ 启动开发服务器 (http://localhost:5173)"
echo "📋 测试页面: http://localhost:5173/test_frontend.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

pnpm run dev 