"""
智能体决策系统 - 根据用户查询路由到合适的Agent
"""
from typing import Dict, List
from langchain_core.prompts import PromptTemplate
from config import AgentDecisionConfig

class AgentDecision:
    """智能体决策类 - 决定使用哪个Agent处理用户请求"""
    
    def __init__(self, config_manager=None):
        self.config = AgentDecisionConfig()
        self.llm = self.config.llm
        self.config_manager = config_manager
        
        # 从配置管理器加载提示词模板
        self.update_prompt()
    
    def update_prompt(self):
        """更新提示词模板"""
        template = self.config_manager.get_prompt("agent_decision") if self.config_manager else self._get_default_template()
        self.decision_prompt = PromptTemplate(
            input_variables=["query", "conversation_history"],
            template=template
        )
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """你是一个智能助手的决策系统。根据用户的查询内容,判断应该使用哪个智能体来处理。

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

你的决策:"""
    
    def _get_knowledge_base_decision_template(self) -> str:
        """获取知识库决策模板"""
        return """你是一个智能知识库路由系统。根据用户的查询内容,判断应该使用哪个知识库来检索信息。

可用的知识库:
{knowledge_bases}

用户查询: {query}

请分析查询内容,判断最适合的知识库。只需回答知识库的名称,如果需要搜索多个知识库,请用逗号分隔。

你的决策:"""
    
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
    
    def decide_knowledge_base(self, query: str, available_kbs: Dict[str, str]) -> List[str]:
        """
        决定使用哪个知识库
        
        Args:
            query: 用户查询
            available_kbs: 可用的知识库 {名称: 描述}
            
        Returns:
            知识库名称列表
        """
        if not available_kbs:
            return []
        
        # 构建知识库信息文本
        kb_info = ""
        for kb_name, description in available_kbs.items():
            kb_info += f"- {kb_name}: {description}\n"
        
        # 创建知识库决策提示词
        template = self._get_knowledge_base_decision_template()
        prompt = template.format(
            knowledge_bases=kb_info,
            query=query
        )
        
        try:
            response = self.llm.invoke(prompt)
            decision = response.content.strip()
            
            # 解析决策结果
            selected_kbs = []
            for kb_name in available_kbs.keys():
                if kb_name in decision:
                    selected_kbs.append(kb_name)
            
            # 如果没有匹配到任何知识库，返回所有知识库
            if not selected_kbs:
                selected_kbs = list(available_kbs.keys())
            
            return selected_kbs
                
        except Exception as e:
            print(f"知识库决策出错: {e}")
            # 默认返回所有知识库
            return list(available_kbs.keys())
    
    def get_agent_info(self) -> Dict[str, str]:
        """返回各Agent的信息"""
        return {
            "RAG": "医学知识库检索智能体",
            "WEBSEARCH": "网络搜索智能体",
            "CONVERSATION": "医疗对话智能体"
        }

