import inputs
import pyautogui
import math
import time
from threading import Thread




# 配置参数
MOUSE_SPEED = 25  # 基础鼠标移动速度
SCROLL_SPEED = 15  # 滚动速度
DEADZONE = 0.15  # 摇杆死区
SMOOTHING = 0.5  # 平滑系数 (0-1, 越大越平滑)
POLL_RATE = 200  # 输入检测频率 (Hz)

# 按钮映射 (Xbox One 手柄)
BUTTON_MAP = {
    'BTN_SOUTH': 'left',    # A按钮
    'BTN_EAST': 'right',    # B按钮
    'BTN_WEST': 'middle',   # X按钮
    'BTN_NORTH': None,      # Y按钮
    'BTN_SELECT': None,     # 视图按钮
    'BTN_START': 'exit',    # 菜单按钮
    'BTN_THUMBL': None,     # 左摇杆按下
    'BTN_THUMBR': None      # 右摇杆按下
}

class XboxController:
    def __init__(self):
        self.gamepad = inputs.devices.gamepads[0]
        self.running = True
        self.state = {
            'ABS_X': 0,      # 左摇杆X
            'ABS_Y': 0,      # 左摇杆Y
            'ABS_RX': 0,     # 右摇杆X
            'ABS_RY': 0,     # 右摇杆Y
            'ABS_Z': 0,      # LT触发器
            'ABS_RZ': 0     # RT触发器
        }
        self.button_state = {k: False for k in BUTTON_MAP}
        self.smooth_x = 0
        self.smooth_y = 0
        
    def apply_deadzone(self, value):
        if abs(value) < DEADZONE * 32768:
            return 0
        return value / 32768.0
    
    def process_events(self):
        while self.running:
            try:
                events = self.gamepad.read()
                for event in events:
                    if event.ev_type == 'Absolute':
                        self.state[event.code] = event.state
                    elif event.ev_type == 'Key':
                        if event.code in BUTTON_MAP:
                            self.button_state[event.code] = bool(event.state)
            except inputs.UnpluggedError:
                print("手柄断开连接")
                self.running = False
            except Exception as e:
                print(f"读取错误: {e}")
                self.running = False
    
    def get_smooth_movement(self, raw_x, raw_y):
        # 应用死区
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

def main():
    try:
        # 初始化控制器
        controller = XboxController()
        thread = Thread(target=controller.process_events)
        thread.daemon = True
        thread.start()
        
        print("Xbox手柄鼠标控制已启动 (按菜单按钮退出)")
        
        last_scroll_time = 0
        scroll_interval = 0.1  # 滚动间隔(秒)
        
        while controller.running:
            current_time = time.time()
            
            # 处理鼠标移动
            move_x, move_y = controller.get_smooth_movement(
                controller.state['ABS_X'], 
                controller.state['ABS_Y']
            )
            
            if move_x != 0 or move_y != 0:
                x, y = pyautogui.position()
                pyautogui.moveTo(x + move_x, y + move_y, _pause=False)
            
            # 处理滚动 (带节流)
            if current_time - last_scroll_time > scroll_interval:
                scroll_y = -controller.apply_deadzone(controller.state['ABS_RY'])
                if abs(scroll_y) > 0:
                    pyautogui.scroll(int(scroll_y * SCROLL_SPEED), _pause=False)
                    last_scroll_time = current_time
            
            # 处理按钮
            for btn_code, mouse_btn in BUTTON_MAP.items():
                if mouse_btn and controller.button_state.get(btn_code, False):
                    if mouse_btn == 'exit':
                        print("退出程序")
                        controller.stop()
                        return
                    pyautogui.mouseDown(button=mouse_btn, _pause=False)
                else:
                    if mouse_btn and mouse_btn != 'exit':
                        pyautogui.mouseUp(button=mouse_btn, _pause=False)
            
            # 控制循环频率
            time.sleep(1/POLL_RATE)
    
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        controller.stop()
        thread.join(timeout=1)
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