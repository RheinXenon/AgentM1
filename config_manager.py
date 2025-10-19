"""
配置管理器 - 管理用户自定义的系统配置
"""
import json
import os
from typing import Dict, Any
from datetime import datetime

class ConfigManager:
    """配置管理器 - 处理用户自定义配置的保存和加载"""
    
    def __init__(self, config_file: str = "./data/user_config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self.config = self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # RAG设置
            "rag_enabled": True,
            
            # Agent决策提示词
            "agent_decision_prompt": """你是一个智能助手的决策系统。根据用户的查询内容,判断应该使用哪个智能体来处理。

可用的智能体:
1. RAG智能体 - 从知识库检索信息,适用于:
   - 需要专业知识的问题
   - 特定领域的查询
   - 已知知识库内容的问题
   
2. 网络搜索智能体 - 搜索最新信息,适用于:
   - 最新资讯和研究进展
   - 实时信息查询
   - 需要最新数据的问题
   
3. 对话智能体 - 进行一般性对话,适用于:
   - 简单的咨询
   - 不需要专业知识库的问题
   - 日常对话

对话历史:
{conversation_history}

用户查询: {query}

请分析查询内容,只回答以下选项之一: "RAG" 或 "WEBSEARCH" 或 "CONVERSATION"

你的决策:""",
            
            # 对话Agent提示词
            "conversation_prompt": """你是一个专业且友好的智能助手。你的任务是回答用户的问题。

重要指导原则:
1. 提供准确、有用的建议
2. 使用通俗易懂的语言
3. 保持专业但友善的语气
4. 根据上下文提供相关信息

对话历史:
{conversation_history}

用户: {query}

助手:""",
            
            # RAG Agent提示词
            "rag_prompt": """你是一个专业的智能助手。请根据以下参考资料回答用户的问题。

参考资料:
{context}

对话历史:
{conversation_history}

用户问题: {query}

请基于提供的参考资料给出准确、专业的回答。如果参考资料中没有相关信息,请诚实地告知用户。

你的回答:""",
            
            # Web搜索Agent提示词
            "websearch_prompt": """你是一个智能助手。请根据以下搜索结果回答用户的问题。

搜索结果:
{search_results}

对话历史:
{conversation_history}

用户问题: {query}

请综合搜索结果,给出准确、有用的回答。

你的回答:""",
            
            # 系统设置
            "system_name": "智能Agent系统",
            "welcome_message": "您好!我是您的智能助手。我可以回答各种问题,提供有用的信息和建议。请问有什么可以帮助您的?",
            
            # 更新时间
            "updated_at": datetime.now().isoformat()
        }
    
    def load_config(self) -> Dict[str, Any]:
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保新增字段存在
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.default_config.copy()
        else:
            # 首次运行，创建默认配置文件
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        # 更新时间戳
        config["updated_at"] = datetime.now().isoformat()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_config(self, key: str = None) -> Any:
        """获取配置项"""
        if key is None:
            return self.config
        return self.config.get(key)
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        self.config.update(updates)
        return self.save_config()
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config = self._get_default_config()
        return self.save_config()
    
    def is_rag_enabled(self) -> bool:
        """检查RAG是否启用"""
        return self.config.get("rag_enabled", True)
    
    def get_prompt(self, prompt_type: str) -> str:
        """获取指定类型的提示词"""
        prompt_key = f"{prompt_type}_prompt"
        return self.config.get(prompt_key, self.default_config.get(prompt_key, ""))

