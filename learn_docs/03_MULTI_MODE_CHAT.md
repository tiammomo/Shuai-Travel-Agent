# 多模式对话系统

本文档介绍 ShuaiTravelAgent 中的三种对话模式：Direct、ReAct 和 Plan，分析各模式的适用场景和实现原理。

## 模式概述

### 三种模式对比

| 模式 | 响应速度 | 工具调用 | 推理深度 | 适用场景 |
|------|----------|----------|----------|----------|
| Direct | 最快 | 无 | 无 | 简单对话、常识问答 |
| ReAct | 中等 | 支持 | 中等 | 需要工具调用的复杂任务 |
| Plan | 较慢 | 支持 | 高 | 多步骤复杂任务规划 |

### 模式选择建议

- **Direct 模式**：用户问题简单直接，无需搜索或查询数据
- **ReAct 模式**：需要执行工具调用（如查询景点、计算预算）
- **Plan 模式**：复杂的多步骤任务，需要先规划再执行

## Direct 模式

### 工作原理

直接调用 LLM 生成回答，不经过 ReAct 推理循环：

```
用户输入 → LLM → 回答
```

### 实现代码

```python
async def _process_direct_mode(
    self,
    user_input: str,
    answer_callback=None,
    done_callback=None,
    thinking_callback=None
) -> Dict[str, Any]:
    # 发送思考开始
    if thinking_callback:
        thinking_callback("【直接模式】直接生成回答...\n\n", 0.0)

    # 构建消息
    messages = [
        {"role": "system", "content": "你是一个专业的旅游助手。"},
        {"role": "user", "content": user_input}
    ]

    # 流式生成回答
    if hasattr(self.llm_client, 'chat_stream') and answer_callback:
        accumulated_answer = ""
        for token in self.llm_client.chat_stream(messages, temperature=0.7):
            accumulated_answer += token
            answer_callback(token)

        answer = accumulated_answer

    # 返回结果
    return {
        "success": True,
        "answer": answer,
        "mode": "direct",
        "reasoning": {
            "text": "<thinking>\n[Direct Mode]\n直接调用 LLM 生成回答\n</thinking>",
            "total_steps": 0,
            "tools_used": []
        },
        "history": []
    }
```

### 适用场景

- 问候和闲聊
- 简单的旅游常识问题
- 需要快速响应的场景
- 无需访问外部数据的查询

### 示例对话

```
用户：你好！
系统：【直接模式】直接生成回答...
      你好呀！有什么旅游问题可以问我哦～

用户：北京是哪个国家的首都？
系统：【直接模式】直接生成回答...
      北京是中华人民共和国的首都，也是中国政治、文化和国际交往中心。
```

## ReAct 模式

### 工作原理

完整的 ReAct 推理循环，思考与行动交替进行：

```
用户输入 → 理解任务 → 制定计划 → 执行工具 → 观察结果 → 思考 → ...
                                                    ↓
                                               生成回答 ←─┘
```

### 实现代码

```python
async def _process_react_mode(
    self,
    user_input: str,
    context: Dict,
    answer_callback=None,
    done_callback=None,
    thinking_callback=None
) -> Dict[str, Any]:
    # 设置思考流式回调
    if hasattr(self.react_agent, 'set_think_stream_callback') and thinking_callback:
        self.react_agent.set_think_stream_callback(thinking_callback)

    # 执行 ReAct 循环
    result = await self.react_agent.run(user_input, context)

    if result.get('success'):
        history = result.get('history', [])
        reasoning_text = self._build_reasoning_text(history)
        answer = self._extract_answer(history)

        # 流式生成最终回答
        if hasattr(self.llm_client, 'chat_stream') and answer_callback:
            for token in self.llm_client.chat_stream(messages, temperature=0.7):
                answer_callback(token)

        return {
            "success": True,
            "answer": answer,
            "mode": "react",
            "reasoning": {
                "text": reasoning_text,
                "total_steps": len(history),
                "tools_used": self._extract_tools_used(history)
            },
            "history": history
        }
```

### 适用场景

- 城市推荐查询
- 景点信息获取
- 预算计算
- 需要工具调用的任何场景

### 示例对话

```
用户：推荐一些适合美食游的城市

【阶段一：理解任务】
用户输入：「推荐一些适合美食游的城市」
意图识别：城市推荐

【阶段二：制定计划】
选择 search_cities 工具，参数：interests=["美食"]

【执行阶段 - 步骤 1】
工具: search_cities [成功]
结果: 获取到 5 个推荐城市

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【生成阶段 - 最终回答】
根据你的需求，我为你推荐以下美食城市：

## 成都
- 推荐天数：3-4天
- 预算：约 500-800元/天
- 必游景点：...
```

## Plan 模式

### 工作原理

先制定完整执行计划，再按计划逐步执行：

```
用户输入 → LLM生成计划 → 分解步骤 → 逐个执行 → 整合结果 → 生成回答
```

### 阶段划分

| 阶段 | 说明 |
|------|------|
| 阶段一：制定计划 | 分析任务，生成详细执行计划 |
| 阶段二：分解任务 | 将计划分解为可执行步骤 |
| 阶段三：执行工具 | 按计划逐步执行工具调用 |
| 阶段四：生成回答 | 整合所有执行结果生成最终回答 |

### 实现代码

```python
async def _process_plan_mode(
    self,
    user_input: str,
    context: Dict,
    answer_callback=None,
    done_callback=None,
    thinking_callback=None
) -> Dict[str, Any]:
    # Step 1: 生成执行计划（阶段一：制定计划）
    if thinking_callback:
        thinking_callback("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n【规划模式 - 阶段一：制定计划】\n正在分析任务并生成执行计划...\n\n", 0.0)

    plan_prompt = f"""用户请求: {user_input}

请制定一个详细的执行计划，以 JSON 格式返回：
{{
    "steps": [
        {{
            "step": 1,
            "action": "工具名称",
            "params": {{"参数": "值"}},
            "description": "步骤描述",
            "phase": "阶段标识"
        }}
    ],
    "goal": "本次规划的最终目标"
}}

只返回 JSON，不要其他内容。"""

    plan_result = self.llm_client.chat([
        {"role": "system", "content": "你是一个专业的旅游规划助手。"},
        {"role": "user", "content": plan_prompt}
    ], temperature=0.3)

    # 解析计划
    plan_data = json.loads(plan_result.get('content', '{}'))
    steps = plan_data.get('steps', [])
    goal = plan_data.get('goal', '完成用户请求')

    if thinking_callback:
        thinking_callback(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n【规划模式】计划生成完成\n目标: {goal}\n共 {len(steps)} 个执行步骤\n\n", 0.0)

    # Step 2: 执行计划（阶段二：逐步执行）
    history = []
    phases = {
        'planning': '阶段二：分解任务',
        'execution': '阶段三：执行工具',
        'generation': '阶段四：生成回答'
    }

    for i, step in enumerate(steps):
        step_num = i + 1
        action_name = step.get('action', '')
        description = step.get('description', '')
        phase_name = phases.get(step.get('phase', 'execution'))

        if thinking_callback:
            progress = f"[{step_num}/{len(steps)}]"
            thinking_callback(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n【规划模式 - {phase_name}】\n{progress} {description}\n\n", 0.0)

        # 执行工具
        result = {'success': False}
        if action_name and action_name != 'none':
            tool = self.react_agent.tool_registry.get_tool(action_name)
            if tool:
                result = await tool.execute(**step.get('params', {}))

        history.append({
            'step': step_num,
            'phase': phase_name,
            'action': action_name,
            'result': result,
            'description': description
        })

    # Step 3: 生成最终回答（阶段四：生成回答）
    if thinking_callback:
        thinking_callback("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n【规划模式 - 阶段四：生成回答】\n正在整合执行结果...\n\n", 0.0)

    tool_results = [h.get('result', {}) for h in history if h.get('result', {}).get('success')]
    answer = self._generate_answer_from_results(user_input, tool_results)

    return {
        "success": True,
        "answer": answer,
        "mode": "plan",
        "reasoning": {...},
        "history": history,
        "plan": steps
    }
```

### 适用场景

- 多日行程规划
- 需要多个工具协同的复杂任务
- 需要先收集信息再综合分析的场景

### 示例对话

```
用户：帮我规划一个北京3日游，包括景点和美食

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段一：制定计划】
正在分析任务并生成执行计划...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式】计划生成完成
目标: 完成北京3日游规划
共 4 个执行步骤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段三：执行工具】
[1/4] 查询北京城市信息

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段三：执行工具】
[2/4] 获取北京热门景点

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段三：执行工具】
[3/4] 搜索北京特色美食

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段三：执行工具】
[4/4] 生成路线规划

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【规划模式 - 阶段四：生成回答】
正在整合执行结果...
```

## 前端集成

### 模式选择器组件

```tsx
// ChatModeSelector.tsx
interface ChatModeSelectorProps {
  value: ChatMode;
  onChange: (mode: ChatMode) => void;
}

const ChatModeSelector: React.FC<ChatModeSelectorProps> = ({
  value,
  onChange
}) => {
  return (
    <Select value={value} onChange={onChange}>
      <Option value="direct">Direct 快速响应</Option>
      <Option value="react">ReAct 推理模式</Option>
      <Option value="plan">Plan 规划模式</Option>
    </Select>
  );
};
```

### 聊天服务调用

```typescript
// chat_service.ts
async function sendMessage(
  message: string,
  mode: 'direct' | 'react' | 'plan',
  onThinking: (content: string) => void,
  onToken: (token: string) => void
) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ message, mode })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.type === 'thinking') {
          onThinking(data.content);
        } else if (data.type === 'token') {
          onToken(data.content);
        }
      }
    }
  }
}
```

## 后端 API

### 请求格式

```json
{
  "message": "规划北京三日游",
  "session_id": "session_123",
  "mode": "react"
}
```

### 响应格式（SSE 流式）

```
data: {"type": "thinking", "content": "【理解阶段】..."}

data: {"type": "token", "content": "北"}

data: {"type": "token", "content": "京"}

...

data: {"type": "done", "result": {...}}
```

## 性能对比

### 响应时间（估算）

| 模式 | 简单问题 | 中等问题 | 复杂问题 |
|------|----------|----------|----------|
| Direct | < 1s | 1-2s | 2-3s |
| ReAct | 1-2s | 2-5s | 5-10s |
| Plan | 3-5s | 5-10s | 10-30s |

### _tokens 消耗对比

| 模式 | 简单问题 | 中等问题 | 复杂问题 |
|------|----------|----------|----------|
| Direct | 100-200 | 300-500 | 500-800 |
| ReAct | 200-400 | 500-1000 | 1000-2000 |
| Plan | 400-800 | 800-1500 | 1500-3000 |

## 模式选择策略

### 自动模式选择

可以根据用户输入自动选择合适的模式：

```python
def select_mode(user_input: str) -> ChatMode:
    # 简单问候 → Direct
    if any(kw in user_input for kw in ["你好", "在吗", "hello"]):
        return ChatMode.DIRECT

    # 包含规划相关关键词 → Plan
    if any(kw in user_input for kw in ["规划", "计划", "行程安排"]):
        return ChatMode.PLAN

    # 包含查询相关关键词 → ReAct
    if any(kw in user_input for kw in ["推荐", "查询", "搜索", "景点"]):
        return ChatMode.REACT

    # 默认 ReAct
    return ChatMode.REACT
```

### 用户偏好持久化

```python
# 保存用户模式偏好
preferences = {
    "default_mode": "react",
    "mode_history": [
        {"query": "...", "mode": "react", "rating": 5}
    ]
}
```

## 扩展指南

### 添加新模式

1. 在 `ChatMode` 枚举中添加新模式
2. 实现 `_process_{mode}_mode` 方法
3. 在 `process_with_mode` 中添加处理分支
4. 更新前端模式选择器

```python
class ChatMode(Enum):
    DIRECT = "direct"
    REACT = "react"
    PLAN = "plan"
    CUSTOM = "custom"  # 新增模式

async def _process_custom_mode(self, ...):
    # 实现自定义模式逻辑
    pass
```

### 自定义模式组合

可以组合不同模式的特点：

```python
# Plan + ReAct 混合模式
async def _process_plan_react_mode(self, user_input: str, ...):
    # 1. 使用 Plan 模式制定计划
    plan = await self._generate_plan(user_input)

    # 2. 使用 ReAct 模式执行计划
    result = await self._execute_with_react(plan)

    return result
```

## 常见问题

### Q: 什么情况下应该使用 Plan 模式而不是 ReAct 模式？

Plan 模式适用于：
- 明确需要多个步骤的任务
- 需要先收集信息再决策的场景
- 用户期望看到明确的执行计划

ReAct 模式适用于：
- 动态决策的任务
- 步骤之间相互依赖
- 需要根据中间结果调整策略

### Q: 模式切换会影响对话历史吗？

不会。每个模式独立处理，但可以通过 `session_id` 共享对话历史：

```python
# 不同模式使用相同 session_id，对话历史共享
result1 = await agent.process_with_mode("你好", mode=ChatMode.DIRECT, session_id="s1")
result2 = await agent.process_with_mode("推荐城市", mode=ChatMode.REACT, session_id="s1")  # 能感知到之前的对话
```

### Q: 如何处理模式执行失败？

各模式有独立的错误处理：

```python
# Direct 模式：回退到 ReAct 模式
try:
    result = await self._process_direct_mode(...)
except Exception as e:
    # 回退到 ReAct 模式
    result = await self._process_react_mode(...)
```
