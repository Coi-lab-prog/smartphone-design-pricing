import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ✅ 设置中文字体（Windows 用户）
plt.rcParams['font.family'] = 'SimHei'  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 1️⃣ 读取情感分析汇总数据
df = pd.read_csv("design_dimension_sentiment_summary.csv")

# 去除空值或无法分析的维度（平均情感得分为 "-"）
df = df[df["平均情感得分"] != "-"]
df["平均情感得分"] = df["平均情感得分"].astype(float)

# 2️⃣ 柱状图：平均情感得分
plt.figure(figsize=(10, 6))
plt.bar(df["设计维度"], df["平均情感得分"], color="skyblue")
plt.ylim(0, 1)
plt.ylabel("平均情感得分")
plt.title("各设计维度平均满意度（情感得分）")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("dimension_sentiment_bar.png")
plt.show()

# 3️⃣ 雷达图：设计维度对比
labels = df["设计维度"].tolist()
values = df["平均情感得分"].tolist()

# 角度处理
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
values += values[:1]  # 闭合
angles += angles[:1]

# 绘图
fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, polar=True)
ax.plot(angles, values, 'o-', linewidth=2, label='满意度')
ax.fill(angles, values, alpha=0.25)

ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=11)
ax.set_ylim(0, 1)
ax.set_title("用户满意度雷达图")
plt.tight_layout()
plt.savefig("dimension_sentiment_radar.png")
plt.show()
