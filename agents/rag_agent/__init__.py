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
    """RAG智能体 - 支持多知识库"""
    
    def __init__(self, config_manager=None):
        self.config = RAGConfig()
        self.llm = self.config.llm
        self.embedding_model = self.config.embedding_model
        self.config_manager = config_manager
        
        # 初始化Qdrant客户端和所有知识库
        self._init_vector_db()
        
        # 存储每个知识库的vectorstore
        self.vectorstores = {}
        self._init_all_collections()
        
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
        """初始化向量数据库客户端"""
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
        except Exception as e:
            print(f"初始化向量数据库客户端失败: {e}")
            self.qdrant_client = None
    
    def _init_all_collections(self):
        """初始化所有知识库的collection"""
        if not self.qdrant_client:
            print("❌ Qdrant客户端未初始化")
            return
        
        try:
            # 获取现有的collections
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            # 为每个知识库创建collection和vectorstore
            for kb_name, kb_config in self.config.knowledge_bases.items():
                collection_name = kb_config["collection_name"]
                
                # 如果collection不存在则创建
                if collection_name not in collection_names:
                    self.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.config.embedding_dim,
                            distance=Distance.COSINE
                        )
                    )
                    print(f"✅ 创建新的知识库: {kb_name} (collection: {collection_name})")
                
                # 初始化vectorstore
                self.vectorstores[kb_name] = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=collection_name,
                    embedding=self.embedding_model
                )
            
            # 保留默认vectorstore以兼容旧代码
            if "医疗知识库" in self.vectorstores:
                self.vectorstore = self.vectorstores["医疗知识库"]
            elif self.vectorstores:
                self.vectorstore = list(self.vectorstores.values())[0]
            else:
                self.vectorstore = None
            
            print(f"📚 已初始化 {len(self.vectorstores)} 个知识库")
            
        except Exception as e:
            print(f"初始化知识库collections失败: {e}")
            self.vectorstore = None
    
    def query(self, query: str, conversation_history: List[Dict] = None, 
              knowledge_bases: List[str] = None) -> Dict:
        """
        处理RAG查询 - 支持多知识库检索
        
        Args:
            query: 用户查询
            conversation_history: 对话历史
            knowledge_bases: 要检索的知识库列表，None表示检索所有知识库
            
        Returns:
            response_dict: 包含回答和元数据的字典
        """
        try:
            # 检查是否有可用的知识库
            if not self.vectorstores:
                return {
                    "agent": "RAG智能体",
                    "response": "知识库暂时不可用。这可能是因为知识库还未初始化。请联系管理员添加文档到知识库中。",
                    "sources": [],
                    "confidence": 0.0,
                    "knowledge_bases_used": []
                }
            
            # 确定要检索的知识库
            if knowledge_bases is None:
                # 检索所有知识库
                search_kbs = list(self.vectorstores.keys())
            else:
                # 检索指定的知识库
                search_kbs = [kb for kb in knowledge_bases if kb in self.vectorstores]
            
            if not search_kbs:
                return {
                    "agent": "RAG智能体",
                    "response": "指定的知识库不存在。",
                    "sources": [],
                    "confidence": 0.0,
                    "knowledge_bases_used": []
                }
            
            # 从所有指定的知识库中检索文档
            all_retrieved_docs = []
            for kb_name in search_kbs:
                vectorstore = self.vectorstores[kb_name]
                docs = vectorstore.similarity_search_with_score(
                    query,
                    k=self.config.top_k
                )
                # 添加知识库来源信息
                for doc, score in docs:
                    doc.metadata["knowledge_base"] = kb_name
                    all_retrieved_docs.append((doc, score))
            
            # 按相似度排序（分数越小越相似）
            all_retrieved_docs.sort(key=lambda x: x[1])
            
            # 检查检索置信度
            if not all_retrieved_docs or all_retrieved_docs[0][1] > self.config.min_retrieval_confidence:
                return {
                    "agent": "RAG智能体",
                    "response": "抱歉,我在知识库中没有找到足够可靠的相关信息来回答您的问题。建议尝试使用网络搜索功能。",
                    "sources": [],
                    "confidence": 0.0,
                    "knowledge_bases_used": search_kbs
                }
            
            # 构建上下文（取前N个最相关的）
            top_docs = all_retrieved_docs[:self.config.reranker_top_k]
            context = "\n\n".join([doc[0].page_content for doc in top_docs])
            
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
                for doc, score in top_docs:
                    source_info = {
                        "content": doc.page_content[:200] + "...",
                        "score": float(score),
                        "metadata": doc.metadata,
                        "knowledge_base": doc.metadata.get("knowledge_base", "未知")
                    }
                    sources.append(source_info)
            
            return {
                "agent": "RAG智能体",
                "response": response.content,
                "sources": sources,
                "confidence": float(all_retrieved_docs[0][1]),
                "knowledge_bases_used": search_kbs
            }
            
        except Exception as e:
            print(f"RAG查询出错: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent": "RAG智能体",
                "response": f"处理查询时出错: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "knowledge_bases_used": []
            }
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None, 
                      knowledge_base: str = None):
        """
        添加文档到知识库
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            knowledge_base: 要添加到的知识库名称，None表示添加到默认知识库
        """
        try:
            # 确定目标知识库
            if knowledge_base and knowledge_base in self.vectorstores:
                vectorstore = self.vectorstores[knowledge_base]
                print(f"向知识库 '{knowledge_base}' 添加文档...")
            elif self.vectorstore:
                vectorstore = self.vectorstore
                knowledge_base = "默认知识库"
            else:
                print("❌ 没有可用的知识库")
                return False
            
            # 添加知识库信息到元数据
            if metadatas:
                for metadata in metadatas:
                    metadata["knowledge_base"] = knowledge_base
            else:
                metadatas = [{"knowledge_base": knowledge_base} for _ in texts]
            
            vectorstore.add_texts(texts=texts, metadatas=metadatas)
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_knowledge_bases(self) -> Dict[str, str]:
        """获取所有知识库的信息"""
        return {
            kb_name: self.config.knowledge_bases[kb_name]["description"]
            for kb_name in self.vectorstores.keys()
            if kb_name in self.config.knowledge_bases
        }
    
    def get_knowledge_base_stats(self, knowledge_base: str = None) -> Dict:
        """
        获取知识库的统计信息
        
        Args:
            knowledge_base: 知识库名称，None表示获取所有知识库的统计
        """
        try:
            if knowledge_base:
                # 获取单个知识库的统计
                if knowledge_base not in self.vectorstores:
                    return {"error": f"知识库 '{knowledge_base}' 不存在"}
                
                collection_name = self.config.knowledge_bases[knowledge_base]["collection_name"]
                collection_info = self.qdrant_client.get_collection(collection_name)
                
                return {
                    knowledge_base: {
                        "vectors_count": collection_info.vectors_count,
                        "collection_name": collection_name
                    }
                }
            else:
                # 获取所有知识库的统计
                stats = {}
                for kb_name in self.vectorstores.keys():
                    collection_name = self.config.knowledge_bases[kb_name]["collection_name"]
                    collection_info = self.qdrant_client.get_collection(collection_name)
                    stats[kb_name] = {
                        "vectors_count": collection_info.vectors_count,
                        "collection_name": collection_name,
                        "description": self.config.knowledge_bases[kb_name]["description"]
                    }
                return stats
        except Exception as e:
            print(f"获取知识库统计信息失败: {e}")
            return {"error": str(e)}

