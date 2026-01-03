"""
================================================================================
gRPC Agent 服务器启动脚本 - ShuaiTravelAgent Agent Service
================================================================================

本脚本用于启动旅游规划 Agent 的 gRPC 服务。

功能说明:
    - 初始化配置管理器，加载 LLM 模型配置
    - 启动 gRPC 服务器，监听指定端口
    - 提供 ProcessMessage 和 StreamMessage 接口

使用场景:
    - 独立启动 Agent 服务供其他模块调用
    - 作为后台服务运行，通过 gRPC 与 Web 模块通信

启动方式:
    python run_agent.py

默认配置:
    - 端口: 50051
    - 配置文件: config/llm_config.yaml

输出示例:
    [*] Starting Agent gRPC Service...
       Config: d:\...\config\llm_config.yaml
       Port: 50051
       Default Model: gpt-4o-mini

    [OK] Agent gRPC Service started on port 50051
       Press Ctrl+C to stop

停止方式:
    Ctrl+C (Windows/Linux)
    Command+. (macOS)

注意事项:
    - 需先启动本服务，再启动 Web API
    - 确保配置文件 config/llm_config.yaml 存在
    - 确保 LLM API 密钥已正确配置
"""

import sys
import os

# =============================================================================
# 初始化项目路径
# =============================================================================

# 获取项目根目录
# __file__ 是当前脚本的路径
# os.path.abspath(__file__) 获取绝对路径
# os.path.dirname() 获取目录部分
project_root = os.path.dirname(os.path.abspath(__file__))

# 切换工作目录到项目根目录
# 确保所有相对路径引用都基于项目根目录
os.chdir(project_root)

# 将 agent 目录添加到 Python 路径
# 这样可以使用相对导入，如 from src.server import serve
agent_path = os.path.join(project_root, 'agent')
if agent_path not in sys.path:
    sys.path.insert(0, agent_path)

# =============================================================================
# 导入服务模块
# =============================================================================

try:
    # 从 agent 模块导入服务器启动函数和配置管理器
    # serve(): gRPC 服务器启动函数
    # ConfigManager: 配置管理类，用于加载 LLM 配置
    from src.server import serve
    from src.config.config_manager import ConfigManager

except ImportError as e:
    """
    导入失败处理
    可能原因:
        - 未在项目根目录运行
        - Python 路径配置错误
        - 依赖模块未安装
    """
    print("\n[X] 导入错误: " + str(e))
    print("\n请从项目根目录运行: " + project_root)
    print("Python 路径: " + str(sys.path) + "\n")
    sys.exit(1)


# =============================================================================
# 主程序入口
# =============================================================================

if __name__ == "__main__":
    """
    程序入口点

    执行流程:
        1. 加载配置文件
        2. 获取 gRPC 端口配置
        3. 启动 gRPC 服务器
        4. 等待服务器终止
    """
    try:
        # ==========================================================================
        # 1. 加载配置文件
        # ==========================================================================

        # 配置文件路径：项目根目录下的 config/llm_config.yaml
        config_path = os.path.join(project_root, 'config', 'llm_config.yaml')

        # 创建配置管理器实例
        # ConfigManager 负责解析 YAML 配置文件
        # 包含 LLM 模型配置、API 密钥、gRPC 设置等
        config_manager = ConfigManager(config_path)

        # ==========================================================================
        # 2. 获取 gRPC 端口配置
        # ==========================================================================

        # 从配置中获取 gRPC 端口
        # 默认端口为 50051
        port = config_manager.grpc_config.get('port', 50051)

        # ==========================================================================
        # 3. 启动 gRPC 服务器
        # ==========================================================================

        # 打印启动信息
        print("\n[*] 正在启动 Agent gRPC 服务...")
        print("   配置文件: " + config_path)
        print("   监听端口: " + str(port))
        print("   默认模型: " + config_manager.get_default_model_id())
        print()

        # 调用 serve() 函数启动 gRPC 服务器
        # 参数:
        #     config_path: str 配置文件路径
        #     port: int 监听端口
        # 返回:
        #     grpc.Server gRPC 服务器实例
        server = serve(config_path=config_path, port=port)

        # ==========================================================================
        # 4. 等待服务器运行
        # ==========================================================================

        print("\n[✓] Agent gRPC 服务已启动，监听端口 " + str(port))
        print("   按 Ctrl+C 停止服务\n")

        # wait_for_termination() 阻塞主线程
        # 等待终止信号（Ctrl+C）或服务器内部停止
        server.wait_for_termination()

    except FileNotFoundError as e:
        """
        配置文件未找到错误处理
        """
        print("\n[X] 配置文件错误:\n" + str(e) + "\n")
        sys.exit(1)

    except Exception as e:
        """
        其他启动错误处理
        可能原因:
            - 端口已被占用
            - LLM API 调用失败
            - 内存不足
        """
        print("\n[X] 启动错误: " + str(e) + "\n")
        sys.exit(1)
