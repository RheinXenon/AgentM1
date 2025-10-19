"""
RAG智能体 - 基于向量数据库的检索增强生成
"""
from typing import Dict, List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import RAGConfig
import os

class MedicalRAG:
    """RAG智能体"""
    
    def __init__(self, config_manager=None):
        self.config = RAGConfig()
        self.llm = self.config.llm
        self.embedding_model = self.config.embedding_model
        self.config_manager = config_manager
        
        # 初始化Qdrant客户端
        self._init_vector_db()
        
        # 从配置管理器加载提示词模板
        self.update_prompt()
    
    def update_prompt(self):
        """更新提示词模板"""
        template = self.config_manager.get_prompt("rag") if self.config_manager else self._get_default_template()
        self.response_prompt = PromptTemplate(
            input_variables=["query", "context", "conversation_history"],
            template=template
        )
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """你是一个专业的智能助手。请根据以下参考资料回答用户的问题。

参考资料:
{context}

对话历史:
{conversation_history}

用户问题: {query}

请基于提供的参考资料给出准确、专业的回答。如果参考资料中没有相关信息,请诚实地告知用户。

你的回答:"""
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            if self.config.use_local:
                # 使用本地Qdrant
                os.makedirs(self.config.vector_local_path, exist_ok=True)
                self.qdrant_client = QdrantClient(path=self.config.vector_local_path)
            else:
                # 使用云端Qdrant
                self.qdrant_client = QdrantClient(
                    url=os.getenv("QDRANT_URL"),
                    api_key=os.getenv("QDRANT_API_KEY")
                )
            
            # 检查collection是否存在,不存在则创建
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.config.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"创建新的collection: {self.config.collection_name}")
            
            # 初始化vectorstore
            self.vectorstore = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=self.config.collection_name,
                embedding=self.embedding_model
            )
            
        except Exception as e:
            print(f"初始化向量数据库失败: {e}")
            self.vectorstore = None
    
    def query(self, query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        处理RAG查询
        
        Args:
            query: 用户查询
            conversation_history: 对话历史
            
        Returns:
            response_dict: 包含回答和元数据的字典
        """
        try:
            # 检查vectorstore是否可用
            if self.vectorstore is None:
                return {
                    "agent": "RAG智能体",
                    "response": "知识库暂时不可用。这可能是因为知识库还未初始化。请联系管理员添加医学文档到知识库中。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 检索相关文档
            retrieved_docs = self.vectorstore.similarity_search_with_score(
                query,
                k=self.config.top_k
            )
            
            # 检查检索置信度
            # 注意: Qdrant使用余弦距离，分数越小表示越相似（0=完全相同，2=完全相反）
            # 所以这里检查分数是否大于阈值（距离太远）
            if not retrieved_docs or retrieved_docs[0][1] > self.config.min_retrieval_confidence:
                return {
                    "agent": "RAG智能体",
                    "response": "抱歉,我在知识库中没有找到足够可靠的相关信息来回答您的问题。建议咨询专业医生或尝试使用网络搜索功能。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 构建上下文
            context = "\n\n".join([doc[0].page_content for doc in retrieved_docs[:self.config.reranker_top_k]])
            
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
                context=context,
                conversation_history=history_text if history_text else "无"
            )
            
            response = self.llm.invoke(prompt)
            
            # 提取来源信息
            sources = []
            if self.config.include_sources:
                for doc, score in retrieved_docs[:self.config.reranker_top_k]:
                    source_info = {
                        "content": doc.page_content[:200] + "...",
                        "score": float(score),
                        "metadata": doc.metadata
                    }
                    sources.append(source_info)
            
            return {
                "agent": "RAG智能体",
                "response": response.content,
                "sources": sources,
                "confidence": float(retrieved_docs[0][1])
            }
            
        except Exception as e:
            print(f"RAG查询出错: {e}")
            return {
                "agent": "RAG智能体",
                "response": f"处理查询时出错: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """添加文档到知识库"""
        try:
            if self.vectorstore:
                self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
                return True
            return False
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False

