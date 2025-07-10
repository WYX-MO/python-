from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 加载鸢尾花数据集
iris = load_iris()
# 特征矩阵
X = iris.data
# 标签向量
y = iris.target

# 划分训练集和测试集，测试集占比 30%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 创建 KNN 分类器，这里设置 K 值为 3
knn = KNeighborsClassifier(n_neighbors=3)

# 使用训练集数据对 KNN 模型进行训练
knn.fit(X_train, y_train)

# 利用训练好的模型对测试集进行预测
y_pred = knn.predict(X_test)

# 计算模型在测试集上的准确率
accuracy = accuracy_score(y_test, y_pred)
print(f"KNN 模型在测试集上的准确率: {accuracy * 100:.2f}%")
