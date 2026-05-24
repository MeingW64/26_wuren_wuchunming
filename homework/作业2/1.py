import numpy as np
from sklearn import datasets

housing = datasets.fetch_california_housing()
X = housing.data  # 特征矩阵X
Y = housing.target  # 结果向量Y
feature_names = housing.feature_names

X = np.column_stack([np.ones(20640) , X])
B = np.linalg.inv(X.T @ X) @ (X.T @ Y)
Yhat = X @ B
Q = Yhat - Y

print(Yhat)
print(Y)
print(Q)

print("特征形状:", X.shape)
# print("目标形状:", Y)
# print("特征名称:", feature_names)