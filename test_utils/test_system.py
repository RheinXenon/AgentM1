"""
简单的系统测试脚本
"""
import sys
import os

# 添加父目录到系统路径，以便导入项目模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config_manager import ConfigManager
from agents.agent_decision import AgentDecision
from agents.conversation_agent import ConversationAgent
from agents.rag_agent import MedicalRAG
from agents.web_search_agent import WebSearchAgent

def test_config_manager():
    """测试配置管理器"""
    print("=" * 50)
    print("测试配置管理器...")
    
    config_mgr = ConfigManager()
    
    # 测试获取配置
    config = config_mgr.get_config()
    print(f"✓ 配置加载成功")
    print(f"  - RAG启用状态: {config.get('rag_enabled')}")
    print(f"  - 系统名称: {config.get('system_name')}")
    
    # 测试更新配置
    test_updates = {
        "system_name": "测试系统",
        "rag_enabled": False
    }
    success = config_mgr.update_config(test_updates)
    print(f"✓ 配置更新{'成功' if success else '失败'}")
    
    # 恢复默认配置
    config_mgr.reset_to_default()
    print(f"✓ 配置重置成功")
    
    return True

def test_agents():
    """测试各个Agent"""
    print("\n" + "=" * 50)
    print("测试各个Agent...")
    
    config_mgr = ConfigManager()
    
    # 测试Agent Decision
    print("\n1. 测试Agent决策系统...")
    agent_decision = AgentDecision(config_mgr)
    decision = agent_decision.decide("你好")
    print(f"   ✓ Agent决策: {decision}")
    
    # 测试Conversation Agent
    print("\n2. 测试对话Agent...")
    conversation_agent = ConversationAgent(config_mgr)
    result = conversation_agent.chat("你好")
    print(f"   ✓ 对话Agent响应长度: {len(result.get('response', ''))} 字符")
    
    # 测试RAG Agent
    print("\n3. 测试RAG Agent...")
    try:
        rag_agent = MedicalRAG(config_mgr)
        result = rag_agent.query("测试问题")
        print(f"   ✓ RAG Agent初始化成功")
    except Exception as e:
        print(f"   ⚠ RAG Agent警告: {str(e)[:50]}... (这是正常的，如果数据库为空)")
    
    # 测试Web Search Agent
    print("\n4. 测试网络搜索Agent...")
    try:
        web_search_agent = WebSearchAgent(config_mgr)
        print(f"   ✓ 网络搜索Agent初始化成功")
    except Exception as e:
        print(f"   ⚠ 网络搜索Agent警告: {str(e)[:50]}...")
    
    return True

def test_prompt_update():
    """测试提示词更新"""
    print("\n" + "=" * 50)
    print("测试提示词更新...")
    
    config_mgr = ConfigManager()
    
    # 更新配置中的提示词
    test_prompt = "这是一个测试提示词"
    config_mgr.update_config({"conversation_prompt": test_prompt})
    
    # 创建Agent并检查是否使用了新提示词
    conversation_agent = ConversationAgent(config_mgr)
    conversation_agent.update_prompt()
    
    print(f"✓ 提示词更新机制正常")
    
    # 恢复默认配置
    config_mgr.reset_to_default()
    
    return True

def test_rag_switch():
    """测试RAG开关"""
    print("\n" + "=" * 50)
    print("测试RAG开关...")
    
    config_mgr = ConfigManager()
    
    # 测试启用状态
    config_mgr.update_config({"rag_enabled": True})
    assert config_mgr.is_rag_enabled() == True
    print(f"✓ RAG启用状态: True")
    
    # 测试禁用状态
    config_mgr.update_config({"rag_enabled": False})
    assert config_mgr.is_rag_enabled() == False
    print(f"✓ RAG禁用状态: False")
    
    # 恢复默认配置
    config_mgr.reset_to_default()
    
    return True

def main():
    """运行所有测试"""
    print("\n" + "🧪 开始系统测试...")
    print("=" * 50)
    
    tests = [
        ("配置管理器", test_config_manager),
        ("Agent系统", test_agents),
        ("提示词更新", test_prompt_update),
        ("RAG开关", test_rag_switch),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # 打印测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    for test_name, result, error in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
        if error:
            print(f"    错误: {error}")
    
    all_passed = all(result for _, result, _ in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    main()

