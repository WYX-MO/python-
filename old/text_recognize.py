import cv2
import numpy
import numpy as np
import math
import pytesseract
import os
from PIL import Image
from cv2 import findContours


#自定義的庫
def show(image, window_name='Image'):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize(image, width=None, height=None):
    if width is None and height is None:
        return image
    if width is None:
        ratio = height / image.shape[0]
        dim = (int(image.shape[1] * ratio), height)
    else:
        ratio = width / image.shape[1]
        dim = (width, int(image.shape[0] * ratio))
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


def get_contour_area(contour):
    return cv2.contourArea(contour)


def sort_contours(cnts, method="right-to-left"):
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    if method == "left-toright" or method == "top-to-bottom":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]  # 機損外接矩形
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))

    return cnts, boundingBoxes


def four_point_transform(img, pts):
    rect = order_four_points(pts)
    # 确保 rect 是 float32 类型
    rect = rect.astype(np.float32)
    (tl, tr, br, bl) = rect

    w1 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    w2 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    final_w = max(int(w1), int(w2))

    h1 = np.sqrt(((br[0] - tr[0]) ** 2) + ((br[1] - tr[1]) ** 2))
    h2 = np.sqrt(((bl[0] - tl[0]) ** 2) + ((bl[1] - tl[1]) ** 2))
    final_h = max(int(h1), int(h2))

    # 修正 dst 点的顺序并确保是 float32 类型
    dst = np.array([
        [0, 0],
        [final_w - 1, 0],
        [final_w - 1, final_h - 1],
        [0, final_h - 1]
    ], dtype=np.float32)
    print(dst.shape)
    M = cv2.getPerspectiveTransform(rect, dst)
    res = cv2.warpPerspective(img, M, (final_w, final_h))
    return res

def order_four_points(pts):
    pts = np.array(pts)  # 确保 pts 是 numpy 数组
    x_sorted = pts[np.argsort(pts[:, 0])]

    leftmost = x_sorted[:2]
    rightmost = x_sorted[2:]

    leftmost = leftmost[np.argsort(leftmost[:, 1])]
    rightmost = rightmost[np.argsort(rightmost[:, 1])]

    tl, bl = leftmost
    tr, br = rightmost

    ordered_pts = np.array([tl, tr, br, bl], dtype=np.float32)
    return ordered_pts


#every thing in this path:  C:/Users/17396/pyLearn/
# text = pytesseract.image_to_string(Image.open("C:/Users/17396/pyLearn/OpenCV.png"))
# print(text)

img = cv2.imread('C:/Users/17396/pyLearn/imgs/opencv.png')
ratio = img.shape[0]/500.0
img_ = img.copy()

high = int((img_.shape[0])*(500/img_.shape[1]))

img = cv2.resize(img_,(500,high))
img_ = img.copy()
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
show(gray)
img = cv2.GaussianBlur(gray,(5,5),0)
show(img)
img = cv2.Canny(img,100,170)
show(img)

cnts = findContours(img.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[1]
cnts = sorted(cnts, key=get_contour_area, reverse=True)[:5]


for c in cnts:
    C = cv2.arcLength(c,True)
    approx = cv2.approxPolyDP(c,0.02*C,True)

    if len(approx) == 4:
        screenCnts = approx
        break
test = cv2.drawContours(img,screenCnts,-1,(0,0,255),3)
show(test)
img_after_perspectiveTransform = four_point_transform(img_, screenCnts.reshape(4,2))
show(img_after_perspectiveTransform)

gray_after_perspective = cv2.cvtColor(img_after_perspectiveTransform,cv2.COLOR_BGR2GRAY)
#形態學操作
img_binary = cv2.threshold(gray_after_perspective,127,255,cv2.THRESH_BINARY,)[1]
show(img_binary)
cv2.imwrite('C:/Users/17396/pyLearn/res_after_per.png', img_binary)
text = pytesseract.image_to_string(Image.open("C:/Users/17396/pyLearn/res_after_per.png"))
print(text)