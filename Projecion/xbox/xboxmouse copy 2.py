import inputs
import pygame
import pyautogui
import math
import time
from threading import Thread

# 配置参数
MOUSE_SPEED = 25          # 基础鼠标移动速度
SCROLL_SPEED = 15         # 滚动速度
DEADZONE = 0.15           # 摇杆死区
SMOOTHING = 0.5           # 平滑系数 (0-1, 越大越平滑)
POLL_RATE = 120           # 输入检测频率 (Hz)
BUTTON_POLL_RATE = 60     # 按钮检测频率 (Hz)

# 按钮映射 (使用pygame的按钮编号)
BUTTON_MAP = {
    0: 'left',    # A按钮
    1: 'right',   # B按钮
    2: 'middle',  # X按钮
    3: None,      # Y按钮
    6: 'exit',    # 菜单按钮
    7: None       # 视图按钮
}

class XboxController:
    def __init__(self):
        # 初始化inputs手柄
        self.gamepad = inputs.devices.gamepads[0]
        self.running = True
        self.state = {
            'ABS_X': 0,      # 左摇杆X
            'ABS_Y': 0,      # 左摇杆Y
            'ABS_RX': 0,     # 右摇杆X
            'ABS_RY': 0      # 右摇杆Y
        }
        self.smooth_x = 0
        self.smooth_y = 0
        
    def apply_deadzone(self, value):
        if abs(value) < DEADZONE * 32768:
            return 0
        return value / 32768.0
    
    def process_joystick(self):
        while self.running:
            try:
                events = self.gamepad.read()
                for event in events:
                    if event.ev_type == 'Absolute' and event.code in self.state:
                        self.state[event.code] = event.state
            except inputs.UnpluggedError:
                print("手柄断开连接")
                self.running = False
            except Exception as e:
                print(f"摇杆读取错误: {e}")
                self.running = False
    
    def get_smooth_movement(self):
        # 应用死区
        raw_x = self.state['ABS_X']
        raw_y = self.state['ABS_Y']
        x = self.apply_deadzone(raw_x)
        y = self.apply_deadzone(raw_y)
        
        # 平滑处理
        self.smooth_x = self.smooth_x * SMOOTHING + x * (1 - SMOOTHING)
        self.smooth_y = self.smooth_y * SMOOTHING + y * (1 - SMOOTHING)
        
        # 非线性加速
        magnitude = math.sqrt(self.smooth_x**2 + self.smooth_y**2)
        if magnitude > 0:
            scale = magnitude ** 1.5 * MOUSE_SPEED / magnitude
            return self.smooth_x * scale, self.smooth_y * scale
        return 0, 0
    
    def stop(self):
        self.running = False

class ButtonMonitor:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise Exception("未检测到手柄连接!")
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.running = True
        self.button_state = {btn: False for btn in BUTTON_MAP}
        self.prev_button_state = self.button_state.copy()
    
    def process_buttons(self):
        while self.running:
            pygame.event.pump()
            
            # 更新按钮状态
            for btn, action in BUTTON_MAP.items():
                self.button_state[btn] = self.joystick.get_button(btn)
            
            time.sleep(1/BUTTON_POLL_RATE)
    
    def stop(self):
        self.running = False
        pygame.quit()

def main():
    try:
        # 初始化控制器
        controller = XboxController()
        button_monitor = ButtonMonitor()
        
        # 启动线程
        joy_thread = Thread(target=controller.process_joystick)
        btn_thread = Thread(target=button_monitor.process_buttons)
        
        joy_thread.daemon = True
        btn_thread.daemon = True
        
        joy_thread.start()
        btn_thread.start()
        
        print("Xbox手柄鼠标控制已启动 (按菜单按钮退出)")
        
        last_scroll_time = 0
        scroll_interval = 0.1  # 滚动间隔(秒)
        
        while controller.running and button_monitor.running:
            current_time = time.time()
            
            # 处理鼠标移动
            move_x, move_y = controller.get_smooth_movement()
            if move_x != 0 or move_y != 0:
                x, y = pyautogui.position()
                pyautogui.moveTo(x + move_x, y + move_y, _pause=False)
            
            # 处理滚动 (带节流)
            if current_time - last_scroll_time > scroll_interval:
                scroll_y = -controller.apply_deadzone(controller.state['ABS_RY'])
                if abs(scroll_y) > 0:
                    pyautogui.scroll(int(scroll_y * SCROLL_SPEED), _pause=False)
                    last_scroll_time = current_time
            
            # 处理按钮动作
            for btn, action in BUTTON_MAP.items():
                if action:
                    current_state = button_monitor.button_state[btn]
                    prev_state = button_monitor.prev_button_state.get(btn, False)
                    
                    if current_state and not prev_state:
                        if action == 'exit':
                            print("退出程序")
                            controller.stop()
                            button_monitor.stop()
                            return
                        pyautogui.mouseDown(button=action, _pause=False)
                    elif not current_state and prev_state:
                        if action != 'exit':
                            pyautogui.mouseUp(button=action, _pause=False)
            
            button_monitor.prev_button_state = button_monitor.button_state.copy()
            
            # 控制循环频率
            time.sleep(1/POLL_RATE)
    
    except KeyboardInterrupt:
        print("用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        controller.stop()
        button_monitor.stop()
        joy_thread.join(timeout=1)
        btn_thread.join(timeout=1)
        print("程序已退出")

if __name__ == "__main__":
    # 检查是否连接了手柄
    if not inputs.devices.gamepads:
        print("未检测到手柄连接!")
        exit(1)
    
    # 设置pyautogui安全措施
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    
    main()