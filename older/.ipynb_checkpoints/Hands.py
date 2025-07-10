import cv2
import mediapipe as mp
import time
import pyautogui
import pydirectinput
import pocketsphinx
import speech_recognition as sr

import ctypes
import time
import struct

from nltk.lm.api import Smoothing
from prompt_toolkit.key_binding.bindings import mouse

# 定义常量
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

# 定义结构体
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
        ]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT)
    ]

def send_mouse_move(dx, dy):
    mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
    inp = INPUT(type=INPUT_MOUSE, mi=mi)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
def smooth_move(dx, dy, steps=10, interval=0.01):
    step_x = dx / steps
    step_y = dy / steps
    for _ in range(steps):
        send_mouse_move(int(step_x), int(step_y))
        time.sleep(interval)

class Hands():
    def __init__(self,RL)->None:
        self.RL = RL
        self.all=[]
        self.fingerState =[0,0,0,0,0]
        self.Pposition=[0,0]
        self.Cposition=[0,0]
        self.direction=[0,0]
        self.speed=[0,0]
        self.finger3direction=[0,0]
    def trans_to_4dir(self,vector):
        if vector[0] != 0 and abs(vector[1] / vector[0]) < 0.8 and vector[0] > 0:
            return 'right'
        elif vector[0] != 0 and abs(vector[1] / vector[0]) < 0.8 and vector[0] < 0:
            return 'left'
        else:
            return 'None'

def fingerBool(all,RL,f):
    #dir is the direction of your palm
    dir = 1
    #f is the finger you want to know its statement,from 0 to 4 is from little to thumb
    if f == 0:
        fingertip = 20
    elif f == 1:
        fingertip = 16
    elif f == 2:
        fingertip = 12
    elif f == 3:
        fingertip = 8
    elif f == 4:
        fingertip = 4

    if all[9][1]>all[0][1] and all[5][1]>all[0][1]:
        dir = 1
    else:
        dir = -1

    if (all[fingertip][1]-all[fingertip-2][1])*dir<0:
        return 0;
    else:
        return 1

def anyDirfingerBool(all,RL,f):
    #dir is the direction of your palm
    dir = -[all[9][0] - all[0][0], all[9][1] - all[0][1]][1]
    #f is the finger you want to know its statement,from 0 to 4 is from little to thumb
    if f == 0:
        fingertip = 20
    elif f == 1:
        fingertip = 16
    elif f == 2:
        fingertip = 12
    elif f == 3:
        fingertip = 8
    elif f == 4:
        fingertip = 4
    vector1 = (all[fingertip][0] - all[fingertip - 2][0], all[fingertip][1] - all[fingertip - 2][1])
    vector2 = (all[fingertip - 2][0] - all[fingertip - 3][0], all[fingertip - 2][1] - all[fingertip - 3][1])
    if fingertip ==4:
        vector1 = (all[fingertip][0]-all[fingertip-1][0],all[fingertip][1]-all[fingertip-1][1])
        vector2 = (all[fingertip-2][0]-all[fingertip-3][0],all[fingertip-2][1]-all[fingertip-3][1])

    sita = vector1[0]*vector2[0]+vector1[1]*vector2[1]
    if sita<0 or (fingertip!=4 and vector1[1]*dir>0):
        return 0;
    else:
        return 1

#def palmState(all,RL):


#=================================Main===========================

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
r = sr.Recognizer()
mpDraw = mp.solutions.drawing_utils
handstyle1=mpDraw.DrawingSpec(color=(0,0,255 ),thickness=1,circle_radius=1)

screen_width, screen_height = pyautogui.size()

click_time =time.time()
Ptime =0
Ctime =0
thresh4mouseShake = 50
hand_l : Hands = Hands(0)
hand_r : Hands = Hands(1)
hand_n = Hands(1)
Pmouse_x=0
Pmouse_y=0
wasd = [0,0,0,0]
optimizer = 0
smoothing = 5

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    w = frame.shape[1]
    h = frame.shape[0]
    if ret:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(img)


        if(res.multi_hand_landmarks):
            #讀取雙手
            for hand, handedness in zip(res.multi_hand_landmarks, res.multi_handedness):
                #分辨左右手
                hand_label = handedness.classification[0].label
                #print(hand_label)

                mpDraw.draw_landmarks(frame, hand, mpHands.HAND_CONNECTIONS,handstyle1)
                all =[]
                #得到具體每個手指的信息
                for i,lm in enumerate(hand.landmark):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    #cv2.putText(frame,str(i),(x-25,y-5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
                    #print(i,lm.x, lm.y)
                    all.append([x,y])

                # 獲得整個手掌的信息

                # speed & position
                hand_n.all = all
                hand_n.Cposition = [all[8][0], all[8][1]]
                hand_n.speed = [hand_n.Cposition[0] - hand_n.Pposition[0], hand_n.Cposition[1] - hand_n.Pposition[1]]
                #print(hand_n.Cposition,hand_n.Pposition,hand_n.speed)
                hand_n.Pposition = hand_n.Cposition

                #print(hand_l.speed)
                #cv2.putText(frame, str(hand_n.speed), (all[0][0] + 25, all[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                hand_n.direction = [all[13][0] - all[0][0], all[13][1] - all[0][1]]

                if hand_label == 'Left':
                    hand_l = hand_n
                    hand_l.finger3direction = [all[8][0] - all[5][0], all[8][1] - all[5][1]]
                    cv2.putText(frame, str(hand_l.finger3direction), (all[0][0] + 25, all[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


                    #finger
                    for i in range(5):
                        if len(hand_l.all) == 21:
                            hand_l.fingerState[i] = anyDirfingerBool(all,hand_l,i)
                            cv2.putText(frame, str(hand_l.fingerState[i]), (100 + i * 20, 25), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2)


                    # print(hand_l.trans_to_4dir(hand_l.finger3direction))
                    if hand_l.trans_to_4dir(hand_l.finger3direction) == 'right':
                        if wasd[3] == 0:
                            wasd[3] = 1
                            print(2)
                            pyautogui.keyDown('d')
                    elif hand_l.trans_to_4dir(hand_l.finger3direction) == 'left':
                        if wasd[1] == 0:
                            wasd[1] = 1
                            print(1)
                            pyautogui.keyDown('a')
                    else:
                        if wasd != [0, 0, 0, 0]:
                            wasd = [0, 0, 0, 0]
                            print(3)
                            pyautogui.keyUp('d')
                            pyautogui.keyUp('a')

                elif hand_label == 'Right':
                    #hands
                    hand_r = hand_n
                    # finger
                    for i in range(5):
                        if len(hand_r.all) == 21:
                            hand_r.fingerState[i] = anyDirfingerBool(all, hand_l, i)
                            cv2.putText(frame, str(hand_r.fingerState[i]), (250 + i * 20, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5, (0, 0, 255), 2)

                    if hand_r.fingerState == [0, 0, 1, 1, 1] or hand_r.fingerState == [0, 0, 1, 1, 0]:
                        if time.time() - click_time > 1:
                            pyautogui.click()
                            click_time = time.time()

                    # 移动鼠标

                    #跟隨式,優化變量
                    _x = int((all[8][0] / frame.shape[1]) * screen_width)
                    _y = int((all[8][1] / frame.shape[0]) * screen_height)

                    Cmouse_x = Pmouse_x+(_x-Pmouse_x)/smoothing
                    Cmouse_y = Pmouse_y+(_y-Pmouse_y)/smoothing
                    #if (Cmouse_x - Pmouse_x) ** 2 + (Cmouse_y - Pmouse_y) ** 2 > thresh4mouseShake:

                    pyautogui.moveTo(Cmouse_x, Cmouse_y)#很卡,急需優化
                    #mouse.position = (Cmouse_x, Cmouse_y)
                    #
                    Pmouse_x = Cmouse_x
                    Pmouse_y = Cmouse_y

                    #滑動式
                    # cv2.putText(frame, str(hand_r.speed), (hand_r.all[0][0],hand_r.all[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
                    #             0.5, (0, 0, 255), 2)
                    # if hand_r.trans_to_4dir(hand_r.speed)=='right' and hand_r.speed[0]>30:
                    #     pyautogui.moveRel(100, 0, duration=0.1)
                    # if hand_r.trans_to_4dir(hand_r.speed) == 'left' and hand_r.speed[0]<-30:
                    #     pyautogui.moveRel(-100, 0, duration=0.1)

                    # #區域定位式
                    # cv2.line(frame, (450, 0), (450, 500), (0, 255, 0), 2)
                    # cv2.line(frame, (550, 0), (550, 500), (0, 255, 0), 2)
                    # cv2.line(frame, (450, 300), (550, 300), (255, 0, 0), 2)
                    # cv2.line(frame, (450, 400), (550, 400), (255, 0, 0), 2)
                    # #cv2.circle(frame, (550, 300), (550, 300), (255, 0, 0), 2)
                    # dpi =5
                    # vx =0
                    # vy =0
                    # if(hand_r.Cposition[0]>550):
                    #     vx = 5*dpi
                    # elif(hand_r.Cposition[0]<450):
                    #     vx = -5*dpi
                    # else:
                    #     vx = 0
                    # if (hand_r.Cposition[1]>400):
                    #     vy = 5*dpi
                    # elif (hand_r.Cposition[1]<300):
                    #     vy = -5*dpi
                    # else:
                    #     vy = 0
                    #
                    # optimizer+=1
                    # if optimizer % 4 ==0:
                    #     #pyautogui.moveRel(vx, vy, duration=0.1)
                    #     #pydirectinput.moveRel(vx, vy, duration=0.1)
                    #     smooth_move(vx,vy)



        Ctime = time.time()
        fps = int(1/(Ctime-Ptime))
        FPS = 'FPS: ' + str(fps)
        Ptime = Ctime
        cv2.putText(frame,str(FPS),(25,25),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

        cv2.imshow("img",frame)

        if cv2.waitKey(1) & 0xFF == 27 :
            break


