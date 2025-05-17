import pandas as pd, numpy as np, statsmodels.formula.api as smf
from joblib import dump, load
import math, os

# ---------- 1. 文件路径 ----------
BASE_DIR = r"D:\data\smartphone-design-pricing\problem2\new_data"
PURA_FILE = os.path.join(BASE_DIR, "panel_ml_monthly_fixed2.csv")
COMP_FILE = os.path.join(BASE_DIR, "competitors_monthly_v2.csv")

# ---------- 2. 读取数据 ----------
pura = pd.read_csv(PURA_FILE)
comp  = pd.read_csv(COMP_FILE)

# ---------- 3. 标准化 month 格式 ----------
pura["month"] = pura["month"].astype(str).str[:7] + "-01"
comp["month"] = pd.to_datetime(comp["month"], errors="coerce").dt.strftime("%Y-%m-01")
pura["month"] = pura["month"].astype(str)
comp["month"] = comp["month"].astype(str)

# ---------- 4. 构建竞品价格指数 ----------
comp_idx = (
    comp.groupby("month")["price"]
    .mean()
    .rename("comp_avg_price")
    .reset_index()
)
base_price = comp_idx.loc[comp_idx["month"] == "2024-05-01", "comp_avg_price"].values[0]
comp_idx["comp_price_idx"] = comp_idx["comp_avg_price"] / base_price * 100

# 合并进 pura 数据
pura = pura.merge(comp_idx[["month", "comp_price_idx"]], on="month", how="left")

# ✅ 错误检查
if "comp_price_idx" not in pura.columns:
    raise ValueError("❌ 合并失败：未找到 comp_price_idx，请检查 month 格式或 merge 步骤")

# ---------- 5. 清洗与特征构造 ----------
pura["comp_price_idx"] = pd.to_numeric(pura["comp_price_idx"], errors="coerce").fillna(method="ffill")
pura["sales"] = pura["sales"] * 1e4
pura["log_sales"] = np.log(pura["sales"])
pura["log_price"] = np.log(pura["price"])
pura["log_comp_idx"] = np.log(pura["comp_price_idx"])
pura["pro_dummy"] = pura["version"].isin([1, 4, 5]).astype(int)
pura["cost"] = pura["price"] * np.where(pura["pro_dummy"], 0.53, 0.50)
pura["profit_per_unit"] = pura["price"] - pura["cost"]

# ---------- 6. 拟合 OLS 模型 ----------
formula = (
    "log_sales ~ log_price + log_comp_idx + promotion_flag + "
    "price_bad_ratio + pro_dummy"
)
model = smf.ols(formula, data=pura).fit()
print(model.summary())

# ---------- 7. 保存模型 ----------
model_file = os.path.join(BASE_DIR, "pura_demand_model.joblib")
dump(model, model_file)
print(f"\n✅ 模型已保存为：{model_file}")

# ---------- 8. 定义预测函数 ----------
def predict_sales(price, comp_idx, promo=0, price_bad=0.05, pro_dummy=0):
    m = load(model_file)
    log_q = (
        m.params["Intercept"]
        + m.params["log_price"] * math.log(price)
        + m.params["log_comp_idx"] * math.log(comp_idx)
        + m.params["promotion_flag"] * promo
        + m.params["price_bad_ratio"] * price_bad
        + m.params["pro_dummy"] * pro_dummy
    )
    return math.exp(log_q)

# ---------- 9. 情景预测 ----------
print("\n📉 模拟“降价 5%”后销量 & 利润预测：\n")
for v in sorted(pura["version"].unique()):
    latest = pura[pura["version"] == v].iloc[-1]
    new_price = latest["price"] * 0.95
    vol_new = predict_sales(
        price=new_price,
        comp_idx=latest["comp_price_idx"],
        promo=latest["promotion_flag"],
        price_bad=latest["price_bad_ratio"],
        pro_dummy=latest["pro_dummy"]
    )
    cost = new_price * (0.53 if latest["pro_dummy"] else 0.50)
    profit = (new_price - cost) * vol_new
    print(f"[v{v}] 价↓5% → 预计销量 {vol_new/1e4:.2f} 万台，利润 {profit/1e8:.2f} 亿元")
