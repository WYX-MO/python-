import cv2
import numpy as np

# 1. 读取图像（请替换为你的图片路径）
image = cv2.imread('E:\\pyLearn\\codes\\Projecion\\comic copy\\imgs\\t1.png')  
if image is None:
    print("无法读取图像，请检查路径是否正确")
    exit()

# 转为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  

# 2. 二值化（根据图像调整阈值）
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)  

# 3. 寻找轮廓
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  

# 4. 遍历轮廓，找到最小外接矩形
min_rect = None
for cnt in contours:
    # 使用 np.intp 替代已弃用的 np.int0
    rect = cv2.minAreaRect(cnt)  
    box = cv2.boxPoints(rect)  
    box = np.intp(box)  # 修复1：替换 np.int0 为 np.intp
    
    # 简单过滤小轮廓（可选优化）
    if cv2.contourArea(box) > 100:  # 只考虑面积大于100的轮廓
        if min_rect is None or cv2.contourArea(box) < cv2.contourArea(min_rect):  
            min_rect = box

# 5. 裁剪图像
if min_rect is not None:
    x_min = np.min(min_rect[:, 0])
    x_max = np.max(min_rect[:, 0])
    y_min = np.min(min_rect[:, 1])
    y_max = np.max(min_rect[:, 1])
    
    # 确保裁剪区域有效
    if x_max > x_min and y_max > y_min:  # 修复2：添加有效性检查
        cropped_image = image[y_min:y_max, x_min:x_max]  
        
        # 显示或保存结果
        cv2.imshow('Cropped Image', cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # cv2.imwrite('cropped_result.png', cropped_image)
    else:
        print("裁剪区域无效：宽度或高度为0")
else:
    print("未检测到有效轮廓，无法裁剪")
    # 可选：显示二值化结果，帮助调试
    cv2.imshow('Threshold Result', thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()