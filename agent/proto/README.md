# Proto 文件使用指南

## 概述

本目录包含 gRPC 服务定义文件和相关说明：

| 文件 | 说明 | 是否可编辑 |
|------|------|-----------|
| `agent.proto` | 服务定义源文件（ protobuf 语法） | ✅ 可编辑 |
| `agent_pb2.py` | 自动生成的消息类型代码 | ❌ 自动生成 |
| `agent_pb2_grpc.py` | 自动生成的 gRPC 通信代码 | ❌ 自动生成 |
| `README.md` | 本使用说明文档 | ✅ 可编辑 |

## 核心概念

### 三个文件的关系

```
                    agent.proto (源定义)
                           │
                           ▼ protoc 编译
                  ┌────────────────┐
                  │  agent_pb2.py  │  消息类型
                  │  (数据结构)    │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │agent_pb2_grpc.py│ gRPC 通信
                  └────────────────┘
```

### agent_pb2.py - 消息类型

**作用**：提供 Protocol Buffer 消息类的 Python 实现

**包含的类**：
- `MessageRequest` - 客户端发送的请求
- `MessageResponse` - 服务端返回的响应
- `ReasoningInfo` - 推理过程信息
- `HistoryStep` - 执行历史步骤
- `ThoughtInfo` - 思考信息
- `ActionInfo` - 行动/工具调用信息
- `EvaluationInfo` - 行动评估信息
- `StreamChunk` - 流式传输的数据块
- `HealthRequest` - 健康检查请求
- `HealthResponse` - 健康检查响应

**消息类的常用方法**：
```python
# 创建消息
request = MessageRequest(session_id="123", user_input="北京三日游")

# 序列化（对象 → 二进制，用于网络传输）
data = request.SerializeToString()

# 反序列化（二进制 → 对象，用于接收数据）
response = MessageResponse.FromString(data)

# 字段访问
print(request.session_id)
print(response.answer)
```

### agent_pb2_grpc.py - 通信代码

**作用**：提供 gRPC 客户端存根和服务端基类

**包含的类**：
- `AgentServiceStub` - 客户端存根，用于调用 gRPC 服务
- `AgentServiceServicer` - 服务端基类，需子类实现具体逻辑
- `AgentService` - 实验性 API（较少使用）
- `add_AgentServiceServicer_to_server()` - 将服务实现注册到 gRPC 服务器

## 快速上手

### 1. 服务端（Agent）实现

**文件**: `agent/src/server.py`

```python
from proto import agent_pb2, agent_pb2_grpc

class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    """
    Agent 服务处理器

    继承自 agent_pb2_grpc.AgentServiceServicer，
    实现三个 RPC 方法：ProcessMessage、StreamMessage、HealthCheck
    """

    def ProcessMessage(self, request, context):
        """
        同步处理用户消息

        Args:
            request: agent_pb2.MessageRequest
                     - request.session_id  会话ID
                     - request.user_input  用户输入
                     - request.model_id    模型ID
                     - request.stream      是否流式

            context: grpc.ServicerContext  gRPC 上下文

        Returns:
            agent_pb2.MessageResponse
        """
        # 1. 从请求中获取数据
        session_id = request.session_id
        user_input = request.user_input

        # 2. 处理业务逻辑
        result = process_travel_request(user_input)

        # 3. 创建响应消息
        response = agent_pb2.MessageResponse(
            success=True,
            answer=result["answer"]
        )
        return response

    def StreamMessage(self, request, context):
        """
        流式处理用户消息

        使用 yield 返回多个 StreamChunk：

        chunk_type 取值:
            - "thinking_start": 思考开始
            - "thinking_chunk": 思考内容
            - "thinking_end":   思考结束
            - "answer_start":   答案开始
            - "answer":         答案内容
            - "done":           完成
            - "error":          错误
        """
        # 发送思考开始
        yield agent_pb2.StreamChunk(chunk_type="thinking_start", content="")

        # 发送思考内容
        yield agent_pb2.StreamChunk(
            chunk_type="thinking_chunk",
            content="分析用户需求..."
        )

        # 发送答案开始
        yield agent_pb2.StreamChunk(chunk_type="answer_start", content="")

        # 发送答案（逐块）
        for chunk in answer_chunks:
            yield agent_pb2.StreamChunk(
                chunk_type="answer",
                content=chunk,
                is_last=False
            )

        # 发送完成信号
        yield agent_pb2.StreamChunk(chunk_type="done", content="", is_last=True)

    def HealthCheck(self, request, context):
        """健康检查"""
        return agent_pb2.HealthResponse(
            healthy=True,
            version="1.0.0",
            status="running"
        )

# 启动服务
def serve():
    from concurrent import futures
    import grpc

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 注册服务到服务器
    agent_pb2_grpc.add_AgentServiceServicer_to_server(
        AgentServicer(),  # 服务实现实例
        server            # gRPC 服务器
    )

    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

### 2. 客户端（Web）调用

**文件**: `web/src/routes/chat.py`

```python
from proto import agent_pb2, agent_pb2_grpc
import grpc

def call_grpc_service():
    """调用 gRPC 服务"""

    # 1. 创建通信通道
    channel = grpc.insecure_channel('localhost:50051')

    # 2. 创建客户端存根（Stub）
    stub = agent_pb2_grpc.AgentServiceStub(channel)

    # 3. 构造请求消息
    request = agent_pb2.MessageRequest(
        session_id="session-123",
        user_input="北京三日游怎么安排？",
        model_id="gpt-4o-mini",
        stream=True  # 使用流式
    )

    # 4. 同步调用
    # response = stub.ProcessMessage(request)
    # print(response.answer)

    # 5. 流式调用
    for chunk in stub.StreamMessage(request):
        # chunk 是 agent_pb2.StreamChunk 类型
        print(f"type={chunk.chunk_type}, content={chunk.content}, last={chunk.is_last}")

    # 6. 健康检查
    health_request = agent_pb2.HealthRequest()
    health_response = stub.HealthCheck(health_request)
    print(f"健康状态: {health_response.healthy}")
```

## 消息类型速查

### 请求消息

```python
# MessageRequest - 消息请求
request = agent_pb2.MessageRequest(
    session_id="abc123",      # 会话ID
    user_input="北京三日游",   # 用户输入
    model_id="gpt-4o-mini",   # 模型ID
    stream=True               # 是否流式
)

# HealthRequest - 健康检查请求（空消息）
request = agent_pb2.HealthRequest()
```

### 响应消息

```python
# MessageResponse - 消息响应
response = agent_pb2.MessageResponse(
    success=True,
    answer="您的北京三日游安排...",
    reasoning=agent_pb2.ReasoningInfo(
        text="分析用户需求...",
        total_steps=5,
        tools_used=["search_city", "get_attractions"]
    ),
    error="",
    history=[...]
)

# HealthResponse - 健康检查响应
response = agent_pb2.HealthResponse(
    healthy=True,
    version="1.0.0",
    status="running"
)

# StreamChunk - 流式数据块
chunk = agent_pb2.StreamChunk(
    chunk_type="answer",
    content="您",
    is_last=False
)
```

## gRPC 调用模式图解

### 同步调用 (ProcessMessage)

```
时间 ──────────────────────────────────────────────────────>

客户端                                    服务端
  │                                        │
  │  ------- MessageRequest ------>        │
  │      (user_input="北京三日游")         │
  │                                        │ 处理中...
  │                                        │
  |  <------- MessageResponse ------       |
  |      (answer="行程安排...")            |
  |                                        |
```

### 流式调用 (StreamMessage)

```
时间 ──────────────────────────────────────────────────────>

客户端                                    服务端
  │                                        │
  │  ------- MessageRequest ------>        │
  │      (user_input="北京三日游")         │
  │                                        │
  │  <--- StreamChunk(chunk_type)    |     实时返回
  │      (content="分析中...")        |     |
  │                                        |
  │  <--- StreamChunk(chunk_type)    |     |
  │      (content="推荐景点...")      |     |
  │                                        |
  │  <--- StreamChunk(chunk_type=done)     │
  │                                        │
```

## 在项目中的实际使用

### 服务端（agent/src/server.py）

```python
# 导入
from proto import agent_pb2, agent_pb2_grpc

# 创建流式数据块
yield agent_pb2.StreamChunk(
    chunk_type="thinking_chunk",
    content=thinking_text,
    is_last=False
)

# 创建响应
return agent_pb2.MessageResponse(
    success=True,
    answer=answer
)
```

### 客户端（web/src/routes/chat.py）

```python
# 导入
from proto import agent_pb2, agent_pb2_grpc

# 初始化 gRPC 存根
stub = agent_pb2_grpc.AgentServiceStub(channel)

# 构建请求
request = agent_pb2.MessageRequest(
    session_id=session_id,
    user_input=message,
    model_id='',
    stream=True
)

# 遍历流式响应
for chunk in stub.StreamMessage(request):
    # 处理每个 chunk
    process_chunk(chunk)
```

## 常见问题

### Q: 为什么要用 gRPC 而不是 HTTP REST？

| 特性 | gRPC | REST |
|------|------|------|
| 协议 | HTTP/2 | HTTP/1.1 |
| 传输格式 | Protocol Buffers（高效） | JSON（文本） |
| 流式支持 | 原生支持 | 需用 SSE |
| 类型安全 | 编译时检查 | 运行时检查 |
| 适用场景 | 服务间通信 | 浏览器-服务端 |

### Q: 如何调试 gRPC 调用？

```python
# 1. 启用详细日志
import grpc
grpc.enable_logging()

# 2. 使用 grpcurl 工具测试
# grpcurl -plaintext localhost:50051 list
# grpcurl -plaintext localhost:50051 agent.AgentService.HealthCheck

# 3. 打印请求/响应
print("Request:", request)
print("Response:", response)
```

### Q: 修改 proto 文件后怎么办？

```bash
# 1. 重新编译
cd agent/proto
python -m grpc_tools.protoc \
    -I. \
    --python_out=../src \
    --grpc_python_out=../src \
    agent.proto

# 2. 重启服务
# 3. 测试验证
```

## 如何生成 proto 文件

### 前置条件

需要安装 `grpcio` 和 `grpcio-tools`：

```bash
pip install grpcio grpcio-tools
```

### 编译命令

修改 `agent.proto` 后，需要重新编译生成 Python 代码：

**编译到 `agent/proto/` 目录**（推荐）：
```bash
cd d:\projects\shuai\ShuaiTravelAgent
python -m grpc_tools.protoc -I./agent/proto --python_out=./agent/proto --grpc_python_out=./agent/proto agent/proto/*.proto
```

**同时编译到 `agent/src/` 目录**（供服务端使用）：
```bash
cd d:\projects\shuai\ShuaiTravelAgent
python -m grpc_tools.protoc -I./agent/proto --python_out=./agent/src --grpc_python_out=./agent/src agent/proto/*.proto
```

**同时编译到 `web/src/` 目录**（供客户端使用）：
```bash
cd d:\projects\shuai\ShuaiTravelAgent
python -m grpc_tools.protoc -I./agent/proto --python_out=./web/src --grpc_python_out=./web/src agent/proto/*.proto
```

**一键编译到所有位置**：
```bash
cd d:\projects\shuai\ShuaiTravelAgent
python -m grpc_tools.protoc -I./agent/proto --python_out=./agent/proto --grpc_python_out=./agent/proto agent/proto/*.proto
python -m grpc_tools.protoc -I./agent/proto --python_out=./agent/src --grpc_python_out=./agent/src agent/proto/*.proto
python -m grpc_tools.protoc -I./agent/proto --python_out=./web/src --grpc_python_out=./web/src agent/proto/*.proto
```

### 修复导入问题

编译生成的 `*_grpc.py` 文件使用绝对导入，修改 `agent.proto` 后需要修复导入：

**问题**：生成的文件包含 `import agent_pb2 as agent__pb2`，但在不同目录下无法找到模块

**解决方案**：修改 `agent_pb2_grpc.py` 开头：

```python
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc
import warnings
try:
    # Python 3.11+ relative import
    from . import agent_pb2 as agent__pb2
except ImportError:
    # Fallback for older Python versions
    import agent_pb2 as agent__pb2
```

### 编译参数说明

| 参数 | 说明 |
|------|------|
| `-I./agent/proto` | proto 文件搜索路径（proto 文件所在目录） |
| `--python_out=./agent/proto` | 生成消息类型代码的输出目录 |
| `--grpc_python_out=./agent/proto` | 生成 gRPC 通信代码的输出目录 |
| `agent/proto/*.proto` | 要编译的 proto 文件 |

### 文件路径结构

```
agent/
├── proto/
│   ├── agent.proto           ← 服务定义源文件（可编辑）
│   ├── agent_pb2.py          ← 自动生成（消息类型）
│   ├── agent_pb2_grpc.py     ← 自动生成（通信代码）
│   ├── __init__.py           ← 使 proto 成为 Python 包
│   └── README.md             ← 本说明文档
│
└── src/
    └── server.py             ← 服务端实现（使用 proto）
```

## 相关文档

- [agent.proto](agent.proto) - 服务接口原始定义
- [agent/src/server.py](../src/server.py) - 服务端完整实现
- [web/src/routes/chat.py](../../web/src/routes/chat.py) - 客户端调用示例
