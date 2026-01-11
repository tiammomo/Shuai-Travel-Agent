# ReAct Agent 核心机制

本文档详细解析 ShuaiTravelAgent 中 ReAct Agent 的实现原理，帮助开发者理解推理与行动循环的工作方式。

## 什么是 ReAct

ReAct（Reasoning and Acting）是一种结合推理和行动的人工智能范式。智能体通过以下循环来处理任务：

1. **Think（思考）** - 分析当前状态，决定下一步行动
2. **Act（行动）** - 执行工具调用，获取结果
3. **Observe（观察）** - 收集行动结果，作为下一步的输入
4. **Evaluate（评估）** - 评估行动效果，决定是否继续

## 核心架构

### 模块结构

```
agent/src/core/
├── react_agent.py      # ReAct Agent 核心实现
├── travel_agent.py     # 旅游助手封装
├── intent_recognizer.py # 意图识别
├── decision_engine.py  # 决策引擎
├── style_config.py     # 风格配置
└── ...
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| AgentState | react_agent.py:89 | 智能体状态枚举 |
| ActionStatus | react_agent.py:105 | 行动执行状态 |
| ThoughtType | react_agent.py:117 | 思考类型枚举 |
| ThoughtPhase | react_agent.py:130 | 执行阶段枚举（分层用） |
| ToolInfo | react_agent.py:148 | 工具元数据 |
| Action | react_agent.py:157 | 行动数据结构 |
| Thought | react_agent.py:246 | 思考数据结构 |
| ToolRegistry | react_agent.py:295 | 工具注册表 |
| ShortTermMemory | react_agent.py:423 | 短期记忆管理 |
| ThoughtEngine | react_agent.py:490 | 思考生成引擎 |
| EvaluationEngine | react_agent.py:1094 | 结果评估引擎 |
| ReActAgent | react_agent.py:1137 | 主智能体类 |

## 状态机

### AgentState（智能体状态）

```python
class AgentState(Enum):
    IDLE = auto()        # 空闲状态，等待新任务
    REASONING = auto()   # 推理状态，正在分析任务
    ACTING = auto()      # 行动状态，正在执行工具
    OBSERVING = auto()   # 观察状态，正在收集结果
    EVALUATING = auto()  # 评估状态，正在评估效果
    COMPLETED = auto()   # 完成状态，任务执行完毕
    ERROR = auto()       # 错误状态，执行过程异常
```

### 状态转换图

```
                    ┌─────────────┐
                    │    IDLE     │
                    └──────┬──────┘
                           │ run()
                           ▼
                    ┌─────────────┐
                    │  REASONING  │  ◄────────────────┐
                    └──────┬──────┘                   │
                           │ _think()                 │
                           ▼                          │
                    ┌─────────────┐                   │
                    │   ACTING    │                   │
                    └──────┬──────┘                   │
                           │ _act()                   │
                           ▼                          │
                    ┌─────────────┐                   │
                    │  OBSERVING  │                   │
                    └──────┬──────┘                   │
                           │ _observe()               │
                           ▼                          │
                    ┌─────────────┐                   │
                    │  EVALUATING │                   │
                    └──────┬──────┘                   │
                           │ _evaluate()              │
                           ▼                          │
              ┌────────────┴────────────┐             │
              │   COMPLETED  │  ERROR   │             │
              └────────────┬────────────┘             │
                    _should_stop() = False ───────────┘
```

## 执行阶段（分层机制）

### ThoughtPhase 枚举

为了更好地展示执行过程，系统引入了阶段分层机制：

```python
class ThoughtPhase(Enum):
    UNDERSTANDING = auto()  # 理解阶段：分析任务、提取实体
    PLANNING = auto()       # 规划阶段：制定执行计划
    EXECUTION = auto()      # 执行阶段：工具调用和结果观察
    GENERATION = auto()     # 生成阶段：生成最终回答
```

### 阶段与步骤的映射

| 步骤 | 阶段 | 说明 |
|------|------|------|
| 步骤 0 | UNDERSTANDING + PLANNING | 分析任务并制定计划 |
| 步骤 1 | PLANNING | 规划阶段 |
| 中间步骤 | EXECUTION | 执行工具调用 |
| 最后步骤 | GENERATION | 生成最终回答 |

### 思考内容格式示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【阶段一：理解任务】
用户输入：「云南旅游推荐」
意图识别：城市推荐
提取信息：目的地=云南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【阶段二：制定计划】
选择 search_cities 工具，参数：interests=[], budget_min=None, budget_max=None, season=None
```

## 思考类型

### ThoughtType 枚举

```python
class ThoughtType(Enum):
    ANALYSIS = auto()    # 分析型思考：理解任务和提取信息
    PLANNING = auto()    # 规划型思考：制定执行计划
    DECISION = auto()    # 决策型思考：做出最终决策
    REFLECTION = auto()  # 反思型思考：回顾和总结
    INFERENCE = auto()   # 推理型思考：从结果中得出结论
```

### 类型与阶段的映射

| 思考类型 | 默认阶段 | 说明 |
|----------|----------|------|
| ANALYSIS | UNDERSTANDING | 任务分析 |
| PLANNING | PLANNING | 执行规划 |
| INFERENCE | EXECUTION | 执行推理 |
| REFLECTION | EXECUTION | 结果反思 |
| DECISION | GENERATION | 最终决策 |

## 工具系统

### ToolInfo 数据结构

```python
@dataclass
class ToolInfo:
    name: str                           # 工具名称（唯一标识）
    description: str                    # 工具功能描述
    parameters: Dict[str, Any]          # OpenAI 风格参数规范
    required_params: List[str]          # 必填参数列表
    timeout: int = 30                   # 超时时间（秒）
    category: str = "general"           # 工具分类
    tags: List[str] = []                # 工具标签
```

### 旅游工具列表

| 工具名称 | 功能描述 | 必填参数 |
|----------|----------|----------|
| search_cities | 根据条件搜索城市 | 无（可选） |
| query_attractions | 查询城市景点 | cities |
| generate_route | 生成旅游路线规划 | city, days |
| calculate_budget | 计算旅游预算 | city, days |
| get_city_info | 获取城市详细信息 | city |
| llm_chat | LLM 对话回答 | query |
| generate_city_recommendation | 生成城市推荐 | user_query, available_cities |
| generate_route_plan | 生成详细路线计划 | city, days |

### 工具注册与执行

```python
# 注册工具
agent = ReActAgent(name="TravelAgent")
agent.register_tool(tool_info, executor_func)

# 执行工具
result = await agent.tool_registry.execute("tool_name", {"param": "value"})
```

## ReAct 主循环

### 循环流程

```python
async def run(self, task: str, context: Dict = None) -> Dict:
    self.state.task = task
    self.state.context = context or {}
    self.state.current_step = 0

    while self.state.current_step < self.max_steps:
        # 1. 观察阶段
        observation = await self._observe()

        # 2. 思考阶段（核心）
        thought = await self._think(observation)

        # 3. 检查是否应该停止
        if self._should_stop(thought):
            break

        # 4. 行动阶段
        action = await self._act(thought)

        # 5. 评估阶段
        evaluation = await self._evaluate(action)

        # 6. 更新状态和记录历史
        self._update_state(action, evaluation)
        self._record_history(thought, action, evaluation)

    return self._build_result()
```

### 关键方法详解

#### _think() - 思考阶段

根据当前步骤自动设置阶段，生成思考内容：

```python
async def _think(self, observation: Observation) -> Thought:
    current_step = self.state.current_step

    if current_step == 0:
        # 理解 + 规划阶段
        thought = self.thought_engine.analyze_task(...)
        plan_thought = self.thought_engine.plan_actions(...)
        thought.phase = ThoughtPhase.UNDERSTANDING
        plan_thought.phase = ThoughtPhase.PLANNING
    elif self._is_final_step():
        # 生成阶段
        thought = self._create_thought(..., ThoughtPhase.GENERATION)
    else:
        # 执行阶段
        thought = self._create_thought(..., ThoughtPhase.EXECUTION)

    return thought
```

#### _act() - 行动阶段

从思考决策中提取行动并执行：

```python
async def _act(self, thought: Thought) -> Action:
    action = self._extract_action(thought)

    if action:
        action.mark_running()
        try:
            result = await self.tool_registry.execute(
                action.tool_name,
                action.parameters
            )
            action.mark_success(result)
        except Exception as e:
            action.mark_failed(str(e))

    return action
```

#### _should_stop() - 停止条件

```python
def _should_stop(self, thought: Thought) -> bool:
    # 条件1：执行了最终工具且成功
    if thought.type == ThoughtType.INFERENCE:
        last_action = self.action_history[-1]
        if last_action.tool_name in ["llm_chat", "generate_city_recommendation", "generate_route_plan"]:
            if last_action.status == ActionStatus.SUCCESS:
                return True

    # 条件2：高置信度且有决策
    if thought.confidence > 0.9 and thought.decision:
        return True

    # 条件3：达到最大步骤数
    if self.state.current_step >= self.max_steps - 1:
        return True

    return False
```

## 历史记录

### 历史数据结构

```python
{
    "step": 0,                              # 步骤编号
    "phase": "UNDERSTANDING",               # 执行阶段
    "thought": {
        "id": "thought_0",
        "type": "ANALYSIS",
        "phase": "UNDERSTANDING",
        "content": "思考内容...",
        "confidence": 0.85,
        "decision": "[{\"step\": 1, \"action\": \"...\"}]"
    },
    "action": {
        "id": "action_0",
        "tool_name": "search_cities",
        "status": "SUCCESS",
        "duration": 1500,
        "result": {"success": True, "cities": [...]},
        "error": None
    },
    "evaluation": {
        "success": True,
        "duration": 1500,
        "has_result": True
    },
    "timestamp": "2025-01-11T10:30:00.000000"
}
```

### 执行结果

```python
{
    "success": True,
    "task": "规划北京三日游",
    "steps_completed": 3,
    "successful_steps": 3,
    "total_duration": 4500,
    "history": [...]  # 历史记录列表
}
```

## 思考流式输出

### 回调机制

ReAct Agent 支持实时思考流式输出，通过回调函数传递思考内容：

```python
# 设置思考流式回调
def on_thinking(content: str, elapsed: float):
    print(f"[{elapsed:.1f}s] {content}")

agent.set_think_stream_callback(on_thinking)

# 执行任务
result = await agent.run("规划北京三日游")
```

### 回调触发时机

每个 ReAct 循环步骤完成后触发回调，传递：
- `content`: 思考内容文本
- `elapsed`: 已耗时秒数

## 与其他模块的集成

### 意图识别集成

```python
# 在 _think 中调用意图识别
intent_result = await intent_recognizer.recognize(task, context)

# 根据意图选择工具
if intent_result.intent == IntentType.CITY_RECOMMENDATION:
    plan_thought = self._plan_city_recommendation()
```

### 风格配置集成

```python
# 根据意图选择回复风格
style = style_manager.get_style_for_task(
    intent_result.intent.value,
    intent_result.sentiment
)
```

### 决策引擎集成

```python
# 使用决策引擎确定下一步行动
decision = decision_engine.make_decision(intent, context, tool_results)
```

## 扩展指南

### 添加新工具

1. 定义 ToolInfo
2. 实现执行函数
3. 注册到 ReActAgent

```python
# 1. 定义工具信息
new_tool = ToolInfo(
    name="custom_tool",
    description="自定义工具描述",
    parameters={...},
    required_params=["param1"],
    category="custom",
    tags=["custom", "special"]
)

# 2. 定义执行函数
async def custom_executor(param1: str) -> Dict:
    # 实现逻辑
    return {"result": "..."}

# 3. 注册工具
agent.register_tool(new_tool, custom_executor)
```

### 添加新思考类型

1. 在 ThoughtType 中添加新枚举值
2. 在 _infer_phase 中映射到对应阶段
3. 在 _think 中处理新类型的逻辑

## 性能考虑

### 最大步骤数

```python
agent = ReActAgent(
    name="TravelAgent",
    max_steps=10,       # 最大执行步骤数
    max_reasoning_depth=5  # 最大推理深度
)
```

### 工具超时控制

```python
tool_info = ToolInfo(
    name="slow_tool",
    description="耗时工具",
    parameters={...},
    timeout=60          # 超时时间（秒）
)
```

## 常见问题

### Q: 为什么步骤 0 包含理解和规划？

步骤 0 的设计是为了在第一时间理解用户意图并制定执行计划，提高执行效率。

### Q: 如何区分不同类型的思考？

通过 `thought.type` 属性判断：
- `ANALYSIS`: 任务分析
- `PLANNING`: 规划
- `INFERENCE`: 推理
- `REFLECTION`: 反思
- `DECISION`: 决策

### Q: 工具执行失败怎么办？

系统会自动：
1. 记录错误信息
2. 标记 ActionStatus 为 FAILED
3. 在下一步思考中进行反思和调整策略
