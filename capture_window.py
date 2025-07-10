import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageGrab
import threading
import time
import webbrowser
import platform

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("窗口监控应用（跨平台版）")
        self.root.geometry("800x600")
        
        self.monitor_region = None  # 存储监控区域坐标 (x1, y1, x2, y2)
        self.monitor_window = None
        self.monitor_running = False
        self.capture_interval = 0.1  # 捕获间隔（秒）
        
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部功能区
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        self.select_btn = ttk.Button(top_frame, text="选择监控窗口", command=self.select_window_region)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = ttk.Button(top_frame, text="开始监控", command=self.toggle_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.url_entry = ttk.Entry(top_frame, width=50)
        self.url_entry.insert(tk.END, "https://www.example.com")
        self.url_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.open_web_btn = ttk.Button(top_frame, text="打开网页", command=self.open_webpage)
        self.open_web_btn.pack(side=tk.LEFT, padx=5)
        
        # 监控预览区域
        self.preview_label = ttk.Label(self.root, text="请选择要监控的窗口区域")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def select_window_region(self):
        """启动屏幕区域选择模式"""
        self.root.withdraw()  # 隐藏主窗口
        time.sleep(0.1)
        
        # 创建全屏幕选择窗口
        select_root = tk.Toplevel(self.root)
        select_root.attributes("-fullscreen", True)
        select_root.attributes("-alpha", 0.3)
        select_root.config(bg="black")
        
        canvas = tk.Canvas(select_root, bg="black", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        start = None
        rect = None
        
        def on_mouse_down(event):
            nonlocal start, rect
            start = (event.x, event.y)
            rect = canvas.create_rectangle(0, 0, 0, 0, outline="red", width=2)
        
        def on_mouse_move(event):
            nonlocal start, rect
            if start:
                x1, y1 = start
                x2, y2 = event.x, event.y
                canvas.coords(rect, x1, y1, x2, y2)
        
        def on_mouse_up(event):
            nonlocal start, rect, select_root
            if start:
                x1, y1 = start
                x2, y2 = event.x, event.y
                self.monitor_region = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                select_root.destroy()
                self.root.deiconify()
                messagebox.showinfo("提示", "已选择监控区域")
            else:
                select_root.destroy()
                self.root.deiconify()
        
        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        select_root.bind("<Escape>", lambda e: select_root.destroy())
    
    def toggle_monitoring(self):
        if self.monitor_running:
            self.monitor_running = False
            self.start_btn.config(text="开始监控")
            if self.monitor_window:
                self.monitor_window.destroy()
        else:
            if not self.monitor_region:
                messagebox.showwarning("警告", "请先选择监控区域")
                return
            
            self.monitor_running = True
            self.start_btn.config(text="停止监控")
            self.create_monitor_window()
            self.start_capturing()
    
    def create_monitor_window(self):
        self.monitor_window = tk.Toplevel(self.root)
        self.monitor_window.title("实时监控")
        self.monitor_window.geometry("640x480")
        
        self.monitor_label = ttk.Label(self.monitor_window)
        self.monitor_label.pack(fill=tk.BOTH, expand=True)
    
    def start_capturing(self):
        def capture_loop():
            while self.monitor_running:
                if self.monitor_region and self.monitor_window.winfo_exists():
                    try:
                        # 捕获指定区域
                        screenshot = ImageGrab.grab(bbox=self.monitor_region)
                        
                        # 调整尺寸适应窗口
                        width, height = self.monitor_window.winfo_width(), self.monitor_window.winfo_height()
                        if width > 0 and height > 0:
                            screenshot = screenshot.resize((width, height), Image.LANCZOS)
                        
                        # 显示图像
                        photo = ImageTk.PhotoImage(screenshot)
                        self.monitor_label.config(image=photo)
                        self.monitor_label.image = photo
                    
                    except Exception as e:
                        print(f"捕获错误: {e}")
                        messagebox.showwarning("警告", "捕获失败，请重试")
                        self.toggle_monitoring()
                        return
                
                time.sleep(self.capture_interval)
        
        threading.Thread(target=capture_loop, daemon=True).start()
    
    def open_webpage(self):
        url = self.url_entry.get()
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showwarning("警告", f"无法打开网页: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()