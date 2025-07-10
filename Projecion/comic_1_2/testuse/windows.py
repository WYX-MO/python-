import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QLabel, QFileDialog)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QScreen, QImage

class ScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("一键截图工具")
        self.setGeometry(100, 100, 600, 400)
        
        # 截图相关变量
        self.full_screenshot = None
        self.selected_region = None
        self.result = None  # 存储OpenCV格式的结果
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 主按钮
        self.btn_capture = QPushButton("一键截图并处理")
        self.btn_capture.clicked.connect(self.capture_and_process)
        layout.addWidget(self.btn_capture)
        
        # 显示区域
        self.label = QLabel("截图预览区域")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #aaa;
                min-height: 300px;
            }
        """)
        layout.addWidget(self.label)
        
        # 状态显示
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def capture_and_process(self):
        """一键执行所有截图和处理步骤"""
        self.status_label.setText("正在捕获全屏...")
        self.capture_fullscreen()
        
        # 延迟后启动区域选择
        QApplication.processEvents()
        self.status_label.setText("请选择截图区域...")
        QApplication.processEvents()
        self.select_region()
    
    def capture_fullscreen(self):
        """捕获全屏截图"""
        self.hide()
        QApplication.processEvents()
        
        # 使用PyQt5的QScreen.grabWindow方法获取全屏截图
        screen = QApplication.primaryScreen()
        self.full_screenshot = screen.grabWindow(0)
        self.show()
    
    def select_region(self):
        """在全屏截图上选择区域"""
        if self.full_screenshot is None:
            return
            
        # 创建区域选择窗口
        self.selector = RegionSelector(self.full_screenshot)
        self.selector.region_selected.connect(self.handle_region_selected)
        self.selector.showFullScreen()
    
    def handle_region_selected(self, region):
        """处理选择的区域"""
        if region:
            self.selected_region = region
            self.status_label.setText("正在截取区域...")
            QApplication.processEvents()
            self.crop_selected_region()
            
            # 自动保存
            self.status_label.setText("正在保存截图...")
            QApplication.processEvents()
            self.save_screenshot()
            
            self.status_label.setText("截图完成，已转为OpenCV格式")
    
    def crop_selected_region(self):
        """截取选定区域"""
        if self.selected_region and self.full_screenshot:
            # 从全屏截图中截取选定区域
            cropped = self.full_screenshot.copy(self.selected_region)
            
            # 显示截取的区域
            self.label.setPixmap(cropped.scaled(
                self.label.width(), self.label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            
            # 转换为OpenCV格式
            self.convert_to_opencv(cropped)
    
    def convert_to_opencv(self, pixmap):
        """将QPixmap转换为OpenCV格式的numpy数组"""
        # 转换为QImage
        qimg = pixmap.toImage()
        
        # 转换为numpy数组
        qimg = qimg.convertToFormat(QImage.Format_RGB888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(height * width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        
        # 转换为BGR格式（OpenCV默认格式）
        self.result = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    
    def save_screenshot(self):
        """保存截图"""
        if self.full_screenshot:
            # 自动保存到临时文件
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存截图", "screenshot.png",
                "PNG文件 (*.png);;JPEG文件 (*.jpg);;BMP文件 (*.bmp)"
            )
            if file_path:
                # 保存截图
                self.full_screenshot.save(file_path)

class RegionSelector(QWidget):
    """区域选择窗口"""
    region_selected = pyqtSignal(QRect)
    
    def __init__(self, screenshot):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        
        # 截图显示
        self.background = screenshot
        
        # 选择区域变量
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
    
    def paintEvent(self, event):
        """绘制界面"""
        painter = QPainter(self)
        
        # 绘制背景截图
        painter.drawPixmap(0, 0, self.background)
        
        if self.is_drawing:
            # 绘制选择矩形
            rect = QRect(self.start_point, self.end_point)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            
            # 绘制半透明遮罩
            painter.setBrush(QColor(0, 0, 0, 120))
            painter.drawRect(0, 0, self.width(), self.height())
            
            # 清除选择区域的遮罩
            painter.setBrush(Qt.transparent)
            painter.drawRect(rect)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.is_drawing = True
        self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.is_drawing = False
        
        # 计算选择区域
        x1 = min(self.start_point.x(), self.end_point.x())
        y1 = min(self.start_point.y(), self.end_point.y())
        x2 = max(self.start_point.x(), self.end_point.x())
        y2 = max(self.start_point.y(), self.end_point.y())
        
        # 确保选择区域足够大
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            self.region_selected.emit(QRect(x1, y1, x2 - x1, y2 - y1))
        
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    tool = ScreenshotTool()
    tool.show()
    sys.exit(app.exec_())