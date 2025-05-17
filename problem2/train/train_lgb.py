# 文件路径: project/train/train_lgb.py

import pandas as pd
import numpy as np
import lightgbm as lgb
import optuna
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 读取数据
df = pd.read_csv("D:\data\smartphone-design-pricing\project\data\panel_ml.csv")
df["log_sales"] = np.log1p(df["sales"])

# 特征与标签
features = ["version", "price", "comp_price_idx", "sent_pos",
            "price_bad_ratio", "promotion_flag", "memory", "storage"]
X = df[features]
y = df["log_sales"]

# 划分训练/验证集
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

# 调参目标函数
def objective(trial):
    params = {
        "objective": "regression",
        "metric": "rmse",
        "verbosity": -1,
        "learning_rate": trial.suggest_float("lr", 0.01, 0.1),
        "num_leaves": trial.suggest_int("leaves", 31, 128),
        "min_data_in_leaf": trial.suggest_int("min_data", 10, 100),
        "feature_fraction": trial.suggest_float("ff", 0.6, 1.0),
        "bagging_fraction": trial.suggest_float("bf", 0.6, 1.0),
        "bagging_freq": 1
    }
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val)
    model = lgb.train(params, train_data, valid_sets=[val_data])
    pred = model.predict(X_val)
    return mean_squared_error(y_val, pred)

# 调参搜索
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=30)

# 训练最终模型
best_params = study.best_params
final_model = lgb.train(best_params, lgb.Dataset(X, label=y), num_boost_round=100)

# 保存模型
final_model.save_model("D:\data\smartphone-design-pricing\project\models\lgb_final.txt")
print("✅ 模型已保存到 models/lgb_final.txt")
