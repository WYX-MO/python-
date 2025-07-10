import sys
import cv2
import numpy as np
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QFrame, QMessageBox, QLabel)
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QCursor, QScreen, QImage, QPixmap

# 窗口位置
class mainWindowPosition:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
#子窗口
class ScreenshotWindow(QMainWindow):
    """显示截图的独立窗口"""
    def __init__(self, pixmap):
        super().__init__()  # 不传递parent参数
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint  # 保持最顶层但不限制在主窗口内
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主窗口部件和布局
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 关闭按钮（浮动在右上角）
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 50, 50, 200);
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 200);
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.move(10, 10)  # 固定在左上角
        
        # 截图显示
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        main_layout.addWidget(self.image_label)
        
        # 初始位置（屏幕中央）
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(
            mainWindowPosition.x,mainWindowPosition.y
        )
    
        
    def mousePressEvent(self, event):
        """鼠标按下事件，用于窗口拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现窗口拖动"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and hasattr(self, 'drag_position'):
            del self.drag_position
            event.accept()
#橙色窗口
class TransparentWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        # 设置窗口保持在最顶层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.screenshot_windows = []
        # 窗口属性设置
        self.setWindowTitle("透明截图窗口")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 窗口最小尺寸
        self.setMinimumSize(400, 300)
        
        # 边缘调整大小的区域宽度
        self._edge_size = 10
        
        # 鼠标跟踪相关变量
        self._drag_pos = QPoint()
        self._drag_edge = None
        self._is_dragging_window = False
        
        # 创建主中心部件
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部边框 (20像素高)
        self.top_border = QFrame()
        self.top_border.setFixedHeight(50)
        self.top_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        main_layout.addWidget(self.top_border)
        
        # 中间部分 (包含左右边框和中心透明区域)
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)
        
        # 左边框 (20像素宽)
        self.left_border = QFrame()
        self.left_border.setFixedWidth(20)
        self.left_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        middle_layout.addWidget(self.left_border)
        
        # 中心透明区域 (可扩展)
        self.center_area = QWidget()
        self.center_area.setStyleSheet("background: transparent;")
        middle_layout.addWidget(self.center_area, 1)
        
        # 右边框 (20像素宽)
        self.right_border = QFrame()
        self.right_border.setFixedWidth(20)
        self.right_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        middle_layout.addWidget(self.right_border)
        
        main_layout.addLayout(middle_layout, 1)
        
        # 底部边框 (50像素高)
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        self.bottom_border = QFrame()
        self.bottom_border.setFixedHeight(20)
        self.bottom_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        bottom_layout.addWidget(self.bottom_border)
        
        # 底部按钮区域
        self.button_area = QWidget()
        self.button_area.setFixedHeight(40)
        self.button_area.setStyleSheet("background: transparent;")
        
        self.button_layout = QHBoxLayout(self.button_area)
        self.button_layout.setContentsMargins(20, 0, 20, 5)
        self.button_layout.setSpacing(10)
        
        # 按钮1 - 截图按钮
        self.btn_capture = QPushButton("截图")
        self.btn_capture.setFixedSize(80, 30)
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 180);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.btn_capture.clicked.connect(self.capture_transparent_area)
        self.button_layout.addWidget(self.btn_capture)
        
        # 按钮2
        self.btn_2 = QPushButton("按钮2")
        self.btn_2.setFixedSize(80, 30)
        self.btn_2.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 180);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.btn_2.clicked.connect(lambda: self.button_clicked(2))
        self.button_layout.addWidget(self.btn_2)
        
        # 按钮3
        self.btn_3 = QPushButton("按钮3")
        self.btn_3.setFixedSize(80, 30)
        self.btn_3.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 180);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.btn_3.clicked.connect(lambda: self.button_clicked(3))
        self.button_layout.addWidget(self.btn_3)
        
        # 退出按钮 (宽度较小)
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setFixedSize(60, 30)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 150, 150, 180);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 200);
            }
            QPushButton:pressed {
                background-color: rgba(255, 50, 50, 220);
            }
        """)
        self.exit_btn.clicked.connect(self.close)
        self.button_layout.addWidget(self.exit_btn)
        
        # 添加弹簧使按钮靠右
        self.button_layout.addStretch(1)
        
        bottom_layout.addWidget(self.button_area)
        main_layout.addLayout(bottom_layout)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 保存原始边框样式
        self.original_border_style = "background-color: rgba(255, 200, 150, 150);"

    def get_transparent_area_coords(self):
        center_rect = self.center_area.geometry()
        print(f"中心区域窗口坐标: {center_rect}")  # 调试输出
        pos = self.center_area.geometry()
        
        global_top_left = self.center_area.mapToGlobal(QPoint(0, 0))
        global_bottom_right = self.center_area.mapToGlobal(
            QPoint(center_rect.width(), center_rect.height()))
        
        #print(f"转换后的屏幕坐标: {global_top_left}, {global_bottom_right}")  # 调试输出
        mainWindowPosition.x,mainWindowPosition.y = global_top_left.x(),global_top_left.y()
        return global_top_left, global_bottom_right

        # def translate(self,screenshot):
         
    def capture_transparent_area(self):
        try:
            top_left, bottom_right = self.get_transparent_area_coords()
            width = bottom_right.x() - top_left.x()
            height = bottom_right.y() - top_left.y()
            
            # 获取截图
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, 
                top_left.x(), top_left.y(), 
                width, height
            )
            
            ##==============================在此更改==========================
            
            # 1. 保存原始截图到桌面
            desktop_path = os.path.expanduser("~/Desktop")
            original_path = os.path.join(desktop_path, "original_screenshot.png")
            screenshot.save(original_path, "PNG")
            
            # 2. 将QPixmap转换为QImage
            qimage = screenshot.toImage()
            
            # 3. 将QImage转换为OpenCV格式
            # 转换为Format_RGBA8888格式确保兼容性
            qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
            ptr = qimage.bits()
            ptr.setsize(qimage.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # RGBA
            
            # 转换为BGR格式供OpenCV使用
            cv_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            

            # #=====================SAVE==================================
            # set = 0#後續添加其他功能的設置參數
            # path = os.path.abspath(__file__)
            # #保存圖片
            # path = path.rsplit('\\', 1)[0]
            # #==
            # path = path+"\\test2.py"
            # if not os.path.exists(path):
            #     raise FileNotFoundError(f"找不到REG: {path}")
            # cmd = [
            #     "python",
            #     path,
            #     str(set)
            # ]
            # result = subprocess.run(
            #     cmd,
            #     capture_output=True,
            #     text=True
            # )
            
            # if result.returncode != 0:
            #     print(f"错误: {result.stderr}")
            # else:
            #     print(result.stdout)
            # print("transDone 1 to 2 !")
            # #==========================================================
            
            # 4. 示例处理：转换为灰度图
            processed_cv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

            # 5. 将处理后的OpenCV图像转回QImage
            bytes_per_line = 1 * width  # 灰度图每个像素1字节
            qimage_processed = QImage(processed_cv.data, width, height, 
                                    bytes_per_line, QImage.Format_Grayscale8)
            
            # 6. 保存处理后的图片
            processed_path = os.path.join(desktop_path, "processed_screenshot.png")
            qimage_processed.save(processed_path, "PNG")
            
            # 7. 将QImage转回QPixmap用于显示
            pixmap_processed = QPixmap.fromImage(qimage_processed)
            #============================END====================================

            # 创建独立窗口（不关联父窗口）
            screenshot_window = ScreenshotWindow(pixmap_processed)
            screenshot_window.show()
            
            # 管理窗口列表
            self.screenshot_windows.append(screenshot_window)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"截图失败: {str(e)}")

    def button_clicked(self, button_num):
        if button_num == 2:
            # 关闭所有截图窗口
            for window in self.screenshot_windows:
                window.close()
            self.screenshot_windows = []
        else:
            QMessageBox.information(self, "按钮点击", f"按下按钮{button_num}")

    def set_borders_transparent(self):
        """将窗口边框设置为完全透明"""
        transparent_style = "background-color: rgba(255, 200, 150, 0);"
        self.top_border.setStyleSheet(transparent_style)
        self.left_border.setStyleSheet(transparent_style)
        self.right_border.setStyleSheet(transparent_style)
        self.bottom_border.setStyleSheet(transparent_style)
    
    def restore_borders(self):
        """恢复窗口边框的原始样式"""
        self.top_border.setStyleSheet(self.original_border_style)
        self.left_border.setStyleSheet(self.original_border_style)
        self.right_border.setStyleSheet(self.original_border_style)
        self.bottom_border.setStyleSheet(self.original_border_style)
    

        QMessageBox.information(self, "按钮点击", f"按下按钮{self.button_num}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下位置
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            
            # 检测是否在边缘调整区域
            rect = self.rect()
            pos = event.pos()
            
            # 左上角区域
            top_left = QRect(0, 0, self._edge_size, self._edge_size)
            # 右上角区域
            top_right = QRect(rect.width() - self._edge_size, 0, self._edge_size, self._edge_size)
            # 左下角区域
            bottom_left = QRect(0, rect.height() - self._edge_size, self._edge_size, self._edge_size)
            # 右下角区域
            bottom_right = QRect(rect.width() - self._edge_size, rect.height() - self._edge_size, 
                                self._edge_size, self._edge_size)
            
            # 上边缘
            top_edge = QRect(self._edge_size, 0, rect.width() - 2 * self._edge_size, self._edge_size)
            # 左边缘
            left_edge = QRect(0, self._edge_size, self._edge_size, rect.height() - 2 * self._edge_size)
            # 右边缘
            right_edge = QRect(rect.width() - self._edge_size, self._edge_size, 
                              self._edge_size, rect.height() - 2 * self._edge_size)
            # 下边缘
            bottom_edge = QRect(self._edge_size, rect.height() - self._edge_size, 
                                rect.width() - 2 * self._edge_size, self._edge_size)
            
            if top_left.contains(pos):
                self._drag_edge = "top-left"
            elif top_right.contains(pos):
                self._drag_edge = "top-right"
            elif bottom_left.contains(pos):
                self._drag_edge = "bottom-left"
            elif bottom_right.contains(pos):
                self._drag_edge = "bottom-right"
            elif top_edge.contains(pos):
                self._drag_edge = "top"
            elif left_edge.contains(pos):
                self._drag_edge = "left"
            elif right_edge.contains(pos):
                self._drag_edge = "right"
            elif bottom_edge.contains(pos):
                self._drag_edge = "bottom"
            else:
                self._drag_edge = None
                
            # 如果不在边缘区域，检查是否在顶部或底部边框内可以拖动窗口
            if self._drag_edge is None:
                # 检查顶部边框
                if self.top_border.rect().contains(self.top_border.mapFromParent(event.pos())):
                    self._is_dragging_window = True
                # 检查底部边框（排除按钮区域）
                elif (self.bottom_border.rect().contains(self.bottom_border.mapFromParent(event.pos())) and
                      not self.button_area.rect().contains(self.button_area.mapFromParent(event.pos()))):
                    self._is_dragging_window = True
        
        event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton:
            if self._is_dragging_window:
                # 移动窗口
                self.move(event.globalPos() - self._drag_pos)
            elif self._drag_edge is not None:
                # 调整窗口大小
                rect = self.geometry()
                global_pos = event.globalPos()
                
                if "top" in self._drag_edge:
                    rect.setTop(global_pos.y())
                if "bottom" in self._drag_edge:
                    rect.setBottom(global_pos.y())
                if "left" in self._drag_edge:
                    rect.setLeft(global_pos.x())
                if "right" in self._drag_edge:
                    rect.setRight(global_pos.x())
                
                # 确保窗口不小于最小尺寸
                if rect.width() < self.minimumWidth():
                    if "left" in self._drag_edge:
                        rect.setLeft(rect.right() - self.minimumWidth())
                    else:
                        rect.setRight(rect.left() + self.minimumWidth())
                if rect.height() < self.minimumHeight():
                    if "top" in self._drag_edge:
                        rect.setTop(rect.bottom() - self.minimumHeight())
                    else:
                        rect.setBottom(rect.top() + self.minimumHeight())
                
                self.setGeometry(rect)
        
        # 更新鼠标光标形状
        self.update_cursor_shape(event.pos())
        event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self._drag_edge = None
        self._is_dragging_window = False
        event.accept()
    
    def update_cursor_shape(self, pos):
        """根据鼠标位置更新光标形状"""
        # 如果正在拖动窗口，保持箭头光标
        if self._is_dragging_window:
            self.setCursor(Qt.ArrowCursor)
            return
            
        rect = self.rect()
        
        # 左上角区域
        top_left = QRect(0, 0, self._edge_size, self._edge_size)
        # 右上角区域
        top_right = QRect(rect.width() - self._edge_size, 0, self._edge_size, self._edge_size)
        # 左下角区域
        bottom_left = QRect(0, rect.height() - self._edge_size, self._edge_size, self._edge_size)
        # 右下角区域
        bottom_right = QRect(rect.width() - self._edge_size, rect.height() - self._edge_size, 
                            self._edge_size, self._edge_size)
        
        # 上边缘
        top_edge = QRect(self._edge_size, 0, rect.width() - 2 * self._edge_size, self._edge_size)
        # 左边缘
        left_edge = QRect(0, self._edge_size, self._edge_size, rect.height() - 2 * self._edge_size)
        # 右边缘
        right_edge = QRect(rect.width() - self._edge_size, self._edge_size, 
                          self._edge_size, rect.height() - 2 * self._edge_size)
        # 下边缘
        bottom_edge = QRect(self._edge_size, rect.height() - self._edge_size, 
                          rect.width() - 2 * self._edge_size, self._edge_size)
        
        if top_left.contains(pos) or bottom_right.contains(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        elif top_right.contains(pos) or bottom_left.contains(pos):
            self.setCursor(Qt.SizeBDiagCursor)
        elif left_edge.contains(pos) or right_edge.contains(pos):
            self.setCursor(Qt.SizeHorCursor)
        elif top_edge.contains(pos) or bottom_edge.contains(pos):
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
#==========================MAIN===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())