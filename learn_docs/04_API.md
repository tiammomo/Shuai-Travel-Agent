# API 参考文档

本文档描述了 Web API 的所有接口，包括请求格式、响应格式和示例。

---

## 基础信息

### 基础URL

```
开发环境: http://localhost:48081
生产环境: https://api.your-domain.com
```

### 认证

当前版本不需要认证，后续可添加 API Key 认证。

### 错误响应

所有错误返回统一格式：

```json
{
  "success": false,
  "error": "错误描述",
  "detail": "详细错误信息（可选）",
  "code": "ERROR_CODE"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器内部错误 |

---

## 健康检查

### GET /api/health

检查服务健康状态。

**响应示例 (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "agent": "healthy"
  }
}
```

### GET /api/live

存活检查（用于 k8s liveness probe）。

**响应示例 (200 OK):**

```json
{
  "status": "alive"
}
```

### GET /api/ready

就绪检查（用于 k8s readiness probe）。

**响应示例 (200 OK):**

```json
{
  "status": "ready"
}
```

---

## 聊天接口

### POST /api/chat/stream

SSE 流式聊天接口，返回思考过程和回答。

**请求头:**

```
Content-Type: application/json
Accept: text/event-stream
```

**请求体:**

```json
{
  "message": "推荐一些适合春天旅游的城市",
  "session_id": null
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息 |
| session_id | string | 否 | 会话ID，为空则创建新会话 |

**SSE 事件流:**

```
data: {"type": "session_id", "session_id": "550e8400-e29b-41d4-a716-446655440000"}

data: {"type": "reasoning_start"}

data: {"type": "reasoning_chunk", "content": "分析用户请求..."}

data: {"type": "reasoning_end"}

data: {"type": "answer_start"}

data: {"type": "chunk", "content": "您好！"}

data: {"type": "chunk", "content": "我推荐..."}

data: {"type": "done"}
```

**事件类型说明:**

| 事件类型 | 说明 |
|----------|------|
| session_id | 会话ID，用于后续请求 |
| reasoning_start | 思考过程开始 |
| reasoning_chunk | 思考过程内容块 |
| reasoning_end | 思考过程结束 |
| answer_start | 回答开始 |
| chunk | 回答内容块 |
| done | 流结束标记 |

**curl 示例:**

```bash
curl -X POST http://localhost:48081/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "推荐适合春天旅游的城市"}'
```

---

## 会话管理

### POST /api/session/new

创建新会话。

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 会话名称，默认自动生成 |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "新会话"
}
```

**curl 示例:**

```bash
curl -X POST http://localhost:48081/api/session/new \
  -H "Content-Type: application/json" \
  -d '{"name": "我的旅行计划"}'
```

---

### GET /api/sessions

获取会话列表。

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_empty | boolean | 否 | 是否包含空会话，默认 false |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "北京旅游计划",
      "message_count": 5,
      "model_id": "gpt-4o-mini",
      "created_at": "2024-01-15T10:30:00",
      "last_active": "2024-01-15T11:45:00"
    }
  ],
  "total": 1
}
```

**curl 示例:**

```bash
# 获取非空会话
curl http://localhost:48081/api/sessions

# 获取所有会话（包括空会话）
curl "http://localhost:48081/api/sessions?include_empty=true"
```

---

### GET /api/session/{session_id}

获取会话详情。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "session": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "北京旅游计划",
    "message_count": 5,
    "model_id": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "推荐北京景点",
        "timestamp": "10:30:00"
      },
      {
        "role": "assistant",
        "content": "北京有很多著名景点...",
        "timestamp": "10:30:05"
      }
    ],
    "created_at": "2024-01-15T10:30:00",
    "last_active": "2024-01-15T11:45:00"
  }
}
```

**错误响应 (404 Not Found):**

```json
{
  "success": false,
  "error": "会话不存在"
}
```

---

### PUT /api/session/{session_id}/name

更新会话名称。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 新会话名称 |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "name": "新的会话名称"
}
```

**curl 示例:**

```bash
curl -X PUT http://localhost:48081/api/session/550e8400-e29b-41d4-a716-446655440000/name \
  -H "Content-Type: application/json" \
  -d '{"name": "杭州旅游"}'
```

---

### DELETE /api/session/{session_id}

删除会话。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**响应示例 (200 OK):**

```json
{
  "success": true
}
```

**curl 示例:**

```bash
curl -X DELETE http://localhost:48081/api/session/550e8400-e29b-41d4-a716-446655440000
```

---

### POST /api/clear/{session_id}

清空会话消息。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**响应示例 (200 OK):**

```json
{
  "success": true
}
```

---

### GET /api/session/{session_id}/model

获取会话使用的模型。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "model_id": "gpt-4o-mini"
}
```

---

### PUT /api/session/{session_id}/model

设置会话使用的模型。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话ID |

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_id | string | 是 | 模型ID |

**响应示例 (200 OK):**

```json
{
  "success": true,
  "model_id": "gpt-4o"
}
```

---

## 模型管理

### GET /api/models

获取可用模型列表。

**响应示例 (200 OK):**

```json
{
  "models": [
    {
      "model_id": "gpt-4o-mini",
      "name": "GPT-4o Mini",
      "provider": "openai",
      "description": "高效快速的小型模型"
    },
    {
      "model_id": "gpt-4o",
      "name": "GPT-4o",
      "provider": "openai",
      "description": "强大的多模态模型"
    },
    {
      "model_id": "claude-3-sonnet",
      "name": "Claude 3 Sonnet",
      "provider": "anthropic",
      "description": "平衡性能与速度"
    }
  ]
}
```

---

### GET /api/models/{model_id}

获取模型详情。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| model_id | string | 模型ID |

**响应示例 (200 OK):**

```json
{
  "model_id": "gpt-4o-mini",
  "name": "GPT-4o Mini",
  "provider": "openai",
  "description": "高效快速的小型模型"
}
```

**错误响应 (404 Not Found):**

```json
{
  "error": "Model not found"
}
```

---

## 城市信息

### GET /api/cities

获取城市列表。

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | 地区筛选 |
| tags | string | 否 | 标签筛选，逗号分隔 |

**响应示例 (200 OK):**

```json
{
  "cities": [
    {
      "id": "beijing",
      "name": "北京",
      "region": "华北",
      "tags": ["历史文化", "首都", "古建筑"]
    },
    {
      "id": "hangzhou",
      "name": "杭州",
      "region": "华东",
      "tags": ["自然风光", "人文历史", "休闲"]
    }
  ]
}
```

**curl 示例:**

```bash
# 获取所有城市
curl http://localhost:48081/api/cities

# 筛选华东地区
curl "http://localhost:48081/api/cities?region=华东"

# 筛选有"美食"标签的城市
curl "http://localhost:48081/api/cities?tags=美食"
```

---

### GET /api/cities/{city_id}

获取城市详情。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| city_id | string | 城市ID |

**响应示例 (200 OK):**

```json
{
  "id": "beijing",
  "name": "北京",
  "region": "华北",
  "tags": ["历史文化", "首都", "古建筑"],
  "description": "北京是华北的热门旅游城市，以历史文化著称。",
  "attractions": [
    {
      "name": "故宫",
      "type": "历史遗迹",
      "duration": "4小时",
      "ticket": 60
    },
    {
      "name": "长城",
      "type": "历史遗迹",
      "duration": "6小时",
      "ticket": 40
    }
  ],
  "avg_budget_per_day": 500,
  "best_seasons": ["春季", "秋季"]
}
```

---

### GET /api/cities/{city_id}/attractions

获取城市景点列表。

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| city_id | string | 城市ID |

**响应示例 (200 OK):**

```json
{
  "city": "北京",
  "attractions": [
    {
      "name": "故宫",
      "type": "历史遗迹",
      "duration": "4小时",
      "ticket": 60
    },
    {
      "name": "长城",
      "type": "历史遗迹",
      "duration": "6小时",
      "ticket": 40
    }
  ]
}
```

---

### GET /api/regions

获取所有地区列表。

**响应示例 (200 OK):**

```json
{
  "regions": ["华北", "华东", "西南", "西北", "华南"]
}
```

---

### GET /api/tags

获取所有标签列表。

**响应示例 (200 OK):**

```json
{
  "tags": ["历史文化", "自然风光", "现代都市", "美食", "海滨度假"]
}
```

---

## 完整使用示例

### Python 请求示例

```python
import httpx
import json

async def chat_example():
    async with httpx.AsyncClient() as client:
        # 1. 创建会话
        session = await client.post(
            "http://localhost:48081/api/session/new",
            json={"name": "旅游咨询"}
        )
        session_id = session.json()["session_id"]
        print(f"会话ID: {session_id}")

        # 2. 发送消息
        async with client.stream(
            "POST",
            "http://localhost:48081/api/chat/stream",
            json={
                "message": "推荐适合春天旅游的城市",
                "session_id": session_id
            }
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"事件: {data.get('type')}")
                    if data.get("type") == "chunk":
                        print(data.get("content"), end="", flush=True)

asyncio.run(chat_example())
```

### JavaScript 请求示例

```javascript
async function chatExample() {
    // 1. 创建会话
    const sessionRes = await fetch('http://localhost:48081/api/session/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: '旅游咨询' })
    });
    const { session_id } = await sessionRes.json();

    // 2. 发送消息
    const response = await fetch('http://localhost:48081/api/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            message: '推荐适合春天旅游的城市',
            session_id
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const line = decoder.decode(value);
        if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            console.log(`事件: ${data.type}`);
            if (data.type === 'chunk') {
                process.stdout.write(data.content);
            }
        }
    }
}

chatExample();
```

---

## 速率限制

当前版本没有速率限制，后续可能添加。

建议客户端：
- 避免频繁请求
- 实现请求重试（指数退避）
- 缓存频繁访问的数据
