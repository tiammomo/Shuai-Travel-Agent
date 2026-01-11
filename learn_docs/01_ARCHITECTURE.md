# 架构设计文档

## 1. 系统架构概览

本项目采用 **三层微服务架构**，通过 gRPC 实现模块间通信：

```
┌─────────────────────────────────────────────────────────────────────┐
│                          用户层 (User Layer)                         │
│                         浏览器 / 移动端                              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend Layer)                      │
│                      Next.js 15 (独立部署)                          │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │   状态管理   │  │   UI组件    │  │      API 服务               │ │
│  │   Zustand   │  │  Ant Design │  │      axios                  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Web层 (API Gateway)                           │
│                      FastAPI (端口 8000)                            │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │  REST API   │  │   SSE流     │  │     gRPC Client             │ │
│  │  /api/*     │  │  Streaming  │  │     ──────────────►         │ │
│  └─────────────┘  └─────────────┘  │     Agent Service           │ │
│                                    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ gRPC (端口 50051)
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent层 (AI Engine)                          │
│                     Python (独立服务)                               │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    ReActTravelAgent                           │  │
│  │                                                               │  │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │   │ Thought  │  │  Action  │  │Observation│  │Evaluation│    │  │
│  │   │ Engine   │──│  Handler │──│  Handler  │──│  Engine  │◄───┘  │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘       │  │
│  │                                                               │  │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │   │  Memory  │  │   LLM    │  │   Tool   │  │ Config   │    │  │
│  │   │ Manager  │──│  Client  │──│ Registry │──│ Manager  │    │  │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 模块职责

### 2.1 Agent 模块

**职责**: AI代理逻辑、业务处理、数据处理

**端口**: 50051 (gRPC)

**核心组件**:

| 组件 | 路径 | 职责 |
|------|------|------|
| ReActAgent | `src/core/react_agent.py` | 推理-行动循环核心引擎 |
| ReActTravelAgent | `src/core/travel_agent.py` | 旅游领域Agent封装 |
| LLMClient | `src/llm/client.py` | 多协议LLM调用 |
| MemoryManager | `src/memory/manager.py` | 对话记忆管理 |
| TravelData | `src/environment/travel_data.py` | 旅游数据环境 |
| ConfigManager | `src/config/config_manager.py` | 配置管理 |

**对外接口**:

```protobuf
service AgentService {
    rpc ProcessMessage (MessageRequest) returns (MessageResponse);
    rpc StreamMessage (MessageRequest) returns (stream StreamChunk);
    rpc HealthCheck (HealthRequest) returns (HealthResponse);
}
```

### 2.2 Web 模块

**职责**: API接口、路由管理、请求处理

**端口**: 8000 (HTTP)

**核心组件**:

| 组件 | 路径 | 职责 |
|------|------|------|
| FastAPI | `src/main.py` | 应用入口 |
| Chat Route | `src/routes/chat.py` | SSE聊天接口 |
| Session Route | `src/routes/session.py` | 会话管理 |
| SessionService | `src/services/session_service.py` | 会话业务逻辑 |
| SessionStorage | `src/storage/session_storage.py` | 会话持久化 |
| Container | `src/dependencies/container.py` | DI容器 |

**API端点**:

```
GET  /api/health              # 健康检查
POST /api/chat/stream         # SSE流式聊天
POST /api/session/new         # 创建会话
GET  /api/sessions            # 列表会话
DELETE /api/session/{id}      # 删除会话
PUT  /api/session/{id}/name   # 重命名
GET  /api/models              # 模型列表
GET  /api/cities              # 城市列表
```

### 2.3 Frontend 模块

**职责**: 用户界面、状态管理、API调用

**技术栈**:

- Next.js 15 (App Router)
- React 19
- TypeScript
- Zustand (状态管理)
- Ant Design 5 (UI组件)
- Vitest (测试)

**核心组件**:

| 组件 | 路径 | 职责 |
|------|------|------|
| ChatStore | `src/stores/chat/chatStore.ts` | 聊天状态 |
| SessionStore | `src/stores/session/sessionStore.ts` | 会话状态 |
| useSendMessage | `src/hooks/useChat/useSendMessage.ts` | 发送消息Hook |
| ChatArea | `src/components/chat/` | 聊天区域组件 |

---

## 3. 数据流

### 3.1 聊天请求流程

```
1. 用户输入消息
   │
   ▼
2. 前端: ChatStore.addMessage() 记录用户消息
   │
   ▼
3. 前端: 发起 SSE 请求到 /api/chat/stream
   │
   ▼
4. Web层: ChatService.generate_chat_stream()
   │
   ▼
5. Web层: gRPC调用 Agent层
   │
   ▼
6. Agent层: ReActTravelAgent.process()
   │        ├── 任务分析
   │        ├── 工具选择
   │        ├── 执行工具
   │        └── 生成回答
   │
   ▼
7. Agent层: 返回结果 (answer + reasoning)
   │
   ▼
8. Web层: SSE流式返回 reasoning + answer
   │
   ▼
9. 前端: 实时渲染思考过程和回答
   │
   ▼
10. 完成
```

### 3.2 会话管理流程

```
创建会话
  ┌─────────────────────┐
  │ POST /session/new   │──► SessionService.create_session()
  └─────────────────────┘                     │
                                              ▼
                                        SessionRepository.create()
                                              │
                                              ▼
                                        MemorySessionStorage.save()
                                              │
                                              ▼
                                        返回 session_id

列出会话
  ┌─────────────────────┐
  │ GET /sessions       │──► SessionRepository.list_all()
  └─────────────────────┘                     │
                                              ▼
                                        过滤活跃会话
                                              │
                                              ▼
                                        返回会话列表
```

---

## 4. 技术选型

### 4.1 后端技术

| 领域 | 技术 | 理由 |
|------|------|------|
| Web框架 | FastAPI | 高性能、自动文档、异步支持 |
| 通信协议 | gRPC | 高效、类型安全、多语言支持 |
| 序列化 | Pydantic | 数据验证、类型提示 |
| 测试 | pytest | 成熟、生态丰富 |
| 异步 | asyncio | Python原生异步支持 |

### 4.2 前端技术

| 领域 | 技术 | 理由 |
|------|------|------|
| 框架 | Next.js 15 | SSR/SSG支持、App Router |
| 状态管理 | Zustand | 简洁、TypeScript友好 |
| UI库 | Ant Design 5 | 组件丰富、设计统一 |
| HTTP客户端 | axios | 拦截器、SSE支持 |
| 测试 | Vitest | 快速、ESM兼容 |

### 4.3 LLM协议支持

```
OpenAI Compatible API
    │
    ├── OpenAI (gpt-4, gpt-4o, gpt-4o-mini)
    ├── Anthropic Claude (claude-3-sonnet, claude-3-opus)
    ├── Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
    └── Local Models (Ollama, LM Studio, etc.)
```

---

## 5. 目录结构详解

### 5.1 Agent 模块

```
agent/
├── proto/                    # gRPC协议定义
│   └── agent.proto           # 服务定义和消息类型
├── src/
│   ├── core/                 # 核心逻辑
│   │   ├── react_agent.py    # ReAct引擎 (2000+行)
│   │   └── travel_agent.py   # 旅游Agent封装
│   ├── llm/                  # LLM相关
│   │   ├── client.py         # LLM客户端 (多协议适配器)
│   │   └── factory.py        # 工厂类
│   ├── tools/                # 工具
│   │   ├── base.py           # 工具基类
│   │   └── travel_tools.py   # 旅游工具实现
│   ├── memory/               # 记忆
│   │   └── manager.py        # 记忆管理器
│   ├── environment/          # 环境
│   │   └── travel_data.py    # 旅游数据环境
│   ├── reasoner/             # 推理
│   │   ├── reasoner.py       # 推理引擎
│   │   └── intent.py         # 意图识别
│   ├── config/               # 配置
│   │   ├── config_manager.py # 配置管理
│   │   └── settings.py       # Pydantic Settings
│   └── server.py             # gRPC服务器
├── tests/                    # 测试
│   └── unit/
└── pyproject.toml           # 项目配置
```

### 5.2 Web 模块

```
web/
├── proto/                    # gRPC协议(从agent同步)
├── src/
│   ├── main.py              # FastAPI应用
│   ├── routes/              # API路由
│   │   ├── chat.py          # SSE聊天
│   │   ├── session.py       # 会话管理
│   │   ├── model.py         # 模型管理
│   │   ├── city.py          # 城市信息
│   │   └── health.py        # 健康检查
│   ├── services/            # 业务逻辑
│   │   ├── chat_service.py  # 聊天服务
│   │   └── session_service.py # 会话服务
│   ├── repositories/        # 数据访问
│   │   ├── session_repository.py       # 接口
│   │   └── session_repository_impl.py  # 实现
│   ├── storage/             # 存储
│   │   └── session_storage.py # 会话存储(内存/文件)
│   ├── grpc_client/         # gRPC客户端
│   ├── dependencies/        # DI
│   │   ├── container.py     # DI容器
│   │   └── providers.py     # Provider
│   └── schemas/             # Pydantic模型
├── tests/                   # 测试
│   └── unit/
└── pyproject.toml
```

### 5.3 Shared 模块

```
shared/
├── proto/                    # gRPC proto副本
├── types/                    # 共享类型
│   ├── message.py           # 消息类型
│   ├── session.py           # 会话类型
│   └── api.py               # API类型
└── constants.py             # 共享常量
```

---

## 6. 配置说明

配置文件位于 `config/llm_config.yaml`，实际使用时需要复制 `llm_config.yaml.example` 为 `llm_config.yaml` 并填入 API Key。

### 6.1 配置文件 (config/llm_config.yaml)

```yaml
# 默认使用的模型ID
default_model: gpt-4o-mini

# 模型配置列表
models:
  gpt-4o-mini:
    name: "GPT-4o Mini"
    provider: openai
    model: "gpt-4o-mini"
    api_base: "https://api.openai.com/v1"
    api_key: "sk-YOUR_OPENAI_API_KEY"
    temperature: 0.7
    max_tokens: 2000
    timeout: 30
    max_retries: 3

  claude-3-5-sonnet:
    name: "Claude 3.5 Sonnet"
    provider: anthropic
    model: "claude-sonnet-4-20250514"
    api_base: "https://api.anthropic.com/v1"
    api_key: "sk-ant-YOUR_ANTHROPIC_API_KEY"
    temperature: 0.7
    max_tokens: 2000
    timeout: 60
    max_retries: 3

  ollama-llama3:
    name: "Llama 3 (Ollama)"
    provider: openai-compatible
    model: "llama3"
    api_base: "http://localhost:11434/v1"
    api_key: ""
    temperature: 0.7
    max_tokens: 2000
    timeout: 120
    max_retries: 2

# Agent 配置
agent:
  name: "TravelAssistantAgent"
  max_steps: 10
  max_reasoning_depth: 5
  max_working_memory: 10
  max_long_term_memory: 50

# Web 服务配置
web:
  host: "0.0.0.0"
  port: 8000
  debug: true

# gRPC 服务配置
grpc:
  host: "0.0.0.0"
  port: 50051
```

### 6.2 前端环境变量

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### 6.3 支持的 Provider 类型

| Provider | 说明 | 示例 |
|----------|------|------|
| openai | OpenAI GPT 系列 | GPT-4o, GPT-4o-mini |
| anthropic | Anthropic Claude 系列 | Claude 3.5 Sonnet |
| google | Google Gemini 系列 | Gemini 1.5 Pro |
| ollama | Ollama 本地模型 | Llama 3, Qwen |
| openai-compatible | 兼容 OpenAI API 的自定义服务 | LM Studio, API聚合平台 |

---

## 7. 扩展指南

### 7.1 添加新工具

1. 在 `agent/src/tools/base.py` 定义工具基类
2. 在 `agent/src/tools/travel_tools.py` 实现工具
3. 在 `agent/src/core/travel_agent.py` 注册工具
4. 更新 `agent/proto/agent.proto`（如需要）

### 7.2 添加新API端点

1. 在 `web/src/routes/` 创建路由文件
2. 在 `web/src/services/` 创建服务类
3. 在 `web/src/main.py` 注册路由

### 7.3 添加新前端组件

1. 在 `frontend/src/components/` 创建组件
2. 在 `frontend/src/stores/` 更新状态管理
3. 在 `frontend/src/hooks/` 添加Hook（如需要）

---

## 8. 性能考虑

### 8.1 异步处理

- 所有IO操作使用 asyncio
- gRPC 使用异步流式响应
- 前端使用 Suspense 和 useTransition

### 8.2 缓存策略

- 会话数据：内存缓存 + 文件持久化
- 前端API响应：React Query / SWR

### 8.3 连接管理

- gRPC 连接池
- HTTP keep-alive
- 前端请求取消
