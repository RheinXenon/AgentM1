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

def ingest_text_data(texts, metadatas=None):
    """导入文本数据到知识库"""
    try:
        rag_agent = MedicalRAG()
        
        if metadatas is None:
            metadatas = [{"source": f"document_{i}"} for i in range(len(texts))]
        
        success = rag_agent.add_documents(texts, metadatas)
        
        if success:
            print(f"✅ 成功导入 {len(texts)} 条数据到知识库")
        else:
            print("❌ 导入失败")
            
    except Exception as e:
        print(f"❌ 导入过程出错: {e}")

def main():
    parser = argparse.ArgumentParser(description="导入医学知识数据")
    parser.add_argument("--text", type=str, help="导入单条文本")
    parser.add_argument("--folder", type=str, default="./text", help="从指定文件夹导入文档 (默认: ./text)")
    
    args = parser.parse_args()
    
    if args.text:
        # 导入单条文本
        print(f"正在导入文本: {args.text[:50]}...")
        ingest_text_data([args.text])
    else:
        # 默认从text文件夹导入文档
        print(f"\n{'='*60}")
        print("📚 开始从文件夹导入文档...")
        print(f"{'='*60}\n")
        
        texts, metadatas = load_documents_from_folder(args.folder)
        
        if texts:
            print(f"\n📊 统计信息:")
            print(f"  - 共找到 {len(texts)} 个有效文档")
            print(f"  - 总字符数: {sum(len(t) for t in texts)}")
            print(f"\n开始导入到知识库...\n")
            ingest_text_data(texts, metadatas)
        else:
            print(f"\n❌ 没有找到可导入的文档")
            print("\n💡 提示:")
            print(f"  - 请确保 {args.folder} 文件夹存在")
            print("  - 支持的文件格式: .txt, .pdf")
            print("  - 可使用 --folder 参数指定其他文件夹")
            print("\n示例:")
            print("  python ingest_data.py")
            print("  python ingest_data.py --folder ./my_documents")
            print("  python ingest_data.py --text '这是一段医学知识...'")
            print("=" * 60)

if __name__ == "__main__":
    main()

