import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageGrab
import threading
import time
import webbrowser
import platform
import numpy as np
from collections import deque

class Window:
    """表示一个应用窗口，包含标题、位置和截图等信息"""
    def __init__(self, title, region, screenshot=None):
        self.title = title
        self.region = region  # (x, y, width, height)
        self.screenshot = screenshot
        self.is_active = True
        
    def __str__(self):
        return self.title

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("应用窗口监控工具")
        self.root.geometry("900x600")
        
        self.windows = []  # 检测到的窗口列表
        self.selected_window = None
        self.monitor_window = None
        self.monitor_running = False
        self.last_captures = deque(maxlen=5)  # 最近的捕获结果
        
        self.create_widgets()
        self.start_window_detection()  # 启动窗口检测线程
    
    def create_widgets(self):
        # 顶部工具栏
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="刷新窗口列表", command=self.refresh_window_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="选择窗口", command=self.select_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="开始监控", command=self.toggle_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="打开网页", command=self.open_webpage).pack(side=tk.RIGHT, padx=5)
        
        # 窗口列表区域
        list_frame = ttk.LabelFrame(self.root, text="应用窗口列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.LEFT, anchor="n")
        
        self.window_listbox = tk.Listbox(list_frame, font=("SimHei", 10), selectmode=tk.SINGLE, width=40)
        self.window_listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.window_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.window_listbox.config(yscrollcommand=scrollbar.set)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(self.root, text="窗口预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.RIGHT, anchor="n", fill=tk.BOTH)
        
        self.preview_label = ttk.Label(preview_frame, text="请选择一个窗口")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
    
    def start_window_detection(self):
        """启动窗口检测线程"""
        def detection_loop():
            while True:
                self.detect_windows()
                self.update_window_list()
                time.sleep(2)  # 每2秒检测一次
        
        threading.Thread(target=detection_loop, daemon=True).start()
    
    def detect_windows(self):
        """检测当前屏幕上的应用窗口"""
        # 捕获全屏
        screenshot = ImageGrab.grab()
        screen_width, screen_height = screenshot.size
        
        # 重置窗口列表
        new_windows = []
        
        # 使用颜色和边缘检测识别可能的窗口
        # 注意：这是一个简化的算法，实际应用中可能需要更复杂的计算机视觉技术
        
        # 1. 检测可能的窗口标题栏（假设为深蓝色）
        title_bar_color = (0, 0, 128)  # 深蓝色作为示例
        tolerance = 30
        
        # 2. 查找颜色匹配的区域
        pixels = screenshot.load()
        window_areas = []
        
        # 简化的窗口检测算法
        for y in range(0, screen_height - 50, 10):  # 跳过底部区域
            for x in range(0, screen_width - 100, 10):  # 跳过右侧区域
                r, g, b = pixels[x, y]
                if (abs(r - title_bar_color[0]) < tolerance and
                    abs(g - title_bar_color[1]) < tolerance and
                    abs(b - title_bar_color[2]) < tolerance):
                    
                    # 找到可能的窗口左上角
                    # 简单估计窗口大小（实际应用中可以使用更复杂的算法）
                    window_width = min(400, screen_width - x)
                    window_height = min(300, screen_height - y)
                    
                    # 避免重复检测
                    is_duplicate = False
                    for (wx, wy, ww, wh) in window_areas:
                        if (abs(wx - x) < 50 and abs(wy - y) < 50):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        window_areas.append((x, y, window_width, window_height))
        
        # 3. 创建窗口对象
        for i, (x, y, width, height) in enumerate(window_areas):
            window_title = f"窗口 {i+1}"
            window_region = (x, y, width, height)
            
            # 截取窗口内容
            window_screenshot = screenshot.crop((x, y, x+width, y+height))
            
            new_windows.append(Window(window_title, window_region, window_screenshot))
        
        # 添加主窗口
        new_windows.append(Window("应用主窗口", (0, 0, screen_width, screen_height), screenshot))
        
        self.windows = new_windows
    
    def update_window_list(self):
        """更新窗口列表显示"""
        self.root.after(0, lambda: self._update_window_list())
    
    def _update_window_list(self):
        """在主线程中更新窗口列表"""
        # 清空列表框
        self.window_listbox.delete(0, tk.END)
        
        # 添加窗口到列表
        for i, window in enumerate(self.windows):
            self.window_listbox.insert(tk.END, window.title)
            
            # 如果是主窗口，默认选中
            if window.title == "应用主窗口":
                self.window_listbox.selection_set(i)
    
    def refresh_window_list(self):
        """手动刷新窗口列表"""
        self.detect_windows()
        self.update_window_list()
    
    def select_window(self):
        """选择要监控的窗口"""
        selection = self.window_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个窗口")
            return
        
        index = selection[0]
        self.selected_window = self.windows[index]
        
        # 显示窗口预览
        if self.selected_window.screenshot:
            preview_img = self.selected_window.screenshot.resize((400, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
        else:
            self.preview_label.config(text=f"已选择: {self.selected_window.title}")
        
        messagebox.showinfo("成功", f"已选择窗口: {self.selected_window.title}")
    
    def toggle_monitoring(self):
        """切换监控状态"""
        if self.monitor_running:
            self.monitor_running = False
            if self.monitor_window:
                self.monitor_window.destroy()
                self.monitor_window = None
            self.preview_label.config(text=f"已停止监控: {self.selected_window.title}")
        else:
            if not self.selected_window:
                messagebox.showwarning("警告", "请先选择一个窗口")
                return
            
            self.monitor_running = True
            self.create_monitor_window()
            self.start_monitoring()
    
    def create_monitor_window(self):
        """创建监控窗口"""
        self.monitor_window = tk.Toplevel(self.root)
        self.monitor_window.title(f"监控: {self.selected_window.title}")
        self.monitor_window.geometry("640x480")
        
        self.monitor_label = ttk.Label(self.monitor_window)
        self.monitor_label.pack(fill=tk.BOTH, expand=True)
    
    def start_monitoring(self):
        """开始监控线程"""
        def monitor_loop():
            while self.monitor_running:
                if not self.selected_window:
                    break
                
                try:
                    # 捕获选定窗口区域
                    x, y, width, height = self.selected_window.region
                    screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
                    
                    # 调整图像大小以适应监控窗口
                    monitor_width = self.monitor_window.winfo_width()
                    monitor_height = self.monitor_window.winfo_height()
                    
                    if monitor_width > 10 and monitor_height > 10:
                        screenshot = screenshot.resize((monitor_width, monitor_height), Image.LANCZOS)
                    
                    # 更新监控窗口
                    photo = ImageTk.PhotoImage(image=screenshot)
                    self.monitor_label.config(image=photo)
                    self.monitor_label.image = photo
                
                except Exception as e:
                    print(f"监控过程中出错: {e}")
                    self.root.after(0, lambda: messagebox.showwarning("警告", f"监控出错: {e}"))
                    self.monitor_running = False
                    break
                
                time.sleep(0.1)  # 控制刷新频率
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def open_webpage(self):
        """打开示例网页"""
        webbrowser.open("https://www.baidu.com")
        messagebox.showinfo("提示", "已在浏览器中打开百度网页")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    
    # 确保中文正常显示
    style = ttk.Style()
    style.configure('.', font=('SimHei', 10))
    
    root.mainloop()