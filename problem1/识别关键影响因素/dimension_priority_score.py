import pandas as pd

# 读取分析结果
df = pd.read_csv("design_dimension_sentiment_summary.csv")
df = df[df["平均情感得分"] != "-"]

# 类型转换
df["平均情感得分"] = df["平均情感得分"].astype(float)
df["提及评论数"] = df["提及评论数"].astype(int)
df["负面评论占比"] = df["负面评论占比"].str.replace("%", "").astype(float) / 100

# 总评论数
total_mentions = df["提及评论数"].sum()

# 计算得分
df["影响力得分"] = (
    df["平均情感得分"]
    * (df["提及评论数"] / total_mentions)
    * (1 - df["负面评论占比"])
)

# 排序
df = df.sort_values(by="影响力得分", ascending=False)

# 输出并保存
print("\n📊 各维度影响力评分（排序）：\n")
print(df[["设计维度", "提及评论数", "平均情感得分", "负面评论占比", "影响力得分"]].to_string(index=False))

df.to_csv("dimension_priority_score.csv", index=False, encoding="utf_8_sig")
print("\n✅ 已保存：dimension_priority_score.csv")
