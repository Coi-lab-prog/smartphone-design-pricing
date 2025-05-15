import pandas as pd
import jieba
import jieba.posseg as pseg
from snownlp import SnowNLP
from collections import defaultdict, Counter

# === 1. 加载评论数据 ===
csv_path = r"D:\data\smartphone-design-pricing\data\tmall_782189145082_comments.csv"
df = pd.read_csv(csv_path)
df = df[df["content"].notna()]

# === 2. 定义维度关键词 ===
dimension_keywords = {
    "外观设计": {"外观", "颜色", "手感", "屏幕", "设计", "颜值"},
    "拍照性能": {"拍照", "清晰", "像素", "摄像", "相机", "微距", "抓拍"},
    "续航发热": {"续航", "发热", "充电", "耗电", "电池", "温度"},
    "系统性能": {"流畅", "不卡", "运行", "速度", "系统", "响应"},
    "售后服务": {"客服", "服务", "物流", "退货", "响应", "沟通"},
    "价格敏感度": {"价格", "值不值", "便宜", "优惠", "划算", "太贵", "贵"}
}

# === 3. 初始化结构 ===
dim_sentiment_scores = defaultdict(list)
dim_mentions = defaultdict(int)

# === 4. 处理每条评论 ===
for content in df["content"]:
    text = str(content)
    words = set(jieba.lcut(text))
    s = SnowNLP(text).sentiments  # 情感分（0-1）

    for dim, keywords in dimension_keywords.items():
        if words & keywords:
            dim_sentiment_scores[dim].append(s)
            dim_mentions[dim] += 1

# === 5. 输出结果表格 ===
output = []
for dim in dimension_keywords.keys():
    scores = dim_sentiment_scores.get(dim, [])
    count = len(scores)
    if count == 0:
        avg = "-"
        bad_ratio = "-"
    else:
        avg = round(sum(scores) / count, 3)
        bad_ratio = round(sum(1 for x in scores if x < 0.4) / count * 100, 1)
    output.append([dim, count, avg, f"{bad_ratio}%" if bad_ratio != "-" else "-"])

# === 6. 保存为 DataFrame 并打印/保存 ===
result_df = pd.DataFrame(output, columns=["设计维度", "提及评论数", "平均情感得分", "负面评论占比"])
print("\n📊 各设计维度用户情感分析：\n")
print(result_df.to_string(index=False))

result_df.to_csv("design_dimension_sentiment_summary.csv", index=False, encoding="utf_8_sig")
print("\n✅ 已保存至 design_dimension_sentiment_summary.csv")
