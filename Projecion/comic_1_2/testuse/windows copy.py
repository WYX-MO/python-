import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QLabel, QFileDialog)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QScreen

class ScreenshotTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Windows区域截图工具")
        self.setGeometry(100, 100, 600, 400)
        
        # 截图相关变量
        self.full_screenshot = None
        self.selected_region = None
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # 按钮区域
        btn_layout = QVBoxLayout()
        
        self.btn_full = QPushButton("1. 获取全屏截图")
        self.btn_full.clicked.connect(self.capture_fullscreen)
        
        self.btn_select = QPushButton("2. 选择截图区域")
        self.btn_select.clicked.connect(self.select_region)
        self.btn_select.setEnabled(False)
        
        self.btn_crop = QPushButton("3. 截取选定区域")
        self.btn_crop.clicked.connect(self.crop_selected_region)
        self.btn_crop.setEnabled(False)
        
        self.btn_save = QPushButton("4. 保存截图")
        self.btn_save.clicked.connect(self.save_screenshot)
        self.btn_save.setEnabled(False)
        
        btn_layout.addWidget(self.btn_full)
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_crop)
        btn_layout.addWidget(self.btn_save)
        
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
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def capture_fullscreen(self):
        """捕获全屏截图"""
        self.hide()
        QApplication.processEvents()
        
        # 使用PyQt5的QScreen.grabWindow方法获取全屏截图
        screen = QApplication.primaryScreen()
        self.full_screenshot = screen.grabWindow(0)
        
        # 显示全屏截图（缩放到适合窗口大小）
        self.label.setPixmap(self.full_screenshot.scaled(
            self.label.width(), self.label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        
        self.btn_select.setEnabled(True)
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
            self.btn_crop.setEnabled(True)
    
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
            
            self.full_screenshot = cropped  # 更新当前截图
            self.btn_save.setEnabled(True)
    
    def save_screenshot(self):
        """保存截图"""
        if self.full_screenshot:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存截图", "screenshot.png",
                "PNG文件 (*.png);;JPEG文件 (*.jpg);;BMP文件 (*.bmp)"
            )
            if file_path:
                # 保存截图
                self.full_screenshot.save(file_path)
                self.label.setText(f"截图已保存: {file_path}")

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