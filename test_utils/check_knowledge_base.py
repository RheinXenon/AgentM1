"""
知识库检查工具 - 检查RAG知识库的状态
"""
import os
from qdrant_client import QdrantClient

def check_knowledge_base():
    """检查知识库状态"""
    print("\n" + "=" * 60)
    print("🔍 检查RAG知识库状态...")
    print("=" * 60 + "\n")
    
    # 获取项目根目录（相对于脚本所在位置）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.join(project_root, "data", "qdrant_db")
    collection_name = "medical_knowledge"
    
    # 检查数据库文件夹是否存在
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件夹不存在: {db_path}")
        print("\n💡 解决方案:")
        print("   1. 运行系统会自动创建数据库")
        print("   2. 或手动创建文件夹: mkdir -p data/qdrant_db")
        return False
    
    print(f"✅ 数据库文件夹存在: {db_path}")
    
    try:
        # 连接数据库
        client = QdrantClient(path=db_path)
        print("✅ 成功连接到数据库\n")
        
        # 获取所有集合
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        print(f"📚 数据库中的集合: {collection_names}")
        
        # 检查目标集合
        if collection_name not in collection_names:
            print(f"\n⚠️  集合 '{collection_name}' 不存在")
            print("\n💡 解决方案:")
            print("   运行以下命令导入数据:")
            print("   python ingest_data.py")
            return False
        
        print(f"✅ 集合 '{collection_name}' 存在\n")
        
        # 获取集合信息
        collection_info = client.get_collection(collection_name)
        points_count = collection_info.points_count
        
        print("📊 集合详细信息:")
        print(f"  - 向量数量: {points_count}")
        print(f"  - 向量维度: {collection_info.config.params.vectors.size}")
        print(f"  - 距离度量: {collection_info.config.params.vectors.distance}")
        
        if points_count == 0:
            print("\n⚠️  知识库是空的（没有任何文档）")
            print("\n💡 解决方案:")
            print("   1. 确保 ./text/ 文件夹中有文档文件")
            print("   2. 运行: python ingest_data.py")
            print("\n支持的文件格式:")
            print("   - .txt 文本文件")
            print("   - .pdf PDF文件")
            return False
        else:
            print(f"\n✅ 知识库包含 {points_count} 个向量")
            
            # 尝试查询测试
            print("\n🧪 测试查询功能...")
            try:
                results = client.search(
                    collection_name=collection_name,
                    query_vector=[0.1] * collection_info.config.params.vectors.size,
                    limit=1
                )
                if results:
                    print("✅ 查询功能正常")
                    print(f"   示例文档片段: {results[0].payload.get('page_content', '')[:100]}...")
                else:
                    print("⚠️  查询返回空结果")
            except Exception as e:
                print(f"⚠️  查询测试失败: {e}")
        
        return points_count > 0
        
    except RuntimeError as e:
        if "already accessed" in str(e):
            print("\n❌ 数据库被锁定！")
            print("\n💡 可能的原因:")
            print("   - app.py 正在运行")
            print("   - 其他进程正在访问数据库")
            print("\n解决方案:")
            print("   1. 停止所有正在运行的 Python 进程")
            print("   2. 或者等待当前进程结束")
            print("   3. 如果问题持续，重启电脑")
        else:
            print(f"\n❌ 数据库错误: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    result = check_knowledge_base()
    
    print("\n" + "=" * 60)
    if result:
        print("🎉 知识库状态正常，可以正常使用RAG功能")
    else:
        print("⚠️  知识库存在问题，请按照上面的提示解决")
    print("=" * 60 + "\n")
    
    # 显示快速操作指南
    print("📖 快速操作指南:")
    print("\n1. 导入数据到知识库:")
    print("   python ingest_data.py")
    print("\n2. 检查知识库状态:")
    print("   python test_utils/check_knowledge_base.py")
    print("\n3. 启动系统:")
    print("   python app.py")
    print("\n4. 测试系统:")
    print("   python test_utils/test_system.py")
    print()

if __name__ == "__main__":
    main()

