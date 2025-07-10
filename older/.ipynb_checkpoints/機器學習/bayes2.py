import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

# 编造数据集
# 天气特征：晴天、多云、雨天
# 温度特征：热、适中、冷
# 湿度特征：高、适中、低
# 风特征：有、无
# 标签：打篮球、不打篮球

data = [
    ["晴天", "热", "高", "无", "打篮球"],
    ["晴天", "热", "高", "有", "不打篮球"],
    ["多云", "热", "高", "无", "打篮球"],
    ["雨天", "适中", "高", "无", "不打篮球"],
    ["雨天", "冷", "适中", "无", "不打篮球"],
    ["雨天", "冷", "适中", "有", "不打篮球"],
    ["多云", "冷", "适中", "有", "打篮球"],
    ["晴天", "适中", "高", "无", "打篮球"],
    ["晴天", "冷", "适中", "无", "打篮球"],
    ["雨天", "适中", "适中", "无", "不打篮球"],
    ["晴天", "适中", "适中", "有", "打篮球"],
    ["多云", "适中", "高", "有", "打篮球"],
    ["多云", "热", "适中", "无", "打篮球"],
    ["雨天", "适中", "高", "有", "不打篮球"]
]

# 将数据转换为特征矩阵 X 和标签向量 y
data = np.array(data)
X = data[:, :-1]
y = data[:, -1]

# 对特征和标签进行编码
encoders_X = []
X_encoded = np.zeros(X.shape)
for i in range(X.shape[1]):
    encoder_X = LabelEncoder()
    X_encoded[:, i] = encoder_X.fit_transform(X[:, i])
    encoders_X.append(encoder_X)

encoder_y = LabelEncoder()
y_encoded = encoder_y.fit_transform(y)

# 创建并训练多项分布朴素贝叶斯模型
model = MultinomialNB()
model.fit(X_encoded, y_encoded)

# 测试数据
x_test = np.array([["雨天", "适中", "高", "无"]])
x_test_encoded = np.zeros(x_test.shape)
for i in range(x_test.shape[1]):
    x_test_encoded[:, i] = encoders_X[i].transform(x_test[:, i])

# 进行预测
prediction_encoded = model.predict(x_test_encoded)
prediction = encoder_y.inverse_transform(prediction_encoded)
print("预测结果:", prediction)
