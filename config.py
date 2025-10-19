"""
配置文件 - 管理所有API密钥和系统配置
"""
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

# 加载环境变量
load_dotenv()

class AgentDecisionConfig:
    """Agent决策配置"""
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.1  # 低温度以确保决策准确性
        )

class ConversationConfig:
    """对话配置"""
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.7  # 适度创造性
        )
        self.context_limit = 20  # 保留最近20条消息

class WebSearchConfig:
    """网络搜索配置"""
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.3
        )
        self.max_results = 5  # 最多搜索结果数

class RAGConfig:
    """RAG系统配置"""
    def __init__(self):
        # 向量数据库配置
        self.vector_db_type = "qdrant"
        self.embedding_dim = 1536
        self.distance_metric = "Cosine"
        self.use_local = True  # 使用本地Qdrant
        self.vector_local_path = "./data/qdrant_db"
        self.collection_name = "medical_knowledge"
        
        # 文本分块配置
        self.chunk_size = 512
        self.chunk_overlap = 50
        
        # Embedding模型
        self.embedding_model = AzureOpenAIEmbeddings(
            deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
            model=os.getenv("AZURE_EMBEDDING_MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
            openai_api_version=os.getenv("AZURE_EMBEDDING_API_VERSION")
        )
        
        # LLM模型
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.3
        )
        
        # 检索配置
        self.top_k = 5  # 检索结果数量
        self.min_retrieval_confidence = 0.40  # 最小置信度阈值
        self.reranker_top_k = 3  # 重排序后保留数量
        self.include_sources = True  # 是否包含来源
        self.context_limit = 20

