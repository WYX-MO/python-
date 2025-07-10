import pygame
import pyautogui
import time
import sys

# 初始化pygame和手柄
pygame.init()
pygame.joystick.init()

# 检查是否有连接的手柄
if pygame.joystick.get_count() == 0:
    print("未检测到手柄连接!")
    sys.exit()

# 初始化第一个手柄
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"已连接手柄: {joystick.get_name()}")

# 鼠标移动速度调节
MOUSE_SPEED = 10
SCROLL_SPEED = 2

# 死区阈值，避免摇杆微小移动导致鼠标抖动
DEADZONE = 0.2

# 按钮映射
BUTTON_LEFT = 0    # A按钮
BUTTON_RIGHT = 1   # B按钮
BUTTON_MIDDLE = 2  # X按钮
BUTTON_EXIT = 7    # 菜单按钮 (通常用于退出)

# 上一次的按钮状态
prev_button_states = {}

try:
    while True:
        pygame.event.pump()  # 处理事件队列
        
        # 获取左摇杆值用于鼠标移动
        axis_x = joystick.get_axis(0)  # 左摇杆X轴
        axis_y = joystick.get_axis(1)  # 左摇杆Y轴
        
        # 应用死区
        if abs(axis_x) < DEADZONE:
            axis_x = 0
        if abs(axis_y) < DEADZONE:
            axis_y = 0
        
        # 移动鼠标
        if axis_x != 0 or axis_y != 0:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + axis_x * MOUSE_SPEED, y + axis_y * MOUSE_SPEED)
        
        # 获取右摇杆值用于滚动
        scroll_x = joystick.get_axis(2)  # 右摇杆X轴
        scroll_y = joystick.get_axis(3)  # 右摇杆Y轴
        
        # 应用死区
        if abs(scroll_y) > DEADZONE:
            pyautogui.scroll(int(-scroll_y * SCROLL_SPEED))  # 上下滚动
        
        # 检查按钮状态
        current_button_states = {
            'left': joystick.get_button(BUTTON_LEFT),
            'right': joystick.get_button(BUTTON_RIGHT),
            'middle': joystick.get_button(BUTTON_MIDDLE),
            'exit': joystick.get_button(BUTTON_EXIT)
        }
        
        # 检测按钮按下事件
        if current_button_states['left'] and not prev_button_states.get('left', False):
            pyautogui.mouseDown(button='left')
        elif not current_button_states['left'] and prev_button_states.get('left', False):
            pyautogui.mouseUp(button='left')
            
        if current_button_states['right'] and not prev_button_states.get('right', False):
            pyautogui.mouseDown(button='right')
        elif not current_button_states['right'] and prev_button_states.get('right', False):
            pyautogui.mouseUp(button='right')
            
        if current_button_states['middle'] and not prev_button_states.get('middle', False):
            pyautogui.mouseDown(button='middle')
        elif not current_button_states['middle'] and prev_button_states.get('middle', False):
            pyautogui.mouseUp(button='middle')
        
        # 退出条件
        if current_button_states['exit']:
            print("退出程序")
            break
        
        # 更新按钮状态
        prev_button_states = current_button_states
        
        # 稍微延迟以减少CPU使用率
        time.sleep(0.01)

except KeyboardInterrupt:
    print("程序被用户中断")

finally:
    # 清理
    pygame.quit()
    print("程序退出")