"""
数据导入工具 - 将文本数据导入到RAG系统
简化版:直接添加文本到向量数据库
"""
import argparse
from agents.rag_agent import MedicalRAG

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
    parser.add_argument("--demo", action="store_true", help="导入示例数据")
    parser.add_argument("--text", type=str, help="导入单条文本")
    
    args = parser.parse_args()
    
    if args.demo:
        # 导入示例医学数据
        demo_texts = [
            """
            高血压定义和分类:
            高血压是指血压持续升高的慢性疾病。正常血压范围为收缩压<120mmHg且舒张压<80mmHg。
            高血压分为三级:
            - 1级高血压(轻度):收缩压140-159mmHg或舒张压90-99mmHg
            - 2级高血压(中度):收缩压160-179mmHg或舒张压100-109mmHg  
            - 3级高血压(重度):收缩压≥180mmHg或舒张压≥110mmHg
            """,
            """
            糖尿病症状和诊断:
            糖尿病是一组以高血糖为特征的代谢性疾病。典型症状包括"三多一少":
            - 多饮:口渴多喝水
            - 多食:容易饥饿
            - 多尿:尿量增加
            - 消瘦:体重下降
            诊断标准:空腹血糖≥7.0mmol/L,或餐后2小时血糖≥11.1mmol/L
            """,
            """
            感冒和流感的区别:
            普通感冒(common cold):
            - 症状较轻,主要是鼻塞、流涕、咽痛
            - 很少发热或仅低热
            - 病程较短,通常1周内恢复
            
            流感(influenza):
            - 症状较重,高热(39-40°C)、全身酸痛、乏力
            - 起病急,传染性强
            - 可能引起肺炎等并发症
            - 需要抗病毒治疗
            """,
            """
            心脏病预警信号:
            以下症状可能是心脏病的预警信号,需要立即就医:
            1. 胸痛或胸部不适:压迫感、紧缩感,可能放射到手臂、颈部、下颌
            2. 呼吸困难:活动或休息时气短
            3. 心悸:心跳加快或不规律
            4. 晕厥或头晕
            5. 异常疲劳
            6. 恶心、呕吐、冷汗
            特别注意:女性心脏病症状可能不典型,更常表现为疲劳、气短等。
            """,
            """
            健康饮食金字塔:
            根据中国居民膳食指南,健康饮食应遵循:
            
            第一层(底层,最多):谷薯类
            - 每天250-400克谷物,包括全谷物和杂豆50-150克
            - 薯类50-100克
            
            第二层:蔬菜水果类
            - 蔬菜300-500克,深色蔬菜占一半
            - 水果200-350克
            
            第三层:动物性食物
            - 鱼禽肉蛋总量120-200克
            - 奶类300克
            - 大豆及坚果25-35克
            
            第四层(顶层,最少):油盐糖
            - 烹调油25-30克
            - 食盐<6克
            - 添加糖<50克
            """
        ]
        
        metadatas = [
            {"source": "高血压指南", "category": "心血管疾病"},
            {"source": "糖尿病诊疗规范", "category": "内分泌疾病"},
            {"source": "呼吸道感染指南", "category": "呼吸系统"},
            {"source": "心脏病预防手册", "category": "心血管疾病"},
            {"source": "营养学基础", "category": "预防保健"}
        ]
        
        print("正在导入示例医学数据...")
        ingest_text_data(demo_texts, metadatas)
        
    elif args.text:
        print(f"正在导入文本: {args.text[:50]}...")
        ingest_text_data([args.text])
        
    else:
        print("请使用 --demo 导入示例数据,或使用 --text 导入自定义文本")
        print("示例: python ingest_data.py --demo")

if __name__ == "__main__":
    main()

