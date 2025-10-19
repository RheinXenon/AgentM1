"""
网络搜索智能体 - 搜索最新医学研究信息
"""
from typing import Dict, List
from langchain_core.prompts import PromptTemplate
from duckduckgo_search import DDGS
from config import WebSearchConfig
import re

class WebSearchAgent:
    """网络搜索智能体"""
    
    def __init__(self, config_manager=None):
        self.config = WebSearchConfig()
        self.llm = self.config.llm
        self.config_manager = config_manager
        
        # 从配置管理器加载提示词模板
        self.update_prompt()
    
    def update_prompt(self):
        """更新提示词模板"""
        template = self.config_manager.get_prompt("websearch") if self.config_manager else self._get_default_template()
        self.response_prompt = PromptTemplate(
            input_variables=["query", "search_results", "conversation_history"],
            template=template
        )
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """你是一个智能助手。请根据以下搜索结果回答用户的问题。

搜索结果:
{search_results}

对话历史:
{conversation_history}

用户问题: {query}

请综合搜索结果,给出准确、有用的回答。

你的回答:"""
    
    def search(self, query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        执行网络搜索并生成响应
        
        Args:
            query: 搜索查询
            conversation_history: 对话历史
            
        Returns:
            response_dict: 包含回答和搜索结果的字典
        """
        try:
            # 直接使用用户的查询
            search_query = query
            
            # 使用DuckDuckGo搜索
            with DDGS() as ddgs:
                search_results = list(ddgs.text(
                    search_query,
                    max_results=self.config.max_results
                ))
            
            if not search_results:
                return {
                    "agent": "网络搜索智能体",
                    "response": "抱歉,没有找到相关的搜索结果。请尝试重新表述您的问题。",
                    "sources": []
                }
            
            # 格式化搜索结果
            formatted_results = ""
            sources = []
            for idx, result in enumerate(search_results, 1):
                title = result.get('title', '无标题')
                body = result.get('body', '无内容')
                link = result.get('href', '')
                
                formatted_results += f"\n[结果{idx}]\n标题: {title}\n内容: {body}\n链接: {link}\n"
                
                sources.append({
                    "title": title,
                    "snippet": body[:200] + "...",
                    "url": link
                })
            
            # 格式化对话历史
            history_text = ""
            if conversation_history:
                recent_history = conversation_history[-4:]
                for msg in recent_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    history_text += f"{role}: {content}\n"
            
            # 生成响应
            prompt = self.response_prompt.format(
                query=query,
                search_results=formatted_results,
                conversation_history=history_text if history_text else "无"
            )
            
            response = self.llm.invoke(prompt)
            
            agent_name = self.config_manager.get_config("system_name") if self.config_manager else "网络搜索智能体"
            return {
                "agent": agent_name,
                "response": response.content,
                "sources": sources
            }
            
        except Exception as e:
            print(f"网络搜索出错: {e}")
            return {
                "agent": "网络搜索智能体",
                "response": f"搜索时出错: {str(e)}。请稍后重试。",
                "sources": []
            }
    
    def is_medical_query(self, query: str) -> bool:
        """判断是否为医学相关查询"""
        medical_keywords = [
            '疾病', '症状', '治疗', '药物', '诊断', '医院', '医生',
            '健康', '病', '痛', '不适', '检查', '手术', '康复'
        ]
        return any(keyword in query for keyword in medical_keywords)

