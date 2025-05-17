import pandas as pd
import numpy as np
import lightgbm as lgb

# ---------- 路径配置：按你的本地实际路径修改 ----------
DATA_PATH   = r"D:\data\smartphone-design-pricing\project\data\panel_ml_weekly.csv"
MODEL_PATH  = r"D:\data\smartphone-design-pricing\project\models\lgb_final.txt"
OUTPUT_PATH = r"D:\data\smartphone-design-pricing\project\data\scenario_prediction.csv"

# ---------- 加载训练数据 & 模型 ----------
df = pd.read_csv(DATA_PATH)
model = lgb.Booster(model_file=MODEL_PATH)

# ---------- 成本表（元） ----------
cost_table = {0: 3000, 1: 3500}        # 可改成真实成本

# ---------- 定义预测函数 ----------
feature_cols = ["version", "price", "comp_price_idx", "sent_pos",
                "price_bad_ratio", "promotion_flag", "memory", "storage"]

def predict_sales(version, price):
    # 取该 version 最近一周记录作为基底
    base_row = df[df["version"] == version].iloc[-1].copy()

    # 更新想要调整的价格
    base_row["price"] = price
    base_row["version"] = version

    row = base_row[feature_cols].to_frame().T.astype({
        "version": int,
        "price": float,
        "comp_price_idx": float,
        "sent_pos": float,
        "price_bad_ratio": float,
        "promotion_flag": int,
        "memory": int,
        "storage": int
    })

    log_q = model.predict(row)[0]
    return np.expm1(log_q)   # 还原对数

# ---------- 情景设计 ----------
scenarios = [
    {"方案": "S0 原价",      "version": 0, "price_adj": 1.00},
    {"方案": "S1 降价5%",    "version": 0, "price_adj": 0.95},
    {"方案": "S2 降价10%",   "version": 0, "price_adj": 0.90},
    {"方案": "S3 降价20%",   "version": 0, "price_adj": 0.80},
    {"方案": "S4 Pro +20%",  "version": 1, "price_adj": 1.20},
]

# ---------- 执行预测 ----------
results = []
for s in scenarios:
    v = s["version"]
    base_price = df[df["version"] == v]["price"].mean()   # 周均价均值
    new_price = round(base_price * s["price_adj"], 2)

    q = predict_sales(v, new_price)
    π = (new_price - cost_table[v]) * q

    results.append({
        "方案": s["方案"],
        "机型": "Pro" if v else "Base",
        "定价": new_price,
        "预测销量": int(q),
        "预测利润（万元）": round(π / 1e4, 2)
    })

# ---------- 输出结果 ----------
df_out = pd.DataFrame(results)
print(df_out)
df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf_8_sig")
print(f"\n✅ 结果已保存到 {OUTPUT_PATH}")
