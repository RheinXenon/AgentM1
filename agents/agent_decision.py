"""
智能体决策系统 - 根据用户查询路由到合适的Agent
"""
from typing import Dict, List
from langchain.prompts import PromptTemplate
from config import AgentDecisionConfig

class AgentDecision:
    """智能体决策类 - 决定使用哪个Agent处理用户请求"""
    
    def __init__(self):
        self.config = AgentDecisionConfig()
        self.llm = self.config.llm
        
        # 决策提示词模板
        self.decision_prompt = PromptTemplate(
            input_variables=["query", "conversation_history"],
            template="""你是一个医疗智能助手的决策系统。根据用户的查询内容,判断应该使用哪个智能体来处理。

可用的智能体:
1. RAG智能体 - 从医学知识库检索信息,适用于:
   - 疾病症状、诊断和治疗的常规问题
   - 医学术语解释
   - 已知医学知识查询
   
2. 网络搜索智能体 - 搜索最新医学研究和信息,适用于:
   - 最新医学研究进展
   - 新药物或新疗法
   - 需要最新数据的问题
   
3. 对话智能体 - 进行一般性医疗咨询对话,适用于:
   - 简单的健康咨询
   - 生活方式建议
   - 不需要专业知识库的问题

对话历史:
{conversation_history}

用户查询: {query}

请分析查询内容,只回答以下选项之一: "RAG" 或 "WEBSEARCH" 或 "CONVERSATION"

你的决策:"""
        )
    
    def decide(self, query: str, conversation_history: List[Dict] = None) -> str:
        """
        决定使用哪个Agent
        
        Args:
            query: 用户查询
            conversation_history: 对话历史
            
        Returns:
            agent_type: "RAG", "WEBSEARCH", 或 "CONVERSATION"
        """
        # 格式化对话历史
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-4:]  # 只看最近4条
            for msg in recent_history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"
        
        # 调用LLM进行决策
        prompt = self.decision_prompt.format(
            query=query,
            conversation_history=history_text if history_text else "无"
        )
        
        try:
            response = self.llm.invoke(prompt)
            decision = response.content.strip().upper()
            
            # 验证决策结果
            if "RAG" in decision:
                return "RAG"
            elif "WEBSEARCH" in decision:
                return "WEBSEARCH"
            else:
                return "CONVERSATION"
                
        except Exception as e:
            print(f"决策出错: {e}")
            return "CONVERSATION"  # 默认返回对话Agent
    
    def get_agent_info(self) -> Dict[str, str]:
        """返回各Agent的信息"""
        return {
            "RAG": "医学知识库检索智能体",
            "WEBSEARCH": "网络搜索智能体",
            "CONVERSATION": "医疗对话智能体"
        }

