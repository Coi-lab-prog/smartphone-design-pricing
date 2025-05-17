import pandas as pd

path = "D:\data\smartphone-design-pricing\data\\tmall_782189145082_comments.csv"

df = pd.read_csv(path)

print(df.columns)

# 删除空评论
df = df[df["content"].notna() & (df["content"].str.strip() != "")]

# 去重（同一用户同一内容）
df = df.drop_duplicates(subset=["user", "content"])

# 去除无效字符（表情、换行等）
df["content"] = df["content"].str.replace(r"\s+", " ", regex=True)
