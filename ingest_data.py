"""
数据导入工具 - 将文本数据导入到RAG系统
支持从text文件夹导入多种格式的文件
"""
import argparse
import os
from pathlib import Path
from typing import List, Tuple
from agents.rag_agent import MedicalRAG

def read_txt_file(file_path: str) -> str:
    """读取TXT文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  无法读取文件 {file_path}: {e}")
            return ""

def read_pdf_file(file_path: str) -> str:
    """读取PDF文件内容"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        print("⚠️  需要安装PyPDF2来读取PDF文件: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"⚠️  无法读取PDF文件 {file_path}: {e}")
        return ""

def read_file(file_path: str) -> Tuple[str, str]:
    """
    根据文件类型读取文件内容
    返回: (文件内容, 文件类型)
    """
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        content = read_txt_file(file_path)
        return content, 'txt'
    elif file_ext == '.pdf':
        content = read_pdf_file(file_path)
        return content, 'pdf'
    else:
        print(f"⚠️  不支持的文件格式: {file_ext}")
        return "", 'unknown'

def load_documents_from_folder(folder_path: str = "./text") -> Tuple[List[str], List[dict]]:
    """
    从指定文件夹加载所有支持的文档
    返回: (文本列表, 元数据列表)
    """
    texts = []
    metadatas = []
    
    # 支持的文件扩展名
    supported_extensions = {'.txt', '.pdf'}
    
    # 确保文件夹存在
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return texts, metadatas
    
    # 遍历文件夹中的所有文件
    folder = Path(folder_path)
    files = list(folder.glob('*'))
    
    if not files:
        print(f"⚠️  文件夹 {folder_path} 中没有文件")
        return texts, metadatas
    
    print(f"📂 正在扫描文件夹: {folder_path}")
    
    for file_path in files:
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"  📄 读取文件: {file_path.name}")
            content, file_type = read_file(str(file_path))
            
            if content and content.strip():
                texts.append(content)
                metadatas.append({
                    "source": file_path.name,
                    "file_type": file_type,
                    "file_path": str(file_path)
                })
                print(f"    ✓ 成功读取 ({len(content)} 字符)")
            else:
                print(f"    ✗ 文件内容为空或读取失败")
    
    return texts, metadatas

def load_documents_from_knowledge_bases(base_folder: str = "./text") -> dict:
    """
    从知识库文件夹结构加载文档
    每个子文件夹代表一个知识库
    
    Args:
        base_folder: 基础文件夹路径
        
    Returns:
        dict: {知识库名称: (文本列表, 元数据列表)}
    """
    knowledge_base_docs = {}
    
    # 确保基础文件夹存在
    if not os.path.exists(base_folder):
        print(f"❌ 文件夹不存在: {base_folder}")
        return knowledge_base_docs
    
    base_path = Path(base_folder)
    
    # 遍历所有子文件夹
    for kb_folder in base_path.iterdir():
        if kb_folder.is_dir():
            kb_name = kb_folder.name
            print(f"\n📚 正在处理知识库: {kb_name}")
            texts, metadatas = load_documents_from_folder(str(kb_folder))
            
            if texts:
                # 为每个元数据添加知识库信息
                for metadata in metadatas:
                    metadata["knowledge_base"] = kb_name
                knowledge_base_docs[kb_name] = (texts, metadatas)
                print(f"  ✅ 从 '{kb_name}' 加载了 {len(texts)} 个文档")
            else:
                print(f"  ⚠️  '{kb_name}' 中没有找到有效文档")
    
    return knowledge_base_docs

def ingest_text_data(texts, metadatas=None, knowledge_base=None):
    """导入文本数据到知识库"""
    try:
        # 导入配置管理器
        from config_manager import ConfigManager
        
        config_manager = ConfigManager()
        rag_agent = MedicalRAG(config_manager)
        
        if metadatas is None:
            metadatas = [{"source": f"document_{i}"} for i in range(len(texts))]
        
        success = rag_agent.add_documents(texts, metadatas, knowledge_base=knowledge_base)
        
        if success:
            kb_info = f"到知识库 '{knowledge_base}'" if knowledge_base else "到默认知识库"
            print(f"✅ 成功导入 {len(texts)} 条数据{kb_info}")
        else:
            print("❌ 导入失败")
            
    except Exception as e:
        print(f"❌ 导入过程出错: {e}")
        import traceback
        traceback.print_exc()

def ingest_all_knowledge_bases(base_folder: str = "./text"):
    """导入所有知识库的文档"""
    try:
        from config_manager import ConfigManager
        
        print(f"\n{'='*60}")
        print("📚 开始批量导入知识库文档...")
        print(f"{'='*60}\n")
        
        # 加载所有知识库的文档
        kb_docs = load_documents_from_knowledge_bases(base_folder)
        
        if not kb_docs:
            print(f"\n❌ 没有找到知识库文件夹")
            print(f"\n💡 提示:")
            print(f"  - 请确保在 {base_folder} 下创建知识库文件夹")
            print(f"  - 每个子文件夹代表一个知识库")
            print(f"  - 例如: {base_folder}/医疗知识库/, {base_folder}/商业知识库/")
            return
        
        # 初始化RAG agent
        config_manager = ConfigManager()
        rag_agent = MedicalRAG(config_manager)
        
        # 显示已配置的知识库
        configured_kbs = rag_agent.get_all_knowledge_bases()
        print(f"📋 已配置的知识库:")
        for kb_name, description in configured_kbs.items():
            print(f"  - {kb_name}: {description}")
        print()
        
        # 导入每个知识库的文档
        total_docs = 0
        for kb_name, (texts, metadatas) in kb_docs.items():
            print(f"\n{'='*60}")
            print(f"📥 正在导入知识库: {kb_name}")
            print(f"{'='*60}")
            print(f"文档数量: {len(texts)}")
            print(f"总字符数: {sum(len(t) for t in texts)}")
            
            # 检查知识库是否已配置
            if kb_name not in configured_kbs:
                print(f"⚠️  警告: 知识库 '{kb_name}' 未在配置中，将使用默认知识库")
                kb_name = None
            
            success = rag_agent.add_documents(texts, metadatas, knowledge_base=kb_name)
            
            if success:
                total_docs += len(texts)
                print(f"✅ 成功导入 {len(texts)} 个文档")
            else:
                print(f"❌ 导入失败")
        
        # 显示最终统计
        print(f"\n{'='*60}")
        print(f"📊 导入完成统计")
        print(f"{'='*60}")
        print(f"总共导入文档数: {total_docs}")
        
        # 显示各知识库的文档数量
        stats = rag_agent.get_knowledge_base_stats()
        print(f"\n各知识库文档数量:")
        for kb_name, info in stats.items():
            print(f"  - {kb_name}: {info['vectors_count']} 个向量")
        print(f"{'='*60}\n")
            
    except Exception as e:
        print(f"❌ 批量导入过程出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="导入知识库数据 - 支持多知识库")
    parser.add_argument("--text", type=str, help="导入单条文本")
    parser.add_argument("--folder", type=str, help="从指定文件夹导入文档到默认知识库")
    parser.add_argument("--kb", type=str, help="指定知识库名称（与--folder配合使用）")
    parser.add_argument("--all", action="store_true", help="从text文件夹批量导入所有知识库")
    parser.add_argument("--base-folder", type=str, default="./text", help="知识库基础文件夹 (默认: ./text)")
    
    args = parser.parse_args()
    
    if args.text:
        # 导入单条文本
        print(f"正在导入文本: {args.text[:50]}...")
        ingest_text_data([args.text], knowledge_base=args.kb)
    elif args.all:
        # 批量导入所有知识库
        ingest_all_knowledge_bases(args.base_folder)
    elif args.folder:
        # 从指定文件夹导入文档
        print(f"\n{'='*60}")
        print(f"📚 开始从文件夹导入文档...")
        if args.kb:
            print(f"目标知识库: {args.kb}")
        print(f"{'='*60}\n")
        
        texts, metadatas = load_documents_from_folder(args.folder)
        
        if texts:
            print(f"\n📊 统计信息:")
            print(f"  - 共找到 {len(texts)} 个有效文档")
            print(f"  - 总字符数: {sum(len(t) for t in texts)}")
            print(f"\n开始导入到知识库...\n")
            ingest_text_data(texts, metadatas, knowledge_base=args.kb)
        else:
            print(f"\n❌ 没有找到可导入的文档")
            print("\n💡 提示:")
            print(f"  - 请确保 {args.folder} 文件夹存在")
            print("  - 支持的文件格式: .txt, .pdf")
            print("=" * 60)
    else:
        # 默认行为：批量导入所有知识库
        print("未指定操作，默认批量导入所有知识库...")
        print("如需其他操作，请使用 --help 查看帮助\n")
        ingest_all_knowledge_bases(args.base_folder)
    
    print("\n💡 使用示例:")
    print("  1. 批量导入所有知识库:")
    print("     python ingest_data.py --all")
    print("  2. 导入到指定知识库:")
    print("     python ingest_data.py --folder ./my_docs --kb 医疗知识库")
    print("  3. 导入单条文本:")
    print("     python ingest_data.py --text '这是一段知识...' --kb 商业知识库")
    print("=" * 60)

if __name__ == "__main__":
    main()

