"""
API路由模块
"""
from .chat import router as chat_router
from .config import router as config_router
from .health import router as health_router

__all__ = ['chat_router', 'config_router', 'health_router']

