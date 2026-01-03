"""
ShuaiTravelAgent Web API Server - ShuaiTravelAgent Web API服务器

本模块是Web服务的入口点，使用FastAPI框架构建REST API。
提供聊天、对话管理、模型配置、城市信息等API接口。

功能特点:
- RESTful API设计
- SSE流式响应支持
- CORS跨域支持
- 依赖注入容器
- gRPC客户端集成

启动方式:
    # 方式1: 直接运行
    python main.py --host 0.0.0.0 --port 8000 --debug

    # 方式2: 使用uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

API端点:
    GET  /                       - API信息
    GET  /api/health             - 健康检查
    POST /api/chat/stream        - SSE流式聊天
    GET  /api/sessions           - 获取会话列表
    GET  /api/sessions/{id}      - 获取会话详情
    GET  /api/models             - 获取可用模型
    GET  /api/cities             - 获取城市列表
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import chat_router, session_router, model_router, city_router, health_router
from src.routes.model import set_config_manager


def create_app() -> FastAPI:
    """
    创建并配置FastAPI应用

    初始化所有中间件、配置、服务和路由。

    Returns:
        FastAPI: 配置完成的FastAPI应用实例

    初始化流程:
        1. 创建FastAPI实例
        2. 配置CORS中间件
        3. 加载配置管理器
        4. 初始化依赖注入容器
        5. 注册路由
        6. 初始化gRPC客户端
    """
    app = FastAPI(
        title="ShuaiTravelAgent API",
        description="AI Travel Assistant API with SSE streaming support",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware - 生产环境应该限制为实际的前端域名
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Initialize ConfigManager and pass to routes
    try:
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(project_root, 'config', 'llm_config.yaml')

        from src.config.config_manager import ConfigManager
        config_manager = ConfigManager(config_path)
        print(f"[*] Config loaded from: {config_path}")

        # Pass config manager to model router
        set_config_manager(config_manager)

        # Also pass to other routes that need it
        if hasattr(chat_router, 'set_config_manager'):
            chat_router.set_config_manager(config_manager)

    except Exception as e:
        print(f"[!] Warning: Could not load config: {e}")

    # Initialize dependency injection container
    from src.dependencies.container import get_container
    get_container()
    print("[*] Dependency container initialized")

    # Include routers
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(session_router, prefix="/api", tags=["session"])
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    app.include_router(model_router, prefix="/api", tags=["model"])
    app.include_router(city_router, prefix="/api", tags=["city"])

    # Initialize gRPC stub for chat service
    try:
        from src.routes.chat import init_grpc_stub
        init_grpc_stub()
        print("[*] gRPC client initialized")
    except Exception as e:
        print(f"[!] Warning: Could not initialize gRPC client: {e}")

    @app.get("/")
    async def root():
        """根端点 - 返回API基本信息"""
        return {
            "name": "ShuaiTravelAgent API",
            "version": "1.0.0",
            "docs": "/docs"
        }

    return app


# Create app instance
app = create_app()


def main(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """
    启动Web服务器

    Args:
        host: str 监听地址，默认"0.0.0.0"
        port: int 监听端口，默认8000
        debug: bool 是否开启调试模式，默认False
    """
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='ShuaiTravelAgent Web Server')
    parser.add_argument("--host", default="0.0.0.0", help="服务器监听地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器监听端口")
    parser.add_argument("--debug", action="store_true", help="开启调试模式")

    args = parser.parse_args()

    main(args.host, args.port, args.debug)
