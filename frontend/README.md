# RequestManager 前端

基于 React + Vite + TypeScript + Ant Design 的HTTP请求管理和任务调度前端界面。

## 功能特性

### 🚀 核心功能
- **HTTP请求管理** - 创建、编辑、测试和管理HTTP请求
- **任务调度系统** - 支持单次、定时和重试任务
- **Fiddler导入** - 一键导入Fiddler抓包数据
- **实时监控** - 任务状态、执行统计的实时显示
- **配置管理** - 调度配置、重试配置、代理配置

### 📊 页面功能

#### 1. Dashboard 仪表板
- 系统状态概览
- 任务执行统计
- 最近任务记录
- 快速操作入口

#### 2. 请求管理 (/requests)
- **列表展示**: 显示所有HTTP请求，支持搜索和过滤
- **测试功能**: 一键测试请求，查看详细响应结果
- **请求详情**: 完整的请求信息展示
- **Fiddler导入**: 支持粘贴Fiddler Raw数据自动解析
- **删除操作**: 确认后删除请求

#### 3. 任务调度 (/tasks)
- **任务列表**: 显示所有任务，支持状态和类型过滤
- **启动/停止**: 实时控制任务执行状态
- **任务编辑**: 完整的任务配置编辑功能
- **任务复制**: 快速复制现有任务配置
- **删除操作**: 确认后删除任务
- **统计信息**: 实时任务状态统计

#### 4. 任务配置
支持四大配置选项卡：

**基本配置**
- 任务名称和描述
- 关联HTTP请求
- 任务类型选择（单次/定时/重试）
- 线程数和时间差设置

**调度配置**
- 立即执行
- 指定时间执行
- Cron表达式定时

**重试配置**
- 最大重试次数
- 重试间隔时间
- 成功条件表达式
- 停止条件表达式
- 关键消息匹配

**代理配置**
- 代理开关
- 代理API地址
- 代理轮换设置
- 超时时间配置

#### 5. 执行记录 (/executions)
- 执行历史记录
- 详细的执行结果
- 错误信息追踪
- 性能数据分析

## 最新修复

### v2.1.0 功能完善
1. **请求测试功能修复**
   - 改善测试结果显示格式
   - 增加成功/失败状态标识
   - 完整显示响应头和响应体
   - 增强错误处理机制

2. **任务操作功能修复**
   - 修复启动/停止任务功能
   - 改善删除任务确认流程
   - 增加操作状态提示
   - 优化错误信息显示

3. **任务配置完善**
   - 修复编辑任务时的数据填充
   - 完善各配置选项卡切换
   - 增加关键消息字段
   - 优化表单验证机制

4. **界面体验优化**
   - 增加加载状态提示
   - 优化错误消息显示
   - 改善操作反馈机制
   - 增强调试信息输出

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: Ant Design 5.x
- **路由**: React Router 6
- **状态管理**: React Hooks
- **HTTP客户端**: Axios
- **代码规范**: ESLint + Prettier

## 快速开始

### 安装依赖
```bash
cd frontend
pnpm install
```

### 开发运行
```bash
# 启动开发服务器
pnpm dev

# 访问 http://localhost:5173
```

### 构建部署
```bash
# 构建生产版本
pnpm build

# 预览生产版本
pnpm preview
```

## 环境配置

### 开发环境
- 后端API地址: `http://localhost:8000`
- 前端开发服务器: `http://localhost:5173`

### 生产环境
根据实际部署情况修改 `src/api/client.ts` 中的 `BASE_URL` 配置。

## 项目结构

```
frontend/
├── src/
│   ├── api/           # API客户端
│   │   ├── client.ts     # 基础HTTP客户端
│   │   ├── requestApi.ts # 请求管理API
│   │   ├── taskApi.ts    # 任务调度API
│   │   └── executionApi.ts # 执行记录API
│   ├── components/    # 通用组件
│   ├── pages/         # 页面组件
│   │   ├── Dashboard/    # 仪表板
│   │   ├── Requests/     # 请求管理
│   │   ├── Tasks/        # 任务调度
│   │   └── Executions/   # 执行记录
│   ├── types/         # TypeScript类型定义
│   ├── utils/         # 工具函数
│   └── App.tsx        # 根组件
├── public/            # 静态资源
└── package.json       # 项目配置
```

## 使用指南

### 导入Fiddler请求
1. 在Fiddler中右键点击请求
2. 选择 "Copy" → "Copy RAW"
3. 在前端点击"导入Fiddler请求"
4. 粘贴RAW数据并填写名称
5. 点击确认导入

### 创建任务
1. 进入"任务调度"页面
2. 点击"新建任务"
3. 配置基本信息和关联请求
4. 根据需要配置调度、重试、代理选项
5. 保存并启动任务

### 查看执行结果
1. 在"执行记录"页面查看历史
2. 点击具体记录查看详情
3. 分析响应数据和性能指标

## 开发指南

### 添加新页面
1. 在 `src/pages/` 下创建页面目录
2. 实现页面组件
3. 在 `App.tsx` 中添加路由配置
4. 更新导航菜单

### 添加新API
1. 在 `src/api/` 下创建API文件
2. 定义API接口和类型
3. 在 `src/types/` 下添加对应类型定义
4. 在页面组件中调用API

## 常见问题

### Q: 前端无法连接后端？
A: 检查后端服务是否正常运行，确认API地址配置正确。

### Q: 测试请求没有响应？
A: 查看浏览器控制台错误信息，确认请求格式正确。

### Q: 任务无法启动？
A: 检查任务配置是否完整，确认关联的请求存在。

### Q: 页面数据不刷新？
A: 尝试手动刷新页面或清除浏览器缓存。

## 贡献指南

1. Fork项目仓库
2. 创建feature分支
3. 提交代码更改
4. 发起Pull Request

## 更新日志

### v2.1.0 (2025-06-11)
- 修复请求测试功能显示问题
- 完善任务操作功能
- 优化配置选项卡切换
- 增强错误处理机制

### v2.0.0 (2025-06-10)
- 完整的前端界面实现
- 支持所有后端功能
- 响应式设计适配

### v1.0.0 (2025-06-01)
- 初始版本发布
- 基础功能实现
