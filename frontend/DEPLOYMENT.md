# React前端部署指南

## 📋 目录
- [快速开始](#快速开始)
- [开发环境](#开发环境)
- [生产构建](#生产构建)
- [部署方案](#部署方案)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 快速开始

#### 前置要求
- Node.js >= 16.0.0
- npm >= 8.0.0
- 后端 API 服务运行在 `http://localhost:8000`

#### 启动前端
```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

访问：http://localhost:3000

---

## 💻 开发环境

### 项目结构
```
frontend/
├── src/
│   ├── components/          # React组件
│   │   ├── ChatArea.tsx     # 聊天交互区域
│   │   ├── MessageList.tsx  # 消息列表
│   │   └── Sidebar.tsx      # 侧边栏（会话管理）
│   ├── context/             # 状态管理
│   │   └── AppContext.tsx   # 全局Context
│   ├── services/            # API服务
│   │   └── api.ts           # 后端API调用
│   ├── types/               # TypeScript类型
│   │   └── index.ts         # 类型定义
│   ├── App.tsx              # 主应用
│   ├── App.css              # 应用样式
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
├── index.html               # HTML模板
├── package.json             # 依赖配置
├── vite.config.ts           # Vite配置
├── tsconfig.json            # TypeScript配置
├── .env.development         # 开发环境变量
└── .env.production          # 生产环境变量
```

### 技术栈
- **React 18** - 现代UI框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Ant Design** - UI组件库
- **Context API** - 状态管理
- **Fetch API + ReadableStream** - SSE流式处理

### 开发命令
```bash
npm run dev      # 启动开发服务器（http://localhost:3000）
npm run build    # 生产构建
npm run preview  # 预览生产构建（http://localhost:4173）
npm run lint     # 代码检查
```

### API代理配置
开发环境通过Vite代理访问后端API（`vite.config.ts`）：
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

---

## 📦 生产构建

### 执行构建
```bash
# 1. 安装依赖（如果还没有）
npm install

# 2. 执行构建
npm run build

# 3. 预览构建结果（可选）
npm run preview
```

### 构建产物
构建完成后，所有静态文件将生成在 `dist/` 目录：
```
dist/
├── index.html          # 入口HTML
├── assets/             # 静态资源
│   ├── index-xxx.js    # 打包后的JS
│   ├── index-xxx.css   # 打包后的CSS
│   └── ...
└── vite.svg            # 静态图标
```

---

## 🌐 部署方案

### 方案1：Nginx部署（推荐）

#### 1. 配置Nginx
创建配置文件 `/etc/nginx/sites-available/shuai-travel-agent`：
```nginx
server {
    listen 80;
    server_name yourdomain.com;  # 修改为您的域名
    
    # 前端静态文件
    location / {
        root /var/www/shuai-travel-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        add_header Cache-Control "public, max-age=31536000" always;
    }
    
    # API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        
        # SSE流式响应支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 禁用缓冲（SSE必需）
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

#### 2. 部署步骤
```bash
# 1. 上传构建产物到服务器
scp -r dist/ user@server:/var/www/shuai-travel-agent/frontend/

# 2. 启用Nginx配置
sudo ln -s /etc/nginx/sites-available/shuai-travel-agent /etc/nginx/sites-enabled/

# 3. 测试并重载Nginx
sudo nginx -t
sudo systemctl reload nginx

# 4. 启动后端API服务
cd /var/www/shuai-travel-agent
python run_api.py
```

---

### 方案2：FastAPI静态托管

#### 修改后端app.py
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# ... 其他API路由 ...

# 托管前端静态文件
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # API路由不受影响
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        
        # 其他路由返回index.html（SPA路由）
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
```

#### 部署步骤
```bash
# 1. 构建前端
npm run build

# 2. 启动FastAPI服务（会自动托管前端）
python run_api.py

# 访问：http://localhost:8000
```

---

### 方案3：Vercel部署（前端）

#### 1. 准备配置文件
在 `frontend/` 目录创建 `vercel.json`：
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-backend-api.com/api/$1" },
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

#### 2. 部署
```bash
# 1. 安装Vercel CLI
npm install -g vercel

# 2. 登录
vercel login

# 3. 部署
cd frontend
vercel --prod
```

---

## ❓ 常见问题

### Q1: TypeScript编译错误
**问题**：运行时出现 `Cannot find module 'react'` 等错误

**解决**：
```bash
# 删除依赖并重新安装
rm -rf node_modules package-lock.json
npm install
```

---

### Q2: API请求失败（CORS错误）
**问题**：前端无法访问后端API

**解决**：
1. 确保后端已配置CORS（`app.py`已添加）
2. 检查后端服务是否运行在 `http://localhost:8000`
3. 开发环境使用Vite代理，生产环境需配置Nginx代理

---

### Q3: 流式响应不工作
**问题**：AI回复不是逐字显示

**解决**：
1. 检查后端 `/api/chat/stream` 端点是否正常
2. 检查网络代理是否禁用了流式传输
3. Nginx配置需添加 `proxy_buffering off`

---

### Q4: 构建体积过大
**问题**：`dist/` 目录体积超过预期

**优化**：
```bash
# 1. 分析构建体积
npm run build -- --mode production

# 2. 查看依赖树
npm list --depth=0

# 3. 移除未使用的依赖
npm prune
```

---

### Q5: 生产环境白屏
**问题**：部署后页面空白

**排查**：
1. 检查浏览器控制台错误
2. 确认静态资源路径正确
3. 检查Nginx/FastAPI路由配置
4. 确认 `index.html` 可访问

---

## 📞 技术支持

如有问题，请检查：
1. **后端日志**：`python run_api.py` 输出
2. **前端控制台**：浏览器开发者工具
3. **网络请求**：浏览器Network标签
4. **配置文件**：`config/config.json`

---

## 📝 更新日志

### v1.0.0 (2024-12-25)
- ✅ 初始版本发布
- ✅ React 18 + TypeScript架构
- ✅ SSE流式响应支持
- ✅ 停止控制功能
- ✅ 会话管理
- ✅ Ant Design UI
