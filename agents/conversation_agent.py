"""
对话智能体 - 处理一般性咨询对话
"""
from typing import Dict, List
from langchain_core.prompts import PromptTemplate
from config import ConversationConfig

class ConversationAgent:
    """对话智能体"""
    
    def __init__(self, config_manager=None):
        self.config = ConversationConfig()
        self.llm = self.config.llm
        self.config_manager = config_manager
        
        # 从配置管理器加载提示词模板
        self.update_prompt()
    
    def update_prompt(self):
        """更新提示词模板"""
        template = self.config_manager.get_prompt("conversation") if self.config_manager else self._get_default_template()
        self.conversation_prompt = PromptTemplate(
            input_variables=["query", "conversation_history"],
            template=template
        )
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """你是一个专业且友好的智能助手。你的任务是回答用户的问题。

重要指导原则:
1. 提供准确、有用的建议
2. 使用通俗易懂的语言
3. 保持专业但友善的语气
4. 根据上下文提供相关信息

对话历史:
{conversation_history}

用户: {query}

助手:"""
    
    def chat(self, query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        处理对话请求
        
        Args:
            query: 用户查询
            conversation_history: 对话历史
            
        Returns:
            response_dict: 包含回答的字典
        """
        try:
            # 格式化对话历史
            history_text = ""
            if conversation_history:
                recent_history = conversation_history[-self.config.context_limit:]
                for msg in recent_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "user":
                        history_text += f"用户: {content}\n"
                    elif role == "assistant":
                        history_text += f"医疗助手: {content}\n"
            
            # 生成响应
            prompt = self.conversation_prompt.format(
                query=query,
                conversation_history=history_text if history_text else "这是对话的开始"
            )
            
            response = self.llm.invoke(prompt)
            
            agent_name = self.config_manager.get_config("system_name") if self.config_manager else "对话智能体"
            return {
                "agent": agent_name,
                "response": response.content
            }
            
        except Exception as e:
            print(f"对话处理出错: {e}")
            agent_name = self.config_manager.get_config("system_name") if self.config_manager else "对话智能体"
            return {
                "agent": agent_name,
                "response": "抱歉,处理您的请求时出现错误。请稍后重试。"
            }
    
    def get_health_tips(self) -> str:
        """返回通用健康建议"""
        tips = """
        通用健康建议:
        1. 保持均衡饮食,多吃蔬菜水果
        2. 每天适量运动,至少30分钟
        3. 保证充足睡眠,成人每天7-9小时
        4. 定期体检,及早发现健康问题
        5. 保持良好心态,适当释放压力
        6. 戒烟限酒,培养健康生活习惯
        7. 注意个人卫生,预防传染病
        8. 有症状及时就医,不要讳疾忌医
        """
        return tips

