import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.preprocessing import LabelEncoder

# 原始训练数据
X_train = np.array([[1, 's'], [1, 's'], [1,'m'], [1, 's'], [1,'m'], [2, 's'], [2, 's'], [2,'m'], [2, 'l'], [2, 'l'], [3,'m'], [3, 'l'], [3,'m'], [3, 'l'], [3, 'l']])
y = [0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1]

# 对每个特征列进行编码
encoders = []
X_train_encoded = np.zeros(X_train.shape)
for i in range(X_train.shape[1]):
    encoder = LabelEncoder()
    X_train_encoded[:, i] = encoder.fit_transform(X_train[:, i])
    encoders.append(encoder)
#如果特征数据并非正态分布，使用高斯朴素贝叶斯（GaussianNB）可能不是最佳选择。
# 此时可以考虑使用其他类型的朴素贝叶斯分类器，
# 例如多项分布朴素贝叶斯（MultinomialNB）或伯努利朴素贝叶斯（BernoulliNB）。
# 创建并训练模型
model = BernoulliNB()
model.fit(X_train_encoded, y)

# 测试数据
x_test = np.array([[2, 's']])
x_test_encoded = np.zeros(x_test.shape)
for i in range(x_test.shape[1]):
    x_test_encoded[:, i] = encoders[i].transform(x_test[:, i])

# 进行预测
prediction = model.predict(x_test_encoded)
print("预测结果:", prediction)