# 测试工具包

本文件夹包含系统测试和知识库检查工具。

## 📂 文件说明

### 1. check_knowledge_base.py
知识库检查工具，用于检查 RAG 知识库的状态。

**功能：**
- 检查数据库文件夹是否存在
- 连接数据库并验证
- 查看集合信息和向量数量
- 测试查询功能

**使用方法：**
```bash
python test_utils/check_knowledge_base.py
```

### 2. test_system.py
系统测试脚本，用于测试各个 Agent 和配置管理功能。

**功能：**
- 测试配置管理器
- 测试各个 Agent（对话、RAG、网络搜索）
- 测试提示词更新机制
- 测试 RAG 开关

**使用方法：**
```bash
python test_utils/test_system.py
```

## 🚀 快速开始

### 检查知识库状态
```bash
python test_utils/check_knowledge_base.py
```

### 运行系统测试
```bash
python test_utils/test_system.py
```

## 📝 注意事项

1. 这些脚本需要从项目根目录运行
2. 确保已安装所有依赖（`pip install -r requirements.txt`）
3. 在运行 `check_knowledge_base.py` 前，确保数据库文件夹存在
4. 如果数据库为空，需要先运行 `python ingest_data.py` 导入数据

## 💡 常见问题

**Q: 数据库被锁定怎么办？**
A: 停止所有正在运行的 Python 进程，特别是 `app.py`

**Q: 知识库为空怎么办？**
A: 运行 `python ingest_data.py` 导入数据

**Q: 测试失败怎么办？**
A: 查看错误信息，确保配置文件正确且所有依赖已安装

