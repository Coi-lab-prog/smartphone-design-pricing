import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 加载评论数据
path = "D:\data\smartphone-design-pricing\data\\tmall_782189145082_comments.csv"

df = pd.read_csv(path)

# 自定义停用词表（可拓展）
STOPWORDS = set([
    "我", "是", "了", "的", "在", "这", "也", "就", "和", "不", "都", "很", "用", "有",
    "没有", "一个", "用户", "使用", "就是", "评价", "填写", "此", "还", "现在",
    "可以", "非常", "手机", "华为", "东西", "感觉", "真的", "来说", "但是", "所以", "评论", 
    "尤其", "还是", "不能", "有点", "到手", "而且", "不到", "其他", "这么", "自己", "不了", 
    "除了", "首先", "哈哈哈", "无论是", "看到", "确实", "的话", "因为", "那么", "各种", "之后",
    "觉得", "网上", "一次", "出来", "希望", "完全", "直接", "更是", "方面", "还有", "不错", "这个", "问题", "客户", "之前", "支持", "照片", "选择", "物流", "平台", "发货",
    "之后", "购物", "收到", "服务", "拍摄", "旗舰店", "产品", "系列", "品牌", "好评", "满意",
    "清晰度", "照片", "显示", "颜色", "操作", "整体", "差评", "快递", "送货", "功能", "时间",
    "收到货", "买的", "性价比", "使用中", "一下", "之后", "整体", "一样", "一次", "目前","苹果",
    "双十","小米","不是","出现","一点","不如","起来","特别","一直","运行","效果","体验","很快","几天",
    "购买","一天"
])

# 分词
text = " ".join(df["content"].dropna().astype(str).tolist())
words = jieba.lcut(text)

# 过滤停用词和长度小于2的词
filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 1]

# 高频词统计（可选查看前2·0个）
top_words = Counter(filtered_words).most_common(20)
print("🔝 高频词 TOP20：")
for word, count in top_words:
    print(f"{word}: {count}")

# 生成词云
wc = WordCloud(
    font_path="simhei.ttf",
    width=800,
    height=400,
    background_color="white"
).generate(" ".join(filtered_words))

# 显示词云
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
#plt.title("清洗后关键词词云")
plt.tight_layout()
plt.show()

# 保存词云图
wc.to_file("cleaned_wordcloud.png")
print("✅ 词云图已保存为 cleaned_wordcloud.png")
