"""
智能手机设计维度分析 - 全功能整合版
功能：从数据加载到关键因素识别，所有代码集成在一个文件中
"""

# ================== 导入依赖 ==================
import re
import json
import jieba
import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict
from snownlp import SnowNLP

# ================== 配置参数 ==================
DATA_PATH = r"D:\data\smartphone-design-pricing\data\tmall_782189145082_comments.csv"          # 输入数据路径
OUTPUT_DIR = "results"                   # 输出目录
STOPWORDS = {"的", "了", "是", "在", "和"}  # 基础停用词
KEYWORD_CONFIG = {
    "外观设计": ["外观", "颜色", "手感", "屏幕", "设计", "颜值"],
    "拍照性能": ["拍照", "清晰", "像素", "摄像", "相机", "微距", "抓拍"],
    "续航发热": ["续航", "发热", "充电", "耗电", "电池", "温度"],
    "系统性能": ["流畅", "不卡", "运行", "速度", "系统", "响应"],
    "售后服务": ["客服", "服务", "物流", "退货", "响应", "沟通"],
    "价格敏感度": ["价格", "值不值", "便宜", "优惠", "划算", "太贵", "贵"]
}

# ================== 工具函数 ==================
def preprocess_text(text):
    """文本预处理（内置停用词）"""
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", text)
    words = [word for word in jieba.lcut(text) 
            if word not in STOPWORDS and len(word) > 1]
    return words

# ================== 情感分析 ==================
def analyze_sentiment():
    """执行情感分析流程"""
    # 加载数据
    df = pd.read_csv(DATA_PATH)
    df = df[df["content"].notna()]
    print(f"📂 已加载 {len(df)} 条评论")

    # 初始化统计
    dim_scores = defaultdict(list)
    dim_counts = defaultdict(int)

    # 处理每条评论
    for text in df["content"]:
        words = set(preprocess_text(str(text)))
        sentiment = SnowNLP(text).sentiments

        # 维度匹配
        for dim, keywords in KEYWORD_CONFIG.items():
            if any(kw in words for kw in keywords):
                dim_scores[dim].append(sentiment)
                dim_counts[dim] += 1

    # 生成结果表
    output = []
    for dim in KEYWORD_CONFIG:
        scores = dim_scores.get(dim, [])
        count = len(scores)
        avg = round(np.mean(scores), 3) if scores else 0.0
        bad_ratio = round(np.mean([s < 0.4 for s in scores]), 3) if scores else 0.0
        
        output.append({
            "设计维度": dim,
            "提及次数": count,
            "平均情感分": avg,
            "负面评价率": bad_ratio
        })

    result_df = pd.DataFrame(output)
    return result_df

# ================== 关键因素识别 ==================
def calculate_priority(df):
    """计算维度优先级"""
    # 熵权法计算权重
    X = df[["提及次数", "平均情感分", "负面评价率"]]
    X_norm = (X - X.min()) / (X.max() - X.min() + 1e-10)
    
    p = X_norm / (X_norm.sum(axis=0) + 1e-10)
    e = -np.sum(p * np.log(p + 1e-10), axis=0) / np.log(len(X))
    weights = (1 - e) / np.sum(1 - e)
    
    # 综合得分
    df["优先级得分"] = np.dot(X_norm, weights)
    df = df.sort_values("优先级得分", ascending=False)
    return df

# ================== 主流程 ==================
if __name__ == "__main__":
    # 执行情感分析
    sentiment_df = analyze_sentiment()
    
    # 计算关键因素
    priority_df = calculate_priority(sentiment_df)
    
    # 保存结果
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    priority_df.to_csv(f"{OUTPUT_DIR}/priority_results.csv", index=False)
    
    # 打印结果
    print("\n🔝 关键维度优先级排序：")
    print(priority_df[["设计维度", "优先级得分"]].head(10))
    print(f"\n✅ 结果已保存至 {OUTPUT_DIR}/ 目录")