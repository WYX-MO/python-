import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import tkinter as tk
from PIL import Image, ImageDraw
import cv2
import numpy as np

# 定义超参数
num_epochs = 10
batch_size = 32
learning_rate = 0.001
# 重新训练的阈值
retrain_threshold = 10
# 记录正确预测的数量
correct_count = 0

# 数据预处理
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# 加载数据集
data_dir = 'E:\\pyLearn\\imgs'  # 替换为你的数据目录
train_dataset = datasets.ImageFolder(os.path.join(data_dir, 'math_train'), transform=transform)
test_dataset = datasets.ImageFolder(os.path.join(data_dir, 'math_test'), transform=transform)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


# 定义简单的卷积神经网络模型
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 8)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x


model = SimpleCNN()

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# 训练模型
total_step = len(train_loader)
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (i + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Step [{i + 1}/{total_step}], Loss: {loss.item():.4f}')


# 定义 Sketchpad 类用于绘制和预测
class Sketchpad:
    def __init__(self, parent, width=200, height=200):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='white')
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Return>", self.save_and_predict)
        self.image = Image.new("L", (width, height), color=255)
        self.draw = ImageDraw.Draw(self.image)

    def draw(self, event):
        x, y = event.x, event.y
        r = 2
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill='black')
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill=0)

    def save_and_predict(self, event=None):
        global correct_count
        resized_image = self.image.resize((32, 32), Image.Resampling.LANCZOS)
        img_array = np.array(resized_image)
        img_array = cv2.threshold(img_array, 127, 255, cv2.THRESH_BINARY)[1]
        img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float()
        img_tensor = (img_tensor / 255.0 - 0.5) / 0.5

        model.eval()
        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs.data, 1)
            print(f"预测结果: {predicted.item()}")

            # 模拟用户反馈，这里可以替换为实际的用户交互
            user_feedback = input("预测是否正确？(y/n): ")
            if user_feedback.lower() == 'y':
                # 这里可以添加代码将图片添加到测试集===================================
                correct_count += 1
                if correct_count >= retrain_threshold:
                    print("达到重新训练阈值，开始重新训练模型...")
                    self.retrain_model()
                    correct_count = 0

    def retrain_model(self):
        global model
        # 重新加载数据集
        train_dataset = datasets.ImageFolder(os.path.join(data_dir, 'math_train'), transform=transform)
        test_dataset = datasets.ImageFolder(os.path.join(data_dir, 'math_test'), transform=transform)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        model = SimpleCNN()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)

        total_step = len(train_loader)
        for epoch in range(num_epochs):
            for i, (images, labels) in enumerate(train_loader):
                outputs = model(images)
                loss = criterion(outputs, labels)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if (i + 1) % 100 == 0:
                    print(f'Epoch [{epoch + 1}/{num_epochs}], Step [{i + 1}/{total_step}], Loss: {loss.item():.4f}')
        print("模型重新训练完成。")


root = tk.Tk()
root.title("鼠标书写并预测")
sketchpad = Sketchpad(root)
root.bind("<Return>", sketchpad.save_and_predict)
root.mainloop()