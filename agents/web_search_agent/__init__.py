"""
网络搜索智能体 - 搜索最新医学研究信息
"""
from typing import Dict, List
from langchain.prompts import PromptTemplate
from duckduckgo_search import DDGS
from config import WebSearchConfig
import re

class WebSearchAgent:
    """网络搜索智能体"""
    
    def __init__(self):
        self.config = WebSearchConfig()
        self.llm = self.config.llm
        
        # 搜索响应生成提示词
        self.response_prompt = PromptTemplate(
            input_variables=["query", "search_results", "conversation_history"],
            template="""你是一个医疗信息搜索助手。基于网络搜索结果回答用户的医学问题。

重要规则:
1. 综合搜索结果提供准确信息
2. 引用来源网站
3. 区分已验证信息和新研究
4. 提醒用户验证信息真实性
5. 始终建议咨询专业医生

对话历史:
{conversation_history}

网络搜索结果:
{search_results}

用户问题: {query}

请基于搜索结果提供详细回答:"""
        )
    
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
            # 优化搜索查询 - 添加医学相关关键词
            medical_query = f"医学 医疗 {query}"
            
            # 使用DuckDuckGo搜索
            with DDGS() as ddgs:
                search_results = list(ddgs.text(
                    medical_query,
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
            
            return {
                "agent": "网络搜索智能体",
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

