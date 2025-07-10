# import torch as t
# import numpy as np
# from matplotlib import pyplot as plt
# from IPython import display
#
# device = t.device('cpu')
# #%%
# t.manual_seed(2021)
# #%%
# def get_fake_data(batch_size):
#     x = t.rand(batch_size,1,device = device)*5
#     y = x*2+3+t.randn(batch_size,1,device=device)
#     return x,y
# #%%
# x,y = get_fake_data(batch_size = 16)
# plt.scatter(x.squeeze().cp
import pyautogui

# import speech_recognition as sr
#
# r = sr.Recognizer()
# with sr.Microphone() as source:
#     print("请说话...")
#     audio = r.listen(source)
#
# try:
#     # 使用 PocketSphinx 进行识别
#     text = r.recognize_sphinx(audio)#, language='zh-CN'
#     print(f"识别结果: {text}")
# except sr.UnknownValueError:
#     print("无法识别语音")
# except sr.RequestError as e:
#     print(f"请求错误; {e}")

# import cv2
# import mediapipe as mp
#
# # 初始化 MediaPipe Hands 模块
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
# mp_drawing = mp.solutions.drawing_utils
#
# # 打开摄像头
# cap = cv2.VideoCapture(0)
#
# while cap.isOpened():
#     success, image = cap.read()
#     if not success:
#         print("无法读取摄像头图像。")
#         continue
#
#     # 转换图像颜色空间
#     image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
#     image.flags.writeable = False
#     results = hands.process(image)
#     image.flags.writeable = True
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#
#     if results.multi_hand_landmarks:
#         for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
#             # 获取左右手信息
#             hand_label = handedness.classification[0].label
#             # 绘制手部关键点
#             mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
#             # 在图像上显示左右手信息
#             h, w, c = image.shape
#             text_x = int(hand_landmarks.landmark[0].x * w)
#             text_y = int(hand_landmarks.landmark[0].y * h)
#             cv2.putText(image, hand_label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#
#     cv2.imshow('MediaPipe Hands', image)
#     if cv2.waitKey(5) & 0xFF == 27:
#         break
#
# cap.release()
# cv2.destroyAllWindows()

# import speech_recognition as sr
# import threading
# import time
#
# # 语音识别线程函数
# def speech_recognition_thread():
#     r = sr.Recognizer()
#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("请说话...")
#                 audio = r.listen(source)
#             # 使用 PocketSphinx 进行识别
#             text = r.recognize_sphinx(audio)
#             print(f"识别结果: {text}")
#         except sr.UnknownValueError:
#             print("无法识别语音")
#         except sr.RequestError as e:
#             print(f"请求错误; {e}")
#
# # 另一个线程函数，这里简单示例每秒打印当前时间
# def another_thread():
#     while True:
#         current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         print(f"当前时间: {current_time}")
#         time.sleep(1)
#
# if __name__ == "__main__":
#     # 创建并启动语音识别线程
#     speech_thread = threading.Thread(target=speech_recognition_thread)
#     speech_thread.start()
#
#     # 创建并启动另一个线程
#     other_thread = threading.Thread(target=another_thread)
#     other_thread.start()
#
#     # 等待线程结束（这里由于是无限循环，不会自然结束）
#     speech_thread.join()
#     other_thread.join()
#

# import subprocess
#
# # 启动第一个程序
# process1 = subprocess.Popen(['python','Sounds.py'])
#
# # 启动第二个程序
# process2 = subprocess.Popen(['python','Hands.py'])
#
# # 等待两个程序执行完毕（可选，根据需要）
# process1.wait()
# process2.wait()
#
# print("两个程序都已执行完毕")

# import ctypes
# # import time
# # import struct
# #
# # # 定义常量
# # INPUT_MOUSE = 0
# # MOUSEEVENTF_MOVE = 0x0001
# #
# # # 定义结构体
# # class MOUSEINPUT(ctypes.Structure):
# #     _fields_ = [
# #         ("dx", ctypes.c_long),
# #         ("dy", ctypes.c_long),
# #         ("mouseData", ctypes.c_ulong),
# #         ("dwFlags", ctypes.c_ulong),
# #         ("time", ctypes.c_ulong),
# #         ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
# #     ]
# #
# # class INPUT(ctypes.Structure):
# #     class _INPUT(ctypes.Union):
# #         _fields_ = [
# #             ("mi", MOUSEINPUT),
# #         ]
# #     _anonymous_ = ("_input",)
# #     _fields_ = [
# #         ("type", ctypes.c_ulong),
# #         ("_input", _INPUT)
# #     ]
# #
# # def send_mouse_move(dx, dy):
# #     mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
# #     inp = INPUT(type=INPUT_MOUSE, mi=mi)
# #     ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
# #
# # def smooth_move(dx, dy, steps=10, interval=0.01):
# #     step_x = dx / steps
# #     step_y = dy / steps
# #     for _ in range(steps):
# #         send_mouse_move(int(step_x), int(step_y))
# #         time.sleep(interval)
# #
# # # 等待一段时间，方便切换到游戏窗口
# #
# #
# # # 视角移动示例
# # smooth_move(100, 0)
# # time.sleep(1)
# # smooth_move(-100, 0)
# # time.sleep(1)
# # smooth_move(0, -100)
# # time.sleep(1)
# # smooth_move(0, 100)

# import threading
#
# # 共享资源
# counter = 0
# # 创建锁对象
# lock = threading.Lock()
#
# # 定义一个函数，作为线程要执行的任务
# def increment1():
#     a=0
#     while(True):
#         a+=1
# def increment2():
#     global counter
#     for _ in range(100):
#         # 获取锁
#         lock.acquire()
#         try:
#             counter -= 1
#             print("increment2:",counter)
#         finally:
#             # 释放锁
#             lock.release()
# # 创建线程对象
# thread1 = threading.Thread(target=increment1)
# thread2 = threading.Thread(target=increment2)
#
# # 启动线程
# thread1.start()
# thread2.start()
#
# # 等待线程执行完毕
# thread1.join()
# thread2.join()
#
# print(f"最终结果: {counter}")

# while True:
#     print(pyautogui.position())#434 421     575 448
#     #400 420   425 450
#     #1537 1398

# pyautogui.scroll(-10000)

from ultralytics import YOLO
import cv2

# 加载预训练的YOLOv8模型
model = YOLO('yolov8n.pt')

# 读取本地图像文件
cap = cv2.VideoCapture(0) # 请替换为实际的图像文件路径
while(True):
    ret,image = cap.read()
    if ret:

        if image is None:
            print("无法读取图像，请检查文件路径。")
        else:
            # 使用模型进行目标检测
            results = model.predict(image)

            # 遍历检测结果
            for result in results:
                boxes = result.boxes  # 边界框信息
                for box in boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    # 获取类别ID和置信度
                    class_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[class_id]

                    # 在图像上绘制边界框和标签
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f'{class_name}: {conf:.2f}'
                    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 显示结果图像
            cv2.imshow('YOLOv8 Object Detection', image)
            if cv2.waitKey(1) & 0xFF == 27:
                break


















