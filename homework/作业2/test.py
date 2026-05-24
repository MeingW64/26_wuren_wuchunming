import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ---------------------- 手搓多元线性回归类 ----------------------
class LinearRegressionScratch:
    """
    多元线性回归（使用正规方程 + 伪逆，避免奇异矩阵问题）
    """
    def __init__(self, fit_intercept=True):
        self.fit_intercept = fit_intercept
        self.coef_ = None      # 特征系数
        self.intercept_ = None # 截距

    def fit(self, X, y):
        """
        训练模型
        X: numpy array, shape (n_samples, n_features)
        y: numpy array, shape (n_samples, )
        """
        n_samples, n_features = X.shape
        # 如果启用截距，则在特征矩阵前加一列 1
        if self.fit_intercept:
            X_b = np.c_[np.ones((n_samples, 1)), X]  # shape (n_samples, n_features+1)
        else:
            X_b = X

        # 正规方程：theta = (X_b^T * X_b)^{-1} * X_b^T * y
        # 使用伪逆 pinv 避免奇异矩阵求逆出错
        theta = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y

        if self.fit_intercept:
            self.intercept_ = theta[0]
            self.coef_ = theta[1:]
        else:
            self.intercept_ = 0.0
            self.coef_ = theta
        return self

    def predict(self, X):
        """
        预测
        X: numpy array, shape (n_samples, n_features)
        return: 预测值数组，shape (n_samples, )
        """
        if self.fit_intercept:
            X_b = np.c_[np.ones((X.shape[0], 1)), X]
            return X_b @ np.r_[self.intercept_, self.coef_]
        else:
            return X @ self.coef_

    def score(self, X, y):
        """
        返回 R^2 决定系数
        """
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        return r2

# ---------------------- 数据加载与预处理 ----------------------
# 加载加州房价数据集
housing = fetch_california_housing()
X, y = housing.data, housing.target
feature_names = housing.feature_names

# 划分训练集与测试集（80% 训练，20% 测试）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------- 模型训练与评估 ----------------------
model = LinearRegressionScratch(fit_intercept=True)
model.fit(X_train, y_train)

# 预测
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# 计算指标
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse  = mean_squared_error(y_test, y_test_pred)
train_rmse = np.sqrt(train_mse)
test_rmse  = np.sqrt(test_mse)
train_r2 = r2_score(y_train, y_train_pred)
test_r2  = r2_score(y_test, y_test_pred)

print("===== 模型评估 =====")
print(f"训练集 MSE : {train_mse:.4f}   RMSE: {train_rmse:.4f}   R²: {train_r2:.4f}")
print(f"测试集 MSE : {test_mse:.4f}   RMSE: {test_rmse:.4f}   R²: {test_r2:.4f}")
print("\n特征系数：")
for name, coef in zip(feature_names, model.coef_):
    print(f"  {name:15s}: {coef:.4f}")
print(f"截距 (intercept): {model.intercept_:.4f}")

# ---------------------- 可视化 ----------------------
plt.rcParams['font.size'] = 12
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. 真实值 vs 预测值（测试集）
ax = axes[0, 0]
ax.scatter(y_test, y_test_pred, alpha=0.4, edgecolors='k', linewidth=0.3)
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax.set_xlabel('真实房价 (单位：$100k)')
ax.set_ylabel('预测房价 (单位：$100k)')
ax.set_title('测试集：真实值 vs 预测值')
ax.grid(True, alpha=0.3)

# 2. 残差图（测试集）
ax = axes[0, 1]
residuals = y_test - y_test_pred
ax.scatter(y_test_pred, residuals, alpha=0.4, edgecolors='k', linewidth=0.3)
ax.axhline(y=0, color='r', linestyle='--', lw=2)
ax.set_xlabel('预测房价')
ax.set_ylabel('残差')
ax.set_title('测试集残差分布')
ax.grid(True, alpha=0.3)

# 3. 残差直方图
ax = axes[1, 0]
ax.hist(residuals, bins=40, edgecolor='k', alpha=0.7)
ax.axvline(x=0, color='r', linestyle='--', lw=2)
ax.set_xlabel('残差')
ax.set_ylabel('频数')
ax.set_title('测试集残差直方图')
ax.grid(True, alpha=0.3)

# 4. 特征系数（重要性）
ax = axes[1, 1]
coef_abs = np.abs(model.coef_)
sorted_idx = np.argsort(coef_abs)
ax.barh(np.array(feature_names)[sorted_idx], coef_abs[sorted_idx], edgecolor='k')
ax.set_xlabel('系数绝对值')
ax.set_title('特征重要性（基于系数绝对值）')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()