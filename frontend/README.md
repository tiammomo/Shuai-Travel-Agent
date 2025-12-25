# 小帅旅游助手 - React前端

基于React + TypeScript + Vite构建的现代化前端界面。

## 技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design** - UI组件库
- **Axios** - HTTP客户端
- **React Markdown** - Markdown渲染

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端将运行在 `http://localhost:3000`

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

## 功能特性

### ✅ 已实现功能

- **实时聊天** - 支持流式SSE响应
- **会话管理** - 创建、切换、删除会话
- **消息历史** - 完整的对话记录
- **AI思考提示** - 显示"正在思考中..."状态
- **停止控制** - 中断流式响应
- **响应式设计** - 适配多设备
- **Markdown渲染** - 支持富文本显示

### 🎯 核心组件

| 组件 | 职责 | 文件 |
|------|------|------|
| **App** | 主应用布局 | `src/App.tsx` |
| **ChatArea** | 聊天交互区域 | `src/components/ChatArea.tsx` |
| **MessageList** | 消息列表渲染 | `src/components/MessageList.tsx` |
| **Sidebar** | 侧边栏（会话管理）| `src/components/Sidebar.tsx` |
| **AppContext** | 全局状态管理 | `src/context/AppContext.tsx` |
| **APIService** | 后端API调用 | `src/services/api.ts` |

## API代理配置

开发环境下，前端请求会自动代理到后端API（配置在`vite.config.ts`）：

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # React组件
│   │   ├── ChatArea.tsx     # 聊天区域
│   │   ├── MessageList.tsx  # 消息列表
│   │   └── Sidebar.tsx      # 侧边栏
│   ├── context/
│   │   └── AppContext.tsx   # Context状态管理
│   ├── services/
│   │   └── api.ts           # API服务
│   ├── types/
│   │   └── index.ts         # TypeScript类型定义
│   ├── App.tsx              # 主应用组件
│   ├── App.css              # 应用样式
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
├── index.html               # HTML模板
├── package.json             # 项目配置
├── tsconfig.json            # TypeScript配置
├── vite.config.ts           # Vite配置
└── README.md                # 本文档
```

## 与后端集成

确保后端FastAPI服务运行在 `http://localhost:8000`：

```bash
# 在项目根目录
python run_api.py
```

## 环境要求

- Node.js >= 16
- npm >= 8

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint
```

## 特性说明

### SSE流式响应处理

使用Fetch API + ReadableStream处理SSE流：

```typescript
const reader = response.body?.getReader();
while (true) {
  const { done, value } = await reader.read();
  // 处理流数据...
}
```

### 状态管理

使用Context API进行全局状态管理，避免引入Redux的复杂性：

- 会话状态
- 消息历史
- 流式控制
- 配置管理

### 组件化设计

- **纯展示组件**：MessageList
- **容器组件**：ChatArea, Sidebar
- **上下文提供者**：AppProvider

## License

MIT
