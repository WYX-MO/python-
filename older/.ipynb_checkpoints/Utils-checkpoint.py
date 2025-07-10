# myutils.py
import cv2
import math

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

def sort_contours(cnts,method ="right-to-left"):
    reverse = False
    i =0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse =  True

    if method == "left-toright" or method == "top-to-bottom":
        i =1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]#機損外接矩形
    (cnts,boundingBoxes)=zip(*sorted(zip(cnts,boundingBoxes),key = lambda b:b[1][i],reverse=reverse))

    return cnts,boundingBoxes

def four_point_transform(img,pts):
    rect = order_four_points(pts)
    (tl,tr,br,bl) = rect

    w1 = np.sqrt(((br[0]-bl[0])**2)+((br[1]-bl[1])**2))
    w2 = np.sqrt(((tr[0]-tl[0])**2)+((tr[1]-tl[1])**2))
    final_w = max(int(w1),int(w2))
    
    h1 = np.sqrt(((br[0]-tr[0])**2)+((br[1]-tr[1])**2))
    h2 = np.sqrt(((bl[0]-tl[0])**2)+((bl[1]-tl[1])**2))
    final_h = max(int(h1),int(h2))
    return final_w,final_h




def order_four_points(pts):
    pts = sorted(pts, key=lambda x: x[0])
    left_pts = sorted(pts[:2], key=lambda x: x[1])
    right_pts = sorted(pts[2:4], key=lambda x: x[1], reverse=True)
    ordered_pts = [left_pts[0], right_pts[0], right_pts[1], left_pts[1]]
    
    return ordered_pts
    





