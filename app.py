"""
应用启动脚本 - 简易医疗Agent系统
"""
import uvicorn
import os


def main():
    """主函数 - 启动FastAPI应用"""
    # 确保数据目录存在
    os.makedirs("./data/qdrant_db", exist_ok=True)
    
    print("=" * 50)
    print("简易医疗Agent系统启动中...")
    print("访问地址: http://localhost:8000")
    print("=" * 50)
    
    # 启动应用
    uvicorn.run(
        "web.app:create_app",
        host="0.0.0.0",
        port=8000,
        factory=True  # 使用工厂模式
    )

if __name__ == "__main__":
    main()

