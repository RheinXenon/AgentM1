"""
配置文件 - 管理所有API密钥和系统配置
"""
import os
from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# 加载环境变量
load_dotenv()

class AgentDecisionConfig:
    """Agent决策配置"""
    def __init__(self):
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus")
        self.llm = ChatTongyi(
            model=self.model_name,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=0.1,  # 低温度以确保决策准确性
            top_p=0.8
        )

class ConversationConfig:
    """对话配置"""
    def __init__(self):
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus")
        self.llm = ChatTongyi(
            model=self.model_name,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=0.7,  # 适度创造性
            top_p=0.8
        )
        self.context_limit = 20  # 保留最近20条消息

class WebSearchConfig:
    """网络搜索配置"""
    def __init__(self):
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus")
        self.llm = ChatTongyi(
            model=self.model_name,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=0.3,
            top_p=0.8
        )
        self.max_results = 5  # 最多搜索结果数

class RAGConfig:
    """RAG系统配置"""
    def __init__(self):
        # 向量数据库配置
        self.vector_db_type = "qdrant"
        self.embedding_dim = 1536  # DashScope text-embedding-v2 的维度
        self.distance_metric = "Cosine"
        self.use_local = os.getenv("QDRANT_USE_LOCAL", "true").lower() == "true"
        self.vector_local_path = os.getenv("QDRANT_LOCAL_PATH", "./data/qdrant_db")
        
        # 多知识库配置 - 每个文件夹对应一个知识库
        self.knowledge_bases = {
            "医疗知识库": {
                "collection_name": "medical_knowledge",
                "description": "医疗、健康、疾病相关的专业知识"
            },
            "商业知识库": {
                "collection_name": "business_knowledge", 
                "description": "商业、金融、管理相关的专业知识"
            }
        }
        
        # 默认知识库（为了兼容旧代码）
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "medical_knowledge")
        
        # 文本分块配置
        self.chunk_size = 512
        self.chunk_overlap = 50
        
        # Embedding模型 - 使用阿里云百炼平台的文本向量模型
        self.embedding_model = DashScopeEmbeddings(
            model=os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v2"),
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        
        # LLM模型
        self.model_name = os.getenv("DASHSCOPE_MODEL_NAME", "qwen-plus")
        self.llm = ChatTongyi(
            model=self.model_name,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=0.3,
            top_p=0.8
        )
        
        # 检索配置
        self.top_k = 5  # 检索结果数量
        self.min_retrieval_confidence = 1.0  # 最大距离阈值（余弦距离，越小越相似，0-2范围）
        self.reranker_top_k = 3  # 重排序后保留数量
        self.include_sources = True  # 是否包含来源
        self.context_limit = 20

