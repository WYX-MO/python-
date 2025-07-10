import os
import tkinter as tk
from PIL import Image, ImageDraw
import cv2
import numpy as np

# 定义 Sketchpad 类：用于手写输入界面的绘制与预测功能
class Sketchpad:
    def __init__(self, parent, width=400, height=400):
        self.parent = parent  # 保存父窗口引用
        self.pencoler = "black"  # 初始画笔颜色为黑色
        # 创建画布组件（白色背景，用于手写绘制）
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='white')
        self.canvas.pack()  # 将画布添加到父窗口中
        # 绑定鼠标左键拖动事件到绘制方法（实现边拖动画笔）
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<B3-Motion>", self.dedraw)
        # 绑定回车键到保存并预测方法（触发结果预测）
        self.canvas.bind("<Return>", self.save_and_label)
        
        # 创建PIL图像对象（用于保存手写轨迹的原始数据，L模式表示8位灰度图）
        self.image = Image.new("L", (width, height), color=255)  # 初始化为全白背景
        self.draw = ImageDraw.Draw(self.image)  # 创建PIL的绘制工具对象
        
        # 新增一个变量，用于存储按钮点击状态
        self.button_clicked = -1
        self.chars = ['plus','minus','multiplication','division','ntegral','divide','derivative','pi','Euler','square_root','example']
        charsNum = self.chars.__len__()
        self.index=[0]*charsNum
        # 创建按钮并绑定点击事件
        for i in range(charsNum): 
            button = tk.Button(parent, text=self.chars[i], command=lambda i=i: self.on_button_click(i))
            button.pack(side=tk.LEFT)  # 将按钮添加到父窗口左侧
        # self.button = tk.Button(parent, text="点击改变变量值", command=self.on_button_click)
        # self.button.pack()

    def show(self,img):
        cv2.imshow('image',img)
        cv2.waitKey(0)#0為不自動消失,按任意鍵消失,單位毫秒
        cv2.destroyAllWindows()
    def dedraw(self, event):
        x,y = event.x, event.y
        r = 13
        self.pencoler = "white"
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.pencoler,outline= self.pencoler)
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill=255,outline=255)

    def draw(self, event):
        # 获取鼠标当前坐标
        x, y = event.x, event.y
        r = 6  # 笔刷半径（控制绘制点的大小）
        self.pencoler = "black"
        # 在Tkinter画布上绘制实心椭圆（模拟笔刷轨迹）
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.pencoler,outline=self.pencoler)
        # 在PIL图像上同步绘制椭圆（保存为模型输入的原始数据）
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill=0,outline=0)  # fill=0表示黑色（0为灰度最小值）

    def save_and_label(self, i, event=None):
        image = cv2.threshold(np.array(self.image), 127, 255, cv2.THRESH_BINARY)[1]  # 二值化处理
        image = cv2.resize(image, (32, 32))  # 调整图像大小为32x32像素
        image = cv2.bitwise_not(image)  # 反转图像颜色（黑变白，白变黑）
        # 确保图像是单通道 8 位无符号整数类型，并且不改变其维度
        image = image.astype(np.uint8)
        
        contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # 找轮廓
        
        if len(contours) == 0:
            print("未找到轮廓")
            return
        
        cnt = contours[0]
        # 将图像转换为彩色图像以便绘制彩色轮廓
        #image_ = cv2.resize(image, (320, 320))
        image_ = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1]  # 二值化处理
        #self.show(image_)

        img_cot = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        res = cv2.drawContours(img_cot, [cnt], -1, (0, 0, 255), 1)  # 画轮廓
        #res  = cv2.resize(res, (320, 320))
        #self.show(res)
        #没什么卵用
        # epsilon = 0.1 * cv2.arcLength(cnt, True)  # 用周长的倍数做分割的阈值
        # approx = cv2.approxPolyDP(cnt, epsilon, True)  # 轮廓近似,获得轮廓转折点
        # img_cot_approx = img_cot.copy()
        # res2 = cv2.drawContours(img_cot_approx, [approx], -1, (0, 0, 255), 1)
        # res2 = cv2.resize(res2, (320, 320))
        # self.show(res2)
        
        x, y, w, h = cv2.boundingRect(cnt)
        w = max(w, h)
        img_rect = cv2.rectangle(img_cot, (x, y), (x + w, y + w), (0, 255, 0), 1)
        #img_rect = cv2.resize(img_rect, (320, 320))
        #self.show(img_rect)

        # 裁剪出数字区域
        img_crop = image[y:y + w, x:x + w]
        #img_crop = image[y-2:y + w+2, x-2:x + w+2]
        img_crop = cv2.resize(img_crop, (32, 32))  # 调整图像大小为32x32像素
        img_crop = cv2.bitwise_not(img_crop)  # 反转图像颜色（黑变白，白变黑）
        img_crop = cv2.threshold(img_crop, 127, 255, cv2.THRESH_BINARY)[1]  # 二值化处理

        # 创建目录
        save_dir = f"E:\\pyLearn\\imgs\\train\\{self.chars[i]}"
        os.makedirs(save_dir, exist_ok=True)

        # 保存图片
        cv2.imwrite(f"{save_dir}\\{self.index[i]}.jpg", img_crop)
        self.index[i]+=1

        img_crop = cv2.resize(img_crop, (320, 320))  # 调整图像大小为32x32像素
        #self.show(img_crop)
    
    def on_button_click(self,i):
                self.button_clicked = i
                print(f"按钮已点击，button_clicked 的值为: {self.button_clicked}")
                self.save_and_label(i)
                self.clear_canvas()


    def clear_canvas(self):
        """清空 Tkinter 画布和 PIL 图像"""
        # 清空 Tkinter 画布
        self.canvas.delete("all")
        # 重新创建一个全白的 PIL 图像
        self.image = Image.new("L", (self.canvas.winfo_width(), self.canvas.winfo_height()), color=255)
        self.draw = ImageDraw.Draw(self.image)

root = tk.Tk()
root.title("鼠标书写并预测")
sketchpad = Sketchpad(root)
root.bind("<Return>", sketchpad.save_and_label)
root.mainloop()


        