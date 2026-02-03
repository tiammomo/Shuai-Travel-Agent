# 开发指南

本指南面向开发者，介绍项目结构、开发环境搭建、代码规范、调试技巧等内容。

---

## 1. 开发环境搭建

### 1.1 前置条件

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | 后端开发 |
| Node.js | 18+ | 前端开发 |
| npm | 9+ | 包管理 |
| Git | 2.0+ | 版本控制 |

### 1.2 克隆项目

```bash
git clone https://github.com/your-repo/ShuaiTravelAgent.git
cd ShuaiTravelAgent
```

### 1.3 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 1.4 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 1.5 配置环境变量

创建 `config/config.json`:

```json
{
  "agent_name": "TravelAssistantAgent",
  "version": "1.0.0",
  "llm": {
    "provider_type": "openai",
    "api_base": "https://api.openai.com/v1",
    "api_key": "YOUR_API_KEY_HERE",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "web": {
    "host": "0.0.0.0",
    "port": 48081,
    "debug": true
  }
}
```

创建 `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:48081
```

---

## 2. 项目结构

### 2.1 目录概览

```
ShuaiTravelAgent/
├── agent/           # AI Agent 模块
├── web/             # Web API 模块
├── shared/          # 共享模块
├── frontend/        # Next.js 前端
├── config/          # 配置文件
├── data/            # 数据存储
├── scripts/         # 脚本工具
└── tests/           # 测试文件
```

### 2.2 模块职责

```
agent/    - AI推理引擎、工具调用、LLM交互
web/      - HTTP API、路由、会话管理
frontend/ - 用户界面、状态管理、API调用
shared/   - 类型定义、常量、协议定义
```

---

## 3. 开发工作流

### 3.1 日常开发

**终端1 - 启动后端（热重载）**

```bash
# 方式1: 使用 run_api.py
python run_api.py

# 方式2: 使用 uvicorn 直接
cd web/src
uvicorn main:app --reload --host 0.0.0.0 --port 48081
```

**终端2 - 启动前端（热更新）**

```bash
cd frontend
npm run dev
```

**终端3 - 运行测试（可选）**

```bash
# 后端测试
python -m pytest src/tests/ -v

# 前端测试
cd frontend
npm run test:run
```

### 3.2 代码修改流程

```
1. 创建功能分支
   git checkout -b feature/your-feature

2. 编写代码
   - 修改相关模块
   - 遵循代码规范

3. 添加测试
   - 单元测试
   - 集成测试

4. 运行测试
   - 确保全部通过

5. 提交代码
   git add .
   git commit -m "feat: 添加新功能"

6. 推送并创建 PR
```

---

## 4. 代码规范

### 4.1 Python 代码规范

**命名约定**

```python
# 包名: 小写简短
import utils
from core import agent

# 类名: PascalCase
class SessionManager:
    ...

# 函数/变量: snake_case
def get_session_id():
    session_count = 0

# 常量: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 私有方法/变量: 前缀_
class UserService:
    def _private_method(self):
        ...
    _private_var = 42
```

**类型注解**

```python
from typing import Dict, List, Optional, Any

def process_message(
    message: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    ...
```

**文档字符串**

```python
class SessionManager:
    """管理用户会话的生命周期。

    负责会话的创建、更新、删除和持久化。
    """

    def create_session(self, name: str) -> str:
        """创建新会话。

        Args:
            name: 会话名称

        Returns:
            新创建的会话ID

        Raises:
            ValueError: 会话名称为空
        """
        ...
```

### 4.2 TypeScript 代码规范

**命名约定**

```typescript
// 文件名: kebab-case
chat-service.ts
session-store.ts

// 类/接口: PascalCase
interface SessionState {
    id: string;
    name: string;
}

// 函数/变量: camelCase
function createSession(name: string): string {
    const sessionId = generateId();
    return sessionId;
}

// 常量: UPPER_SNAKE_CASE 或 camelCase
const MAX_SESSION_COUNT = 100;
const defaultSessionName = '新会话';
```

**类型定义**

```typescript
// 接口定义
interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: string;
    reasoning?: string;
}

// 类型别名
type SessionStatus = 'active' | 'inactive' | 'expired';

// 函数类型
type ChatHandler = (message: string) => Promise<string>;
```

### 4.3 代码格式化

**Python (Ruff)**

```bash
# 检查代码
ruff check .

# 自动修复
ruff check --fix .
```

**TypeScript (ESLint + Prettier)**

```bash
# 检查代码
npm run lint

# 修复
npm run lint:fix
```

---

## 5. 调试技巧

### 5.1 后端调试

**日志输出**

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("函数开始执行")
    logger.debug(f"调试信息: {variable}")
    logger.warning("警告信息")
    logger.error("错误信息")
```

**断点调试**

```bash
# 使用 Python debugger
python -m pdb script.py

# 或使用 VS Code
# 1. F5 启动调试
# 2. 设置断点
# 3. 查看变量
```

**API 测试**

使用 Swagger 文档: http://localhost:48081/docs

### 5.2 前端调试

**浏览器开发者工具**

```javascript
// console.log 调试
console.log('变量值:', variable);
console.error('错误:', error);

// 调试组件
console.trace();
```

**React DevTools**

- 安装 Chrome/Firefox 扩展
- 查看组件树
- 检查 state/props

**网络请求**

- Network 面板查看 API 请求
- 检查 SSE 流式响应

### 5.3 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 后端启动失败 | 检查 config.json 是否存在，API Key 是否配置 |
| 前端无法连接后端 | 检查 NEXT_PUBLIC_API_BASE 环境变量 |
| 端口被占用 | 修改端口或杀死占用进程 |
| 依赖安装失败 | 检查 Python/Node 版本，清理缓存 |

---

## 6. 添加新功能

### 6.1 添加新工具（Agent模块）

**步骤1: 定义工具**

```python
# agent/src/tools/travel_tools.py
from .base import Tool, ToolResult

class CitySearchTool(Tool):
    """城市搜索工具"""

    @property
    def name(self) -> str:
        return "search_cities"

    @property
    def description(self) -> str:
        return "根据条件搜索城市"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "region": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }

    async def execute(self, region: str = None, tags: List[str] = None) -> ToolResult:
        # 实现搜索逻辑
        return ToolResult(success=True, data={...})
```

**步骤2: 注册工具**

```python
# agent/src/core/travel_agent.py
def _register_tools(self) -> None:
    tools = [
        # ... 现有工具
        (CitySearchTool(), self._search_cities),
    ]
    for tool_info, executor in tools:
        self.react_agent.register_tool(tool_info, executor)
```

**步骤3: 添加工具执行函数**

```python
def _search_cities(self, region: str = None, tags: List[str] = None) -> Dict[str, Any]:
    from ..environment.travel_data import TravelData
    env = TravelData(self.config_manager)
    return env.search_cities(region=region, interests=tags)
```

### 6.2 添加新API端点

**步骤1: 创建路由文件**

```python
# web/src/routes/analytics.py
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()

@router.get("/analytics/summary")
async def get_analytics_summary(days: int = 7):
    """获取分析摘要"""
    # 实现逻辑
    return {"summary": {...}}
```

**步骤2: 注册路由**

```python
# web/src/main.py
from .routes import (
    chat_router,
    session_router,
    analytics_router,  # 新增
    # ...
)

app.include_router(analytics_router, prefix="/api", tags=["analytics"])
```

### 6.3 添加新前端组件

**步骤1: 创建组件**

```typescript
// frontend/src/components/analytics/AnalyticsPanel.tsx
import { useState, useEffect } from 'react';
import { Card, Statistic } from 'antd';

interface AnalyticsData {
    totalSessions: number;
    totalMessages: number;
    avgResponseTime: number;
}

export function AnalyticsPanel() {
    const [data, setData] = useState<AnalyticsData | null>(null);

    useEffect(() => {
        // 加载数据
    }, []);

    if (!data) return <div>加载中...</div>;

    return (
        <Card>
            <Statistic title="总会话数" value={data.totalSessions} />
            <Statistic title="总消息数" value={data.totalMessages} />
        </Card>
    );
}
```

**步骤2: 添加到页面**

```typescript
// frontend/src/app/page.tsx
import { AnalyticsPanel } from '@/components/analytics/AnalyticsPanel';

export default function HomePage() {
    return (
        <div>
            <AnalyticsPanel />
            {/* 其他组件 */}
        </div>
    );
}
```

### 6.4 添加测试

**后端测试**

```python
# tests/unit/test_services/test_analytics_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.get_summary = AsyncMock(return_value={...})
    return repo

@pytest.mark.asyncio
async def test_get_analytics_summary(mock_repository):
    from web.src.services.analytics_service import AnalyticsService
    service = AnalyticsService(mock_repository)

    result = await service.get_summary(days=7)

    assert result['success'] is True
    assert 'summary' in result
```

**前端测试**

```typescript
// tests/unit/components/AnalyticsPanel.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { AnalyticsPanel } from '@/components/analytics/AnalyticsPanel';
import { describe, it, expect, vi } from 'vitest';

describe('AnalyticsPanel', () => {
    it('显示加载状态', () => {
        render(<AnalyticsPanel />);
        expect(screen.getByText('加载中...')).toBeInTheDocument();
    });
});
```

---

## 7. Git 工作流

### 7.1 分支命名

| 分支类型 | 命名示例 | 说明 |
|----------|----------|------|
| 主分支 | `main` | 生产环境代码 |
| 开发分支 | `develop` | 开发主分支 |
| 功能分支 | `feature/chat-streaming` | 新功能 |
| 修复分支 | `bugfix/fix-session-bug` | Bug修复 |
| 热修复分支 | `hotfix/critical-fix` | 紧急修复 |

### 7.2 提交规范

```
feat: 新功能
fix: Bug修复
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

示例:

```bash
git commit -m "feat: 添加城市搜索工具"
git commit -m "fix: 修复会话超时问题"
git commit -m "docs: 更新API文档"
```

### 7.3 代码审查

1. 创建 Pull Request
2. 描述变更内容
3. 添加截图/演示（如有UI变更）
4. 关联 Issue（如有）
5. 等待 Review
6. 根据反馈修改
7. 合并到主分支

---

## 8. 资源

### 8.1 学习资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Next.js 文档](https://nextjs.org/docs)
- [React 文档](https://react.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [gRPC Python 教程](https://grpc.io/docs/languages/python/)

### 8.2 相关链接

- [项目仓库](https://github.com/your-repo/ShuaiTravelAgent)
- [Issue Tracker](https://github.com/your-repo/ShuaiTravelAgent/issues)
- [Wiki](https://github.com/your-repo/ShuaiTravelAgent/wiki)
