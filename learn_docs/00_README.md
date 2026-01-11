# ShuaiTravelAgent 学习文档

本项目是一个智能旅游助手系统，采用现代化的微服务架构。本文档旨在帮助开发者按顺序理解系统架构和核心机制。

---

## 阅读指南

### 快速开始（5 分钟）

如果你想快速了解项目概览：

1. **[00_README.md](00_README.md)** - 你正在阅读本文档，获取项目整体印象

### 进阶学习（30 分钟）

建议按以下顺序阅读：

| 顺序 | 文档 | 重点内容 | 预计时间 |
|------|------|----------|----------|
| 1 | [01_系统架构.md](01_ARCHITECTURE.md) | 整体架构、技术选型、三层微服务结构 | 10 分钟 |
| 2 | [02_ReAct代理.md](02_REACT_AGENT.md) | ReAct 推理循环、状态机、工具系统 | 15 分钟 |
| 3 | [03_多模式对话.md](03_MULTI_MODE_CHAT.md) | Direct/ReAct/Plan 三种模式对比和实现 | 10 分钟 |

### 深入开发（按需阅读）

开发过程中可查阅：

| 顺序 | 文档 | 重点内容 | 用途 |
|------|------|----------|------|
| 4 | [04_接口文档.md](04_API.md) | HTTP API 接口定义 | API 集成 |
| 5 | [05_开发指南.md](05_DEVELOP.md) | 开发环境配置、本地调试 | 本地开发 |
| 6 | [06_部署指南.md](06_DEPLOY.md) | 部署配置、生产环境 | 项目部署 |
| 7 | [07_API文档配置.md](07_RapiDoc_ReDoc.md) | API 文档配置、SSE 测试面板 | 接口测试 |

---

## 推荐阅读路径

```
新手入门
    │
    ├── 1. 阅读 01_系统架构
    │      了解系统由哪些模块组成
    │      理解三层架构（Frontend → Web → Agent）
    │
    ├── 2. 阅读 02_ReAct代理
    │      理解 Agent 如何思考和执行
    │      了解工具如何被调用
    │
    └── 3. 阅读 03_多模式对话
           理解三种对话模式的区别
           知道何时使用哪种模式
                  │
                  ▼
            开始开发
                  │
                  ├── 需要 API 文档 → 04_接口文档
                  ├── 本地调试 → 05_开发指南
                  ├── 部署上线 → 06_部署指南
                  └── 接口测试 → 07_API文档配置
```

---

## 快速开始

### 环境准备
```bash
# 克隆项目
git clone https://github.com/your-repo/ShuaiTravelAgent.git
cd ShuaiTravelAgent

# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend && npm install
```

### 启动服务
```bash
# 终端1: 启动 Agent 服务 (gRPC, 端口 50051)
python run_agent.py

# 终端2: 启动 Web API 服务 (FastAPI, 端口 8000)
python run_api.py

# 终端3: 启动前端开发服务器
cd frontend && npm run dev
```

### 访问应用
- Web 应用: http://localhost:3000
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 技术栈概览

### 后端 (Python)
- **Agent**: 自研 ReAct Agent (无第三方框架依赖)
- **Web Framework**: FastAPI + SSE 流式响应
- **RPC**: gRPC (Agent 服务通信)
- **LLM**: 多协议支持 (OpenAI/Anthropic/Ollama 等)

### 前端 (TypeScript)
- **Framework**: Next.js 16 + React 19
- **UI Library**: Ant Design 6
- **State**: Zustand
- **HTTP**: Axios + SSE

---

## 核心特性速览

| 特性 | 说明 | 相关文档 |
|------|------|----------|
| ReAct 推理 | 思考 → 行动 → 观察 → 评估 循环 | [02_ReAct代理.md](02_REACT_AGENT.md) |
| 多模式对话 | Direct/ReAct/Plan 三种模式 | [03_多模式对话.md](03_MULTI_MODE_CHAT.md) |
| 动态风格 | 5 种回复风格自动切换 | 源码 style_config.py |
| SSE 流式 | Token 级别实时响应 | [04_接口文档.md](04_API.md) |
| 意图识别 | LLM + 规则双引擎 | 源码 intent_recognizer.py |

---

## 常见问题

**Q: 我应该先看哪个文档？**

A: 如果你是新加入的开发者，建议按顺序阅读 01 → 02 → 03。如果你只想了解某个具体功能，可以直接查阅对应文档。

**Q: 文档和代码不一致怎么办？**

A: 以代码为准。文档可能更新不及时，欢迎提 Issue 或 PR 反馈。

**Q: 如何贡献文档？**

A: 在 `learn_docs/` 目录下添加或修改文档，按数字前缀排序，更新本 README 的目录链接。
