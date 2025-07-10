import pyautogui as pag
import time
import cv2
import numpy as np
import pytesseract

#from codes.ai import img_p


def moveAndClick(x,y):
    pag.moveTo(x,y)
    pag.click()

screen_width, screen_height = pag.size()

def is_green_dominant(im, threshold=0.3):
    try:
        # 读取图像
        image = im

        # 将图像转换为 HSV 颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 定义绿色的 HSV 范围
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])

        # 创建掩码，筛选出绿色区域
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 统计绿色像素数量
        green_pixel_count = cv2.countNonZero(mask)

        # 计算图像总像素数量
        total_pixel_count = image.shape[0] * image.shape[1]

        # 计算绿色像素比例
        green_ratio = green_pixel_count / total_pixel_count

        # 判断绿色像素比例是否超过阈值
        #print(green_ratio)
        return green_ratio > threshold

    except Exception as e:
        print(f"出现错误: {e}")
        return False
def is_yellow_dominant(im, threshold=0.2):
    try:
        # 读取图像
        image =im


        # 将图像转换为 HSV 颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 定义黄色的 HSV 范围
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])

        # 创建掩码，筛选出黄色区域
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 统计黄色像素数量
        yellow_pixel_count = cv2.countNonZero(mask)

        # 计算图像总像素数量
        total_pixel_count = image.shape[0] * image.shape[1]

        # 计算黄色像素比例
        yellow_ratio = yellow_pixel_count / total_pixel_count

        # 判断黄色像素比例是否超过阈值
        #print(yellow_ratio)
        return yellow_ratio > threshold
    except Exception as e:
        print(f"出现错误: {e}")
        return False

def main():
    next = 0
    th=0
    while True:
        # 获取桌面截图
        screenshot = pag.screenshot()
        # 将截图转换为 OpenCV 可以处理的格式
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        #400 420   425 450
        fi = screenshot[420:450,400:430]
        resize_img = cv2.resize(fi, (30, 30))
        is_green = is_green_dominant(resize_img)
        is_yellow = is_yellow_dominant(resize_img)

        if next ==1:
            pag.scroll(100)
            time.sleep(1)
            moveAndClick(1070,845)
            next=0

        if not(is_green or is_yellow):
            th+=1
            print(th)
            if th>40:
                th=0
                pag.scroll(-10000)
                time.sleep(2)
                moveAndClick(1525, 1362)
                time.sleep(2)
                moveAndClick(1600, 850)
                next=1
        if is_green:
            next=1
            # 1522 1515
            moveAndClick(1520,1515)
            # 1537 1398
            time.sleep(2)
            moveAndClick(1520, 1380)
            time.sleep(2)
            moveAndClick(1600, 850)

        cv2.imshow('Processed Desktop Image',fi)
        if cv2.waitKey(1) & 0xFF == 27:
            break


main()
