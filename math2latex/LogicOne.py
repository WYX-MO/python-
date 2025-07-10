import math
import cv2
import numpy as np
from PIL import Image, ImageDraw
class LogicHandler:
    def __init__(self,image):
        self.image = image

    def show(self,img,name='image'):
        cv2.imshow('image',img)
        cv2.waitKey(0)#0為不自動消失,按任意鍵消失,單位毫秒
        cv2.destroyAllWindows()
    
    def PixelProjection(self,imageToProjection,threshold = 10):#像素投影法
        img = imageToProjection.copy()
        img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]  # 二值化处理
        inf =0
        result4Num = [inf]*img.shape[1]#初始化结果数组
        result4Ratio = [inf]*img.shape[1]#初始化结果数组
        reslut4Max=[inf]*img.shape[1]#初始化结果数组

        for i in range(img.shape[0]):#遍历每一行
            for j in range(img.shape[1]):#遍历每一列
                if img[i][j]==0:
                    result4Num[j]+=1
            result4Ratio[i]=result4Num[i]/img.shape[0]

        cur_max =0
        cur = 0 
        for i in range(img.shape[0]):#遍历每一行
            for j in range(img.shape[1]):#遍历每一列
                if img[i][j] == 0:
                    cur += 1
                else:
                    if cur_max < cur:
                        cur_max = cur
                    cur = 0
        
        cv2.line(img,(result4Num.index(min(result4Num)),img.shape[1]),(result4Num.index(min
        (result4Num)),0),(0,0,255),1)#画一条线
        self.show(img)
            
    def basicInfomationAndOperation(self):
        _, self.image = cv2.threshold(self.image, 127, 255, cv2.THRESH_BINARY)  # Properly unpack threshold result
        self.show(self.image)
        #腐蚀操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 定义结构元素
        image = cv2.erode(self.image, kernel)  # 腐蚀操作
        #开操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))  # 定义结构元素
        image_ = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)  # 开操作
        #腐蚀操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (32, 32))  # 定义结构元素
        image_ = cv2.erode(image_, kernel)  # 腐蚀操作
        _, image_ = cv2.threshold(image_, 50, 255, cv2.THRESH_BINARY)  # Properly unpack threshold result

        contours,hierarchy = cv2.findContours(image_, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if(len(contours)==0):
            print("未找到轮廓")
            return
        cnt = contours[0]
        image_ = cv2.cvtColor(image_, cv2.COLOR_GRAY2BGR)  # Convert grayscale image to BGR for drawing
        new_contours = []
        
        for i in range(len(contours)):
            cnt = contours[i]
            mask = np.zeros((image_.shape[0], image_.shape[1]), dtype=np.uint8)
            # 在掩膜上绘制轮廓内部
            cv2.drawContours(mask, cnt, 0, 255, -1)  # -1表示填充轮廓内部
            mean_val = cv2.mean(image_, mask=mask)[0]
            area = cv2.contourArea(cnt)

            if area>=1000 and mean_val>127:#筛除面积较小的块和内部空心的块
                new_contours.append(cnt)

        for i in range(len(new_contours)):# Draw the contour on the image
            cnt = new_contours[i]
            cv2.drawContours(image_, [cnt], -1, (0, 255,0), 2)  
            cv2.putText(image_,str(cv2.contourArea(cnt)),(cnt[0][0][0],cnt[0][0][1]),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)  # Draw the contour on the image
            x, y, w, h = cv2.boundingRect(cnt)
            image_ = cv2.rectangle(image_, (x, y), (x + w, y + h), (0, 0, 255), 1)
        self.show(image_)
      #======================================完成基本分块=======================================
        # 裁剪出数字区域
        img_crop =[]
        for i in range(len(new_contours)):
            cnt = new_contours[i]
            x, y, w, h = cv2.boundingRect(cnt)
            
            img_crop.append(image[y:y + h, x:x + w])  # 裁剪出数字区域
            #self.show(img_crop[i])
            #self.PixelProjection(img_crop[i])
        self.operator4img_crop(img_crop)
    def operator4img_crop(self,img_crop = []):#对裁剪出的数字区域进行操作
        for i in range(len(img_crop)):
            image = img_crop[i]
            self.show(image)
            
            # #腐蚀操作
            # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 定义结构元素
            # image = cv2.erode(image, kernel)  # 腐蚀操作

            # # #腐蚀操作
            # # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (32, 32))  # 定义结构元素
            # # image_ = cv2.erode(image_, kernel)  # 腐蚀操作
            # _, image_ = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)  # Properly unpack threshold result

            # contours,hierarchy = cv2.findContours(image_, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            # if(len(contours)==0):
            #     print("未找到轮廓")
            #     return
            # cnt = contours[0]
            # image_ = cv2.cvtColor(image_, cv2.COLOR_GRAY2BGR)  # Convert grayscale image to BGR for drawing
            # new_contours = []
            
            # for i in range(len(contours)):
            #     cnt = contours[i]
            #     mask = np.zeros((image_.shape[0], image_.shape[1]), dtype=np.uint8)
            #     # 在掩膜上绘制轮廓内部
            #     cv2.drawContours(mask, cnt, 0, 255, -1)  # -1表示填充轮廓内部
            #     mean_val = cv2.mean(image_, mask=mask)[0]
            #     area = cv2.contourArea(cnt)

            #     if area>=1000 and mean_val>127:#筛除面积较小的块和内部空心的块
            #         new_contours.append(cnt)

            # for i in range(len(new_contours)):# Draw the contour on the image
            #     cnt = new_contours[i]
            #     cv2.drawContours(image_, [cnt], -1, (0, 255,0), 2)  
            #     cv2.putText(image_,str(cv2.contourArea(cnt)),(cnt[0][0][0],cnt[0][0][1]),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)  # Draw the contour on the image
            #     x, y, w, h = cv2.boundingRect(cnt)
            #     image_ = cv2.rectangle(image_, (x, y), (x + w, y + h), (0, 0, 255), 1)
            # self.show(image_)


image = cv2.imread('E:\\pyLearn\\imgs\\train\\example.jpg', cv2.IMREAD_GRAYSCALE)
lh = LogicHandler(image)
lh.basicInfomationAndOperation()






