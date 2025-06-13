# RequestManager - HTTP请求管理与调度系统

> 一个基于FastAPI + React的HTTP请求管理与自动化调度平台，支持请求导入、任务调度、重试机制和代理配置等功能。

## 🎯 项目概述

RequestManager 是一个完整的 HTTP 请求管理和调度系统，旨在简化 HTTP 请求的管理、测试和自动化执行。

### ✨ 核心功能

- **📥 请求导入**: 支持 Fiddler Raw 格式和 cURL 命令导入
- **📋 请求管理**: 完整的 CRUD 操作，支持分类、标签管理
- **⏰ 任务调度**: 支持定时任务、周期性执行、多线程并发
- **🔄 代理轮换**: 智能代理管理和自动轮换
- **📊 执行记录**: 详细的执行历史和统计信息
- **🎛️ 实时监控**: 任务状态实时监控和控制

## 🏗️ 技术架构

### 后端技术栈
- **Framework**: FastAPI (高性能异步Web框架)
- **Database**: MySQL (支持PostgreSQL、SQLite)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Logging**: Loguru
- **Task Scheduling**: 内置多线程调度器

### 前端技术栈
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: TBD (计划使用 Ant Design 或 Material-UI)

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- MySQL 5.7+ / PostgreSQL 12+ / SQLite 3
- pnpm (推荐) 或 npm

### 配置数据库

项目使用 JSON 配置文件管理所有配置。首先需要配置数据库：

1. **编辑配置文件** `backend/config.json`:

```json
{
  "database": {
    "type": "mysql",
    "host": "192.168.31.186",
    "port": 3306,
    "username": "root",
    "password": "123456",
    "database": "request_manager",
    "charset": "utf8mb4"
  }
}
```

2. **支持的数据库类型**:
   - `mysql`: 使用 PyMySQL 驱动
   - `postgresql`: 使用 psycopg2 驱动  
   - `sqlite`: 文件数据库（开发测试用）

### 安装和启动

#### 方法一：使用 Nix 开发环境（推荐）

```bash
# 进入项目目录
cd request-manager

# 启动开发环境
nix develop .#default

# 启动后端服务
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端服务（新终端）
cd frontend && pnpm dev
```

#### 方法二：手动安装

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 启动后端服务
python start.py

# 安装前端依赖（新终端）
cd frontend
pnpm install
pnpm dev
```

#### 方法三：一键启动脚本

```bash
cd backend
python install_and_run.py
```

### 验证安装

1. **检查后端服务**:
   - API文档: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/health
   - 配置信息: http://localhost:8000/config

2. **检查前端服务**:
   - 前端界面: http://localhost:5173

## 📚 API 文档

### 配置管理 API

- `GET /config` - 获取当前配置信息
- `GET /health` - 健康检查和状态监控

### HTTP 请求管理 API

- `POST /api/requests` - 创建请求
- `GET /api/requests` - 获取请求列表
- `GET /api/requests/{id}` - 获取单个请求
- `PUT /api/requests/{id}` - 更新请求
- `DELETE /api/requests/{id}` - 删除请求
- `POST /api/requests/import/fiddler` - 导入 Fiddler Raw 格式
- `POST /api/requests/import/curl` - 导入 cURL 命令
- `POST /api/requests/{id}/test` - 测试请求

### 任务管理 API

- `POST /api/tasks` - 创建任务
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/{id}` - 获取单个任务
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `POST /api/tasks/{id}/start` - 启动任务
- `POST /api/tasks/{id}/stop` - 停止任务
- `POST /api/tasks/{id}/duplicate` - 复制任务
- `GET /api/tasks/{id}/statistics` - 获取任务统计

### 执行记录 API

- `GET /api/executions` - 获取执行记录
- `GET /api/executions/{id}` - 获取单个执行记录
- `GET /api/executions/statistics` - 获取执行统计

## 🔧 配置说明

### 完整配置文件示例 (`backend/config.json`)

```json
{
  "app": {
    "name": "RequestManager",
    "version": "0.1.0",
    "debug": true,
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "type": "mysql",
    "host": "192.168.31.186",
    "port": 3306,
    "username": "root",
    "password": "123456",
    "database": "request_manager",
    "charset": "utf8mb4",
    "pool_size": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": null
  },
  "security": {
    "secret_key": "your-secret-key-here-change-in-production",
    "algorithm": "HS256",
    "access_token_expire_minutes": 30
  },
  "cors": {
    "origins": [
      "http://localhost:5173",
      "http://localhost:5174"
    ]
  },
  "scheduler": {
    "default_timeout": 30,
    "max_retry_attempts": 10,
    "default_thread_count": 5,
    "check_interval": 10
  },
  "proxy": {
    "timeout": 30,
    "rotation_enabled": true,
    "fetch_interval": 30
  },
  "logging": {
    "level": "INFO",
    "file": null,
    "max_size": "10 MB",
    "retention": "1 week"
  }
}
```

### 配置项说明

- **app**: 应用基础配置
- **database**: 数据库连接配置
- **redis**: Redis缓存配置（可选）
- **security**: 安全认证配置
- **cors**: 跨域请求配置
- **scheduler**: 任务调度器配置
- **proxy**: 代理管理配置
- **logging**: 日志系统配置

## 📝 使用示例

### 导入 Fiddler 请求

```bash
curl -X POST "http://localhost:8000/api/requests/import/fiddler" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "POST https://api.example.com/endpoint HTTP/1.1\nHost: api.example.com\nContent-Type: application/json\n\n{\"key\": \"value\"}"
  }'
```

### 创建定时任务

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "定时任务示例",
    "request_id": 1,
    "schedule_type": "CRON",
    "schedule_config": {"cron_expression": "0 */10 * * * ?"},
    "execution_config": {
      "timeout": 30,
      "max_retry_attempts": 3,
      "thread_count": 2
    }
  }'
```

## 🚧 开发进度

### ✅ 已完成功能

#### Stage 1: 基础架构 (完成)
- [x] 数据库模型设计 (HttpRequest, Task, ExecutionRecord)
- [x] Pydantic 模式定义
- [x] FastAPI 应用设置
- [x] CORS 配置
- [x] 基础日志系统

#### Stage 2: 请求管理 (完成)
- [x] HTTP 请求解析器 (Fiddler Raw, cURL)
- [x] 请求管理服务
- [x] 请求执行器
- [x] 请求 CRUD API
- [x] 导入和测试 API

#### Stage 3: 任务调度 (完成)
- [x] 任务管理服务
- [x] 调度服务实现
- [x] 多线程执行支持
- [x] 代理管理和轮换
- [x] 任务控制 API
- [x] 执行记录和统计

#### Stage 4: 配置管理 (新增完成)
- [x] JSON 配置文件系统
- [x] 配置管理器实现
- [x] MySQL 数据库支持
- [x] 配置验证和初始化
- [x] 一键安装脚本

### 🔄 开发中

#### Stage 5: 前端界面
- [ ] React + TypeScript 基础框架
- [ ] 请求管理界面
- [ ] 任务管理界面
- [ ] 实时监控面板
- [ ] 统计报表界面

#### Stage 6: 高级功能
- [ ] 用户认证和权限管理
- [ ] API 限流和熔断
- [ ] 请求录制和回放
- [ ] 性能监控和告警
- [ ] 数据导入/导出

#### Stage 7: 部署优化
- [ ] Docker 容器化
- [ ] 性能优化
- [ ] 监控告警
- [ ] 备份恢复

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**注意**: 这是一个积极开发中的项目，API 可能会发生变化。建议在生产环境使用前仔细测试。

## 📖 项目简介

RequestManager 是一个基于demo.py重构的HTTP请求管理和调度系统，提供了完整的前后端解决方案，支持请求管理、任务调度、Fiddler数据导入等功能。

## 🏗️ 系统架构

### 前端技术栈
- **React 18** + **TypeScript** - 现代化UI框架
- **Vite** - 快速构建工具  
- **Ant Design** - 企业级UI组件库
- **React Router** - 客户端路由
- **Zustand** - 轻量级状态管理
- **Monaco Editor** - 代码编辑器
- **Axios** - HTTP客户端

### 后端技术栈
- **FastAPI** - 现代高性能Web框架
- **SQLAlchemy** - ORM数据库工具
- **Pydantic** - 数据验证和序列化
- **SQLite** - 轻量级数据库(开发环境)
- **Loguru** - 优雅的日志系统
- **Requests** - HTTP请求库

## 🚀 开发进度

### ✅ 第一阶段：基础架构 (已完成)
- [x] 数据库模型设计
  - [x] HttpRequest - HTTP请求模型
  - [x] Task - 任务模型  
  - [x] ExecutionRecord - 执行记录模型
  - [x] BaseModel - 基础模型类
- [x] Pydantic数据模式
  - [x] 请求相关schemas
  - [x] 任务相关schemas
  - [x] 执行记录schemas
  - [x] 统一响应格式
- [x] 应用基础配置
  - [x] FastAPI应用设置
  - [x] 数据库连接管理
  - [x] CORS配置
  - [x] 日志系统

### ✅ 第二阶段：核心API (已完成)
- [x] HTTP请求解析器
  - [x] Fiddler Raw格式解析
  - [x] cURL命令解析  
  - [x] 数据验证和错误处理
- [x] 请求管理服务
  - [x] CRUD操作
  - [x] 搜索和过滤
  - [x] 导入功能
- [x] 请求执行服务
  - [x] HTTP请求发送
  - [x] 响应处理
  - [x] 代理支持
- [x] API端点实现
  - [x] 请求管理API
  - [x] 导入API (Fiddler/cURL)
  - [x] 测试API
  - [x] 复制API

### ✅ 第三阶段：任务调度 (已完成)
- [x] 任务管理API
  - [x] 任务CRUD操作
  - [x] 任务状态管理
  - [x] 调度配置
- [x] 调度引擎
  - [x] 立即执行
  - [x] 定时执行
  - [x] 多线程支持
- [x] 重试机制
  - [x] 智能重试
  - [x] 条件判断
  - [x] 失败处理
- [x] 执行记录管理
  - [x] 执行历史记录
  - [x] 统计分析
  - [x] 状态跟踪

### 📋 第四阶段：监控与优化 (计划中)
- [ ] 高级调度功能
  - [ ] Cron表达式解析
  - [ ] 复杂时间调度
  - [ ] 任务依赖关系
- [ ] 性能优化
  - [ ] 连接池管理
  - [ ] 内存优化
  - [ ] 缓存机制
- [ ] 监控与告警
  - [ ] 实时监控面板
  - [ ] 性能指标统计
  - [ ] 异常告警

## 🏃‍♂️ 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- pnpm 或 npm

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings requests loguru python-multipart
```

#### 前端依赖
```bash
cd frontend
pnpm install
```

### 启动开发服务器

#### 启动后端服务 (端口8000)
```bash
cd backend
python start.py
```

#### 启动前端服务 (端口5173/5174)
```bash
cd frontend
pnpm dev
```

### 测试功能

#### 测试解析器
```bash
cd backend
python test_parser.py
```

#### 测试任务管理
```bash
cd backend
python test_task.py
```

## 📚 API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### HTTP请求管理
- `GET /api/requests/` - 获取请求列表
- `POST /api/requests/` - 创建新请求
- `GET /api/requests/{id}` - 获取请求详情
- `PUT /api/requests/{id}` - 更新请求
- `DELETE /api/requests/{id}` - 删除请求

#### 数据导入
- `POST /api/requests/import/fiddler` - 从Fiddler导入
- `POST /api/requests/import/curl` - 从cURL导入

#### 请求测试
- `POST /api/requests/{id}/test` - 测试请求
- `POST /api/requests/{id}/duplicate` - 复制请求

#### 任务管理
- `GET /api/tasks/` - 获取任务列表
- `POST /api/tasks/` - 创建新任务
- `GET /api/tasks/{id}` - 获取任务详情
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `POST /api/tasks/{id}/start` - 启动任务
- `POST /api/tasks/{id}/stop` - 停止任务
- `POST /api/tasks/{id}/duplicate` - 复制任务

#### 执行记录
- `GET /api/executions/` - 获取执行记录
- `GET /api/executions/{id}` - 获取执行记录详情
- `GET /api/executions/stats/summary` - 获取执行统计

## 🔧 配置说明

### 环境变量
创建 `.env` 文件配置：
```env
# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./request_manager.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 调度配置
DEFAULT_THREAD_COUNT=10
DEFAULT_TIMEOUT=30
```

## 📁 项目结构

```
request-manager/
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   └── stores/         # 状态管理
│   └── package.json
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # 数据模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── pyproject.toml
│   ├── start.py            # 启动脚本
│   ├── test_parser.py      # 解析器测试
│   └── test_task.py        # 任务管理测试
└── README.md
```

## 🧪 测试功能

### Fiddler数据导入测试
使用提供的美团抢购请求数据测试解析器：
```bash
cd backend
python test_parser.py
```

### 任务管理功能测试
测试完整的任务创建、执行、监控流程：
```bash
cd backend
python test_task.py
```

### API测试
使用测试脚本验证各个API端点：
```bash
# 创建请求
curl -X POST "http://localhost:8000/api/requests/" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试请求","method":"GET","url":"https://httpbin.org/get"}'

# 创建任务
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试任务","request_id":1,"task_type":"SINGLE"}'

# 启动任务
curl -X POST "http://localhost:8000/api/tasks/1/start"
```

## 🤝 开发规范

### 代码风格
- 后端: 遵循PEP 8规范
- 前端: 使用Prettier格式化
- 类型检查: TypeScript/Python类型提示

### 提交规范
- feat: 新功能
- fix: 修复bug  
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构代码

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 联系我们

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至 team@requestmanager.com

---

**RequestManager** - 让HTTP请求管理变得简单高效! 🚀

## 🔄 重发机制详解

系统实现了完整的重发机制，包含以下核心组件：

#### 1. 重试配置 (RetryConfig)
```python
{
    "max_attempts": 10,          # 最大重试次数
    "interval_seconds": 5,       # 重试间隔(秒)
    "success_condition": "response.status_code == 200",  # 成功条件
    "stop_condition": "response.status_code == 404"      # 停止条件
}
```

#### 2. 重发流程
1. **任务执行**: 调度器调度待执行任务
2. **HTTP请求**: 执行HTTP请求并获取响应
3. **条件判断**: 根据成功/失败条件判断结果
4. **重试决策**: 
   - 成功 → 标记完成，记录成功次数
   - 失败且未达到最大次数 → 等待间隔后重试
   - 失败且达到最大次数 → 标记失败
5. **状态更新**: 更新任务状态和统计信息

#### 3. 重试策略
- **固定间隔**: 每次重试间隔固定时间
- **指数退避**: 间隔时间逐次增加 (计划中)
- **条件停止**: 满足停止条件时立即结束

## 📋 项目概述

RequestManager是一个现代化的HTTP请求管理系统，旨在帮助开发者和测试人员高效地管理和调度HTTP请求任务。系统支持从多种格式导入请求，配置灵活的调度策略，并提供强大的重试和代理机制。

## 🚀 主要特性

### 💡 核心功能
- **请求管理**: 支持导入Fiddler Raw格式、cURL命令等
- **任务调度**: 支持单次执行、定时执行、Cron表达式调度
- **重试机制**: 智能重试策略，支持自定义成功/失败条件
- **代理支持**: 支持代理轮换和超时配置
- **实时监控**: 任务执行状态实时监控和统计

### 🔄 重发机制详解

系统实现了完整的重发机制，包含以下核心组件：

#### 1. 重试配置 (RetryConfig)
```python
{
    "max_attempts": 10,          # 最大重试次数
    "interval_seconds": 5,       # 重试间隔(秒)
    "success_condition": "response.status_code == 200",  # 成功条件
    "stop_condition": "response.status_code == 404"      # 停止条件
}
```

#### 2. 重发流程
1. **任务执行**: 调度器调度待执行任务
2. **HTTP请求**: 执行HTTP请求并获取响应
3. **条件判断**: 根据成功/失败条件判断结果
4. **重试决策**: 
   - 成功 → 标记完成，记录成功次数
   - 失败且未达到最大次数 → 等待间隔后重试
   - 失败且达到最大次数 → 标记失败
5. **状态更新**: 更新任务状态和统计信息

#### 3. 重试策略
- **固定间隔**: 每次重试间隔固定时间
- **指数退避**: 间隔时间逐次增加 (计划中)
- **条件停止**: 满足停止条件时立即结束

## 🏗️ 系统架构

### 后端架构 (FastAPI)
```
backend/
├── app/
│   ├── api/          # API路由
│   │   ├── requests.py   # 请求管理API
│   │   ├── tasks.py      # 任务管理API
│   │   └── executions.py # 执行记录API
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic模式
│   ├── services/     # 业务逻辑
│   │   ├── task_service.py      # 任务服务
│   │   ├── request_service.py   # 请求服务
│   │   ├── executor_service.py  # 执行服务
│   │   └── scheduler_service.py # 调度服务
│   ├── worker/       # 后台任务
│   └── utils/        # 工具类
```

### 前端架构 (React + TypeScript)
```
frontend/src/
├── api/              # API服务层
├── components/       # 通用组件
├── pages/            # 页面组件
│   ├── Dashboard/    # 仪表板
│   ├── Requests/     # 请求管理
│   ├── Tasks/        # 任务管理
│   └── Settings/     # 系统设置
├── types/            # 类型定义
└── utils/            # 工具函数
```

### 📡 API数据格式

#### 统一响应格式 (BaseResponse)
```json
{
  "code": 0,              // 状态码: 0成功, 非0失败
  "data": {...},          // 响应数据
  "message": "操作成功",   // 响应消息
  "timestamp": 1640995200 // 时间戳(毫秒)
}
```

#### 任务统计API (/api/tasks/stats/summary)
```json
{
  "code": 0,
  "data": {
    "total": 5,                    // 总任务数
    "running": 2,                  // 运行中
    "pending": 1,                  // 待执行
    "completed": 10,               // 已完成
    "failed": 2,                   // 已失败
    "stopped": 0,                  // 已停止
    "scheduler_running_count": 2   // 调度器运行任务数
  },
  "message": "获取任务统计成功"
}
```

#### 任务列表API (/api/tasks/)
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "美团秒杀任务",
      "request_id": 1,
      "status": "running",
      "execution_count": 5,
      "success_count": 3,
      "failure_count": 2,
      "next_execution_at": "2024-01-01T10:00:00Z",
      // ... 其他字段
    }
  ],
  "message": "获取任务列表成功"
}
```

### 🔧 前后端数据交互修复

#### 问题分析
1. **响应解析**: 前端API客户端需正确解析BaseResponse格式
2. **错误处理**: 优雅处理null值和错误响应
3. **类型安全**: 确保TypeScript类型定义与后端一致

#### 解决方案
1. **API客户端优化** (`frontend/src/api/client.ts`)
   - 增强响应拦截器
   - 添加null值检查
   - 提供原始响应访问方法

2. **页面组件增强**
   - 使用Promise.allSettled并行加载
   - 添加默认值处理
   - 改进错误提示

3. **类型定义对齐**
   - 确保前后端类型定义一致
   - 添加详细的接口文档

## 🛠️ 环境要求

### 后端
- Python 3.12+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- APScheduler 3.10+

### 前端
- Node.js 20+
- React 18+
- TypeScript 5+
- Ant Design 5+

## 📦 快速开始

### 1. 安装依赖

**后端**:
```bash
cd backend
pip install -r requirements.txt
```

**前端**:
```bash
cd frontend
pnpm install
```

### 2. 配置数据库

编辑 `backend/config.json`:
```json
{
  "database": {
    "type": "sqlite",
    "database": "request_manager.db"
  }
}
```

### 3. 初始化数据库
```bash
cd backend
alembic upgrade head
```

### 4. 启动服务

**后端服务**:
```bash
cd backend
python start.py
```

**前端服务**:
```bash
cd frontend
pnpm dev
```

### 5. 访问系统
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📝 使用指南

### 1. 导入请求
1. 从Fiddler复制Raw格式请求
2. 在"HTTP请求管理"页面点击"导入Fiddler请求"
3. 填写请求名称和描述
4. 点击确定完成导入

### 2. 创建任务
1. 在"任务管理"页面点击"新建任务"
2. 选择关联的HTTP请求
3. 配置调度策略:
   - **单次执行**: 立即执行一次
   - **定时执行**: 指定时间执行
   - **周期执行**: 使用Cron表达式
4. 配置重试策略
5. 配置代理设置(可选)
6. 保存并启动任务

### 3. 监控执行
1. 在仪表板查看整体统计
2. 在任务管理页面查看任务状态
3. 查看执行记录和错误日志

## 🔍 API文档

### 请求管理
- `GET /api/requests/` - 获取请求列表
- `POST /api/requests/` - 创建请求
- `POST /api/requests/import/fiddler` - 导入Fiddler请求
- `POST /api/requests/{id}/test` - 测试请求

### 任务管理
- `GET /api/tasks/` - 获取任务列表
- `POST /api/tasks/` - 创建任务
- `POST /api/tasks/{id}/start` - 启动任务
- `POST /api/tasks/{id}/stop` - 停止任务
- `GET /api/tasks/stats/summary` - 获取任务统计

### 执行记录
- `GET /api/executions/` - 获取执行记录
- `GET /api/executions/{id}` - 获取执行详情

## 🐛 故障排除

### 常见问题

1. **前端显示数据为空**
   - 检查后端服务是否启动
   - 查看浏览器控制台错误信息
   - 确认API响应格式正确

2. **任务不执行**
   - 检查调度器状态 (访问 /health)
   - 查看任务状态是否为pending
   - 检查next_execution_at时间设置

3. **数据库连接失败**
   - 检查config.json配置
   - 确认数据库文件权限
   - 运行数据库迁移命令

### 调试工具

1. **后端日志**: 查看终端输出的详细日志
2. **API文档**: 访问 http://localhost:8000/docs
3. **健康检查**: 访问 http://localhost:8000/health
4. **浏览器开发工具**: 查看网络请求和控制台错误

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🚧 开发计划

- [ ] 支持更多请求格式导入 (Postman, Insomnia)
- [ ] 添加请求模板功能
- [ ] 实现分布式任务调度
- [ ] 添加Webhook通知
- [ ] 支持请求链和依赖关系
- [ ] 添加性能监控和报警

## 📞 联系方式

如有问题或建议，请提交Issue或联系开发团队。

