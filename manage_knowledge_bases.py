"""
知识库管理工具 - 查看和管理多个知识库
"""
import argparse
from agents.rag_agent import MedicalRAG
from config_manager import ConfigManager

def list_knowledge_bases():
    """列出所有可用的知识库"""
    try:
        config_manager = ConfigManager()
        rag_agent = MedicalRAG(config_manager)
        
        print("\n" + "="*60)
        print("📚 可用的知识库列表")
        print("="*60 + "\n")
        
        kbs = rag_agent.get_all_knowledge_bases()
        
        if not kbs:
            print("⚠️  没有配置知识库")
            return
        
        for kb_name, description in kbs.items():
            print(f"📖 {kb_name}")
            print(f"   描述: {description}")
            print()
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ 获取知识库列表失败: {e}")

def show_knowledge_base_stats(kb_name=None):
    """显示知识库统计信息"""
    try:
        config_manager = ConfigManager()
        rag_agent = MedicalRAG(config_manager)
        
        print("\n" + "="*60)
        print("📊 知识库统计信息")
        print("="*60 + "\n")
        
        stats = rag_agent.get_knowledge_base_stats(kb_name)
        
        if "error" in stats:
            print(f"❌ {stats['error']}")
            return
        
        for kb_name, info in stats.items():
            print(f"📖 {kb_name}")
            print(f"   Collection名称: {info['collection_name']}")
            print(f"   文档向量数: {info['vectors_count']}")
            if 'description' in info:
                print(f"   描述: {info['description']}")
            print()
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
        import traceback
        traceback.print_exc()

def search_knowledge_base(query, kb_name=None):
    """在指定知识库中搜索"""
    try:
        config_manager = ConfigManager()
        rag_agent = MedicalRAG(config_manager)
        
        print("\n" + "="*60)
        print(f"🔍 搜索查询: {query}")
        if kb_name:
            print(f"📖 目标知识库: {kb_name}")
            kb_list = [kb_name]
        else:
            print("📖 搜索所有知识库")
            kb_list = None
        print("="*60 + "\n")
        
        result = rag_agent.query(query, knowledge_bases=kb_list)
        
        print(f"✨ 回答:\n{result['response']}\n")
        print(f"📊 置信度: {result['confidence']:.4f}")
        print(f"📚 使用的知识库: {', '.join(result['knowledge_bases_used'])}\n")
        
        if result['sources']:
            print("📄 相关来源:")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n  [{i}] 来源知识库: {source.get('knowledge_base', '未知')}")
                print(f"      相似度分数: {source['score']:.4f}")
                print(f"      内容片段: {source['content'][:150]}...")
                if 'metadata' in source:
                    metadata = source['metadata']
                    if 'source' in metadata:
                        print(f"      文件来源: {metadata['source']}")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="知识库管理工具")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列出知识库
    subparsers.add_parser("list", help="列出所有可用的知识库")
    
    # 显示统计信息
    stats_parser = subparsers.add_parser("stats", help="显示知识库统计信息")
    stats_parser.add_argument("--kb", type=str, help="指定知识库名称")
    
    # 搜索知识库
    search_parser = subparsers.add_parser("search", help="搜索知识库")
    search_parser.add_argument("query", type=str, help="搜索查询")
    search_parser.add_argument("--kb", type=str, help="指定知识库名称")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_knowledge_bases()
    elif args.command == "stats":
        show_knowledge_base_stats(args.kb if hasattr(args, 'kb') else None)
    elif args.command == "search":
        search_knowledge_base(args.query, args.kb if hasattr(args, 'kb') else None)
    
    print("\n💡 使用示例:")
    print("  1. 列出所有知识库:")
    print("     python manage_knowledge_bases.py list")
    print("  2. 查看所有知识库统计:")
    print("     python manage_knowledge_bases.py stats")
    print("  3. 查看特定知识库统计:")
    print("     python manage_knowledge_bases.py stats --kb 医疗知识库")
    print("  4. 搜索所有知识库:")
    print("     python manage_knowledge_bases.py search \"高血压怎么治疗\"")
    print("  5. 搜索特定知识库:")
    print("     python manage_knowledge_bases.py search \"投资策略\" --kb 商业知识库")
    print("="*60)

if __name__ == "__main__":
    main()

