import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QCursor, QScreen, QImage

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口保持在最顶层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
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
        # 新增鼠标选取相关变量
        self.selecting = False
        self.start_pos = None
        self.end_pos = None
        self.rect_item = None
    
    def get_transparent_area_coords(self):
        """获取透明区域的屏幕坐标"""
        # 获取中心透明区域相对于窗口的位置
        center_rect = self.center_area.geometry()
        
        # 转换为屏幕坐标
        top_left = self.mapToGlobal(center_rect.topLeft())
        bottom_right = self.mapToGlobal(center_rect.bottomRight())
        
        return top_left, bottom_right
    
    def capture_transparent_area(self):
        """截取透明区域内的图片"""
        try:
            top_left, bottom_right = self.get_transparent_area_coords()
            
            # 获取屏幕截图
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0).toImage()
            print(type(screenshot))
            
            # 转换为numpy数组
            width = screenshot.width()
            height = screenshot.height()
            
            ptr = screenshot.bits()
            ptr.setsize(screenshot.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # RGBA
            
            # 转换为BGR格式供OpenCV使用
            img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            # 计算截图区域
            x1, y1 = top_left.x(), top_left.y()
            x2, y2 = bottom_right.x(), bottom_right.y()
            
            # 确保坐标在图像范围内
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)
            
            # 截取区域
            cropped = img[y1:y2, x1:x2]
            
            # 保存截图
            #cv2.imwrite("screenshot.png", cropped)
            cv2.imshow("Cropped Screenshot", cropped)
            cv2.waitKey(0)
            
            # 显示成功消息
            QMessageBox.information(self, "截图成功", f"已保存透明区域截图到 screenshot.png\n"
                                  f"左上角坐标: ({x1}, {y1})\n"
                                  f"右下角坐标: ({x2}, {y2})")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"截图失败: {str(e)}")
    
    def button_clicked(self, button_num):
        if button_num == 2:
            # 启动鼠标选取模式
            self.selecting = True
            print("已启动鼠标选取模式")
            # 确保窗口能接收鼠标事件
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        print(f"按下按钮{button_num}")
        QMessageBox.information(self, "按钮点击", f"按下按钮{button_num}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下位置
            self.selecting = True
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            if self.rect_item:
                self.scene.removeItem(self.rect_item)
            self.rect_item = None
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = TransparentWindow()
    window.resize(600, 400)
    window.show()
    
    sys.exit(app.exec_())

    def mouseMoveEvent(self, event):
        if self.selecting:
            # 动态更新选取的矩形框
            self.end_pos = event.pos()
            if self.rect_item:
                self.scene.removeItem(self.rect_item)
            start = self.start_pos
            end = self.end_pos
            rect = QRectF(start, end).normalized()
            self.rect_item = self.scene.addRect(rect, QPen(Qt.red))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            self.end_pos = event.pos()
            if self.rect_item:
                self.scene.removeItem(self.rect_item)
            # 获取选取区域的屏幕坐标
            start = self.mapToGlobal(self.start_pos)
            end = self.mapToGlobal(self.end_pos)
            x1, y1 = start.x(), start.y()
            x2, y2 = end.x(), end.y()
            # 截取矩形区域
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x1, y1, x2 - x1, y2 - y1).toImage()
            # 显示截图（可根据需求添加显示逻辑）
            print('已截取矩形区域')
            # 在原位置绘制绿色矩形框（可根据需求调整绘制方式）
            self.draw_green_rect(x1, y1, x2 - x1, y2 - y1)

    def draw_green_rect(self, x, y, width, height):
        # 绘制绿色矩形框的逻辑
        # 这里可以创建一个新的窗口或者使用其他方式绘制矩形框
        rect_window = QMainWindow()
        rect_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        rect_window.setAttribute(Qt.WA_TranslucentBackground)
        rect_window.setGeometry(x, y, width, height)
        central_widget = QWidget()
        central_widget.setStyleSheet('background: rgba(0, 255, 0, 100);')
        rect_window.setCentralWidget(central_widget)
        rect_window.show()
