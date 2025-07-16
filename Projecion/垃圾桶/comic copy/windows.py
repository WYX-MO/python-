
import pytesseract
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv  # 新增：用于加载环境变量
import sys
import cv2
import numpy as np
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QFrame, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QCursor, QScreen, QImage, QPixmap

BLANK = 1
GAUSSIAN = 2
def show(img , name = "img"):
    cv2.imshow(name , img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def my_detect_text_boxes(image1):
    # nnn = image1.copy()

    i = image1.copy()
    gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)  # 灰度化
    ret, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
    #show(thresh,"thresh")  # 二值化
    kernel = np.ones((5, 5), np.uint8)
    img = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    #show(img,"open")  # 开
    # img = cv2.bitwise_not(img)
    img = img.astype(np.uint8)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # 找轮廓
    text_boxes = []
    image_ = img.copy()
    cv2.drawContours(image_, contours, -1, (0, 255, 0), 2)
    open2 = cv2.morphologyEx(image_, cv2.MORPH_OPEN, kernel)
    #show(open2,"open2")
    kernel = np.ones((1,9),np.uint8)
    erode = cv2.erode(open2,kernel, iterations=1)
    #show(erode,"erode")
    contours, _ = cv2.findContours(erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnts = []

    # nnn = erode.copy()
    # nnn = cv2.cvtColor(nnn,cv2.COLOR_GRAY2BGR)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        #print(img.size)
        if(float(w*h/img.size) >0.6):
            cnts.append(cnt)
            x,y,w,h = cv2.boundingRect(cnt)
            #cv2.rectangle(nnn,(x,y),(x+w,y+h),(255,0,0),2)
            #show(nnn)
        else:
            print("too small")
    
    areas = [cv2.contourArea(c) for c in cnts]
    sorted_idx = sorted(range(len(areas)), key=lambda i: areas[i], reverse=False)
    
    # 根据排序索引重新排列轮廓
    sorted_cnts = [cnts[i] for i in sorted_idx]
    cnts = sorted_cnts
    fl_cnts = []
    if cnts: 
        fl_cnts.append(cnts[0])
        for c1 in cnts:
            for c2 in fl_cnts:

                x1, y1, w1, h1 = cv2.boundingRect(c2)
                x2, y2, w2, h2 = cv2.boundingRect(c1)
                
                # 计算边界
                rect1_left = x1
                rect1_right = x1 + w1
                rect1_top = y1
                rect1_bottom = y1 + h1
                
                rect2_left = x2
                rect2_right = x2 + w2
                rect2_top = y2
                rect2_bottom = y2 + h2
                
                # 判断水平和垂直方向是否同时重叠
                horizontal_overlap = rect1_left < rect2_right and rect2_left < rect1_right
                vertical_overlap = rect1_top < rect2_bottom and rect2_top < rect1_bottom
                
                if not( horizontal_overlap and vertical_overlap):
                    fl_cnts.append(c1)

    image_with_boxes = image1.copy()
    type = BLANK
    if fl_cnts:
        for cnt in fl_cnts:
            x,y,w,h = cv2.boundingRect(cnt)
            image_with_boxes[y:y+h,x:x+w] = (255,255,255)
    else:
        type = GAUSSIAN
        # x,y,w,h = 0,0,image1.shape[1],image1.shape[0]
        # image_with_boxes[y:y+h,x:x+w] = (255,255,255)
        image_with_boxes = cv2.GaussianBlur(image_with_boxes,(3,3),0)

    return image1 , image_with_boxes, fl_cnts ,type

from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

def put_text_in_rectangle(img_cv2, text, rect, font_path="simhei.ttf",type = BLANK):
    textcolor = (0,0,0)
    if type == GAUSSIAN:
        textcolor = (0,0,0)
    """
    在OpenCV格式的图片的指定矩形区域内写入汉字
    
    参数:
    img_cv2: 输入的OpenCV图像（numpy数组，BGR格式）
    text: 要写入的汉字文本
    rect: 矩形区域 (x, y, width, height)
    font_path: 中文字体文件路径，默认使用系统中的黑体
    
    返回:
    result_img: 处理后的OpenCV图像
    """
    # 将OpenCV格式(BGR)转换为PIL格式(RGB)
    img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # 解析矩形参数
    x, y, w, h = rect

    #添加段落的分行
    words_per = int(pow(w/h*len(text),1/2))
    print(words_per)
    text = text.replace('\n','')
    text = ''.join(
        text[i:i+words_per] + '\n' 
        if i + words_per < len(text) 
        else text[i:] 
        for i in range(0, len(text), words_per)
    )

    # 加载字体
    try:
        font = ImageFont.truetype(font_path, size=30)
    except IOError:
        # 字体加载失败时的备选方案
        print(f"警告：无法加载字体 {font_path}，尝试使用系统字体")
        try:
            font = ImageFont.truetype("simhei.ttf", size=30)  # Windows
        except IOError:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttf", size=30)  # Linux
            except IOError:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=30)  # macOS
                except IOError:
                    print("警告：未找到中文字体，使用默认字体")
                    font = ImageFont.load_default()
    
    # 动态调整字体大小
    font_size = 30
    while True:
        test_font = ImageFont.truetype(font_path, font_size) if font_path else font
        
        # 根据Pillow版本选择计算文本尺寸的方法
        try:
            # 新版本 (>=10.0.0) 使用textbbox
            bbox = draw.textbbox((0, 0), text, font=test_font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # 旧版本使用textsize
            text_width, text_height = draw.textsize(text, font=test_font)
        
        if text_width > w * 0.9 or text_height > h * 0.9:
            font_size -= 1
            if font_size < 1:
                break
        else:
            break
    
    # 使用调整后的字体
    font = ImageFont.truetype(font_path, font_size) if font_path else font
    
    # 计算文字居中位置
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    text_x = x + (w - text_width) // 2
    text_y = y + (h - text_height) // 2
    
    # 写入文字（白色）
    draw.text((text_x, text_y), text, font=font, fill=textcolor)
    if type == GAUSSIAN:
        # 获取文字包围盒
        bbox = draw.textbbox((text_x, text_y), text, font=font)
        
        # 添加边距
        padding = 5
        bg_x = max(bbox[0] - padding, 0)
        bg_y = max(bbox[1] - padding, 0)
        bg_width = min(bbox[2] - bbox[0] + 2*padding, img_pil.width - bg_x)
        bg_height = min(bbox[3] - bbox[1] + 2*padding, img_pil.height - bg_y)
        
        # 绘制背景
        draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], fill=(255, 255, 255))
        draw.text((text_x, text_y), text, font=font, fill=textcolor)

    # 将PIL图像转回OpenCV格式(BGR)
    result_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return result_img


img = cv2.imread("E:\\pyLearn\\codes\\Projecion\\comic copy\\imgs\\t1.png")
#show(img)
cnts = []
img_o , img_b, cnts ,type= my_detect_text_boxes(img)
#show(img_b,"box")
if cnts:
    rect = cv2.boundingRect(cnts[0])
else:
    rect = 0,0,img.shape[1],img.shape[0]
img_t = put_text_in_rectangle(img_b,"你好,这中中s d\n中中中个世界！",rect,type = type)
show(img_t,"text")


