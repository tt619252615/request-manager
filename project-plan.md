# RequestManager - 定时HTTP请求管理系统

## 项目概述

基于demo.py的定时请求逻辑，构建一个功能完整的Web界面HTTP请求管理系统，支持导入、编辑、调度和监控HTTP请求。

## 技术架构

### 前端架构
- **框架**: React 18 + TypeScript + Vite
- **UI组件**: Ant Design 5.x
- **状态管理**: Zustand
- **路由**: React Router v6
- **HTTP客户端**: Axios
- **代码风格**: ESLint + Prettier

### 后端架构
- **框架**: FastAPI + Pydantic
- **ORM**: SQLAlchemy 2.0 + Alembic
- **任务调度**: Celery + Redis
- **数据库**: PostgreSQL
- **认证**: JWT
- **API文档**: OpenAPI/Swagger

## 项目目录结构

```
request-manager/
├── flake.nix                    # NixOS 开发环境配置
├── flake.lock
├── docker-compose.yml           # 本地开发环境
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── 
├── frontend/                    # 前端项目
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── types/               # 类型定义
│   │   │   ├── api.d.ts         # API 响应类型
│   │   │   ├── request.d.ts     # 请求相关类型
│   │   │   └── common.d.ts      # 通用类型
│   │   ├── api/                 # API 调用
│   │   │   ├── client.ts        # HTTP 客户端配置
│   │   │   ├── requests.ts      # 请求相关API
│   │   │   └── tasks.ts         # 任务相关API
│   │   ├── components/          # 组件
│   │   │   ├── common/          # 通用组件
│   │   │   ├── request/         # 请求管理组件
│   │   │   └── task/            # 任务管理组件
│   │   ├── pages/               # 页面
│   │   │   ├── Dashboard/
│   │   │   ├── Requests/
│   │   │   ├── Tasks/
│   │   │   └── Settings/
│   │   ├── stores/              # 状态管理
│   │   │   ├── useRequestStore.ts
│   │   │   ├── useTaskStore.ts
│   │   │   └── useAppStore.ts
│   │   ├── utils/               # 工具函数
│   │   │   ├── parser.ts        # Fiddler数据解析
│   │   │   ├── request.ts       # 请求处理工具
│   │   │   └── time.ts          # 时间处理工具
│   │   └── styles/              # 样式文件
│   │       ├── global.css
│   │       └── variables.css
│   └── public/
│
├── backend/                     # 后端项目
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── dependencies.py      # 依赖注入
│   │   ├── 
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── requests.py  # 请求管理API
│   │   │   │   ├── tasks.py     # 任务管理API
│   │   │   │   ├── execution.py # 执行管理API
│   │   │   │   └── monitoring.py# 监控API
│   │   │   └── deps.py          # API 依赖
│   │   ├── 
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # 基础模型
│   │   │   ├── request.py       # 请求模型
│   │   │   ├── task.py          # 任务模型
│   │   │   ├── execution.py     # 执行记录模型
│   │   │   └── user.py          # 用户模型
│   │   ├── 
│   │   ├── schemas/             # Pydantic 模式
│   │   │   ├── __init__.py
│   │   │   ├── response.py      # 统一响应模式
│   │   │   ├── request.py       # 请求相关模式
│   │   │   ├── task.py          # 任务相关模式
│   │   │   └── common.py        # 通用模式
│   │   ├── 
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── request_service.py   # 请求服务
│   │   │   ├── task_service.py      # 任务服务
│   │   │   ├── execution_service.py # 执行服务
│   │   │   ├── parser_service.py    # 解析服务
│   │   │   └── scheduler_service.py # 调度服务
│   │   ├── 
│   │   ├── core/                # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── security.py      # 安全相关
│   │   │   ├── scheduler.py     # 任务调度器
│   │   │   ├── executor.py      # 请求执行器
│   │   │   └── monitor.py       # 监控组件
│   │   ├── 
│   │   ├── utils/               # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── parser.py        # Fiddler解析器
│   │   │   ├── request_builder.py # 请求构建器
│   │   │   ├── time_utils.py    # 时间工具
│   │   │   └── proxy_manager.py # 代理管理
│   │   └── 
│   │   └── worker/              # Celery 任务
│   │       ├── __init__.py
│   │       ├── celery_app.py    # Celery 配置
│   │       ├── tasks.py         # 异步任务
│   │       └── scheduler.py     # 定时任务
│   │
│   └── alembic/                 # 数据库迁移
│       ├── versions/
│       ├── env.py
│       └── script.py.mako
│
└── docs/                        # 文档
    ├── api.md                   # API 文档
    ├── deployment.md            # 部署文档
    └── development.md           # 开发文档
```

## 核心功能模块

### 1. 请求管理模块
- **导入功能**: 支持Fiddler Raw格式、cURL命令、Postman导出
- **编辑功能**: 可视化HTTP请求编辑器
- **验证功能**: 请求格式验证和测试执行
- **存储功能**: 请求模板保存和分类管理

### 2. 任务调度模块
- **单次执行**: 立即执行HTTP请求
- **定时任务**: 基于时间的任务调度
- **循环重试**: 支持条件判断的循环执行
- **策略配置**: 重试策略、超时设置、代理配置

### 3. 执行引擎模块
- **多线程执行**: 并发请求处理
- **代理支持**: 动态代理IP管理
- **状态监控**: 实时执行状态跟踪
- **结果处理**: 响应解析和条件判断

### 4. 监控管理模块
- **实时监控**: 任务执行状态实时显示
- **历史记录**: 执行历史和统计分析
- **日志管理**: 详细的执行日志记录
- **告警通知**: 异常情况告警机制

## 数据模型设计

### 请求模型 (Request)
```python
class Request(Base):
    id: int
    name: str
    description: str
    method: str                  # GET, POST, etc.
    url: str
    headers: dict
    body: str
    params: dict
    created_at: datetime
    updated_at: datetime
```

### 任务模型 (Task)
```python
class Task(Base):
    id: int
    name: str
    request_id: int             # 关联请求
    task_type: str              # single, scheduled, retry
    schedule_config: dict       # 调度配置
    retry_config: dict          # 重试配置
    proxy_config: dict          # 代理配置
    status: str                 # pending, running, stopped, completed
    created_at: datetime
    updated_at: datetime
```

### 执行记录模型 (Execution)
```python
class Execution(Base):
    id: int
    task_id: int
    request_id: int
    status: str                 # success, failed, timeout
    response_code: int
    response_body: str
    response_time: float
    error_message: str
    executed_at: datetime
```

## API接口设计

### 统一响应格式
```typescript
interface BaseResponse<T = any> {
    code: number;
    data: T;
    message: string;
    timestamp: number;
}
```

### 主要接口

#### 请求管理接口
- `POST /api/v1/requests` - 创建请求
- `GET /api/v1/requests` - 获取请求列表
- `GET /api/v1/requests/{id}` - 获取请求详情
- `PUT /api/v1/requests/{id}` - 更新请求
- `DELETE /api/v1/requests/{id}` - 删除请求
- `POST /api/v1/requests/import` - 导入请求
- `POST /api/v1/requests/{id}/test` - 测试请求

#### 任务管理接口
- `POST /api/v1/tasks` - 创建任务
- `GET /api/v1/tasks` - 获取任务列表
- `GET /api/v1/tasks/{id}` - 获取任务详情
- `PUT /api/v1/tasks/{id}` - 更新任务
- `DELETE /api/v1/tasks/{id}` - 删除任务
- `POST /api/v1/tasks/{id}/start` - 启动任务
- `POST /api/v1/tasks/{id}/stop` - 停止任务

#### 执行管理接口
- `GET /api/v1/executions` - 获取执行记录
- `GET /api/v1/executions/{id}` - 获取执行详情
- `GET /api/v1/tasks/{id}/executions` - 获取任务执行记录

## 实现步骤

### 阶段1: 项目初始化 (Week 1)
1. 设置NixOS开发环境
2. 初始化前后端项目结构
3. 配置开发工具和代码规范
4. 设置数据库和Redis

### 阶段2: 后端核心功能 (Week 2-3)
1. 实现数据模型和数据库迁移
2. 构建基础API接口
3. 实现请求解析和存储功能
4. 开发执行引擎核心逻辑

### 阶段3: 前端基础界面 (Week 3-4)
1. 搭建前端项目架构
2. 实现请求管理界面
3. 开发任务配置界面
4. 集成API调用和状态管理

### 阶段4: 调度和执行 (Week 4-5)
1. 集成Celery任务调度
2. 实现定时任务功能
3. 开发循环重试逻辑
4. 添加代理管理功能

### 阶段5: 监控和优化 (Week 5-6)
1. 实现实时监控界面
2. 添加执行历史和统计
3. 完善错误处理和日志
4. 性能优化和测试

### 阶段6: 部署和文档 (Week 6)
1. Docker容器化部署
2. 编写用户文档
3. API文档完善
4. 最终测试和优化

## 关键技术点

### 1. Fiddler数据解析
基于demo.py中的请求处理逻辑，实现对Fiddler Raw格式的解析，提取HTTP方法、URL、头部、请求体等信息。

### 2. 定时调度实现
参考demo.py的wait_for_start_time逻辑，结合Celery实现精确的定时任务调度。

### 3. 并发执行控制
基于demo.py的多线程实现，在Web环境下通过异步任务实现高并发请求处理。

### 4. 状态管理和监控
实现任务状态的实时更新和监控，确保用户能够及时了解执行情况。

这个规划为您提供了完整的项目架构和实现路径。接下来我们可以开始第一阶段的实现，您希望从哪个部分开始？ 