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

# Global window position tracker
class WindowPosition:
    def __init__(self):
        self.x = 0
        self.y = 0

mainWindowPosition = WindowPosition()

class ScreenshotWindow(QMainWindow):
    """显示截图的独立窗口"""
    def __init__(self, pixmap):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
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
        self.close_btn.move(10, 10)
        
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        main_layout.addWidget(self.image_label)
        
        self.move(mainWindowPosition.x, mainWindowPosition.y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and hasattr(self, 'drag_position'):
            del self.drag_position
            event.accept()

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.screenshot_windows = []
        
        self.setWindowTitle("透明截图窗口")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 300)
        
        self._edge_size = 10
        self._drag_pos = QPoint()
        self._drag_edge = None
        self._is_dragging_window = False
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.top_border = QFrame()
        self.top_border.setFixedHeight(50)
        self.top_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        main_layout.addWidget(self.top_border)
        
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)
        
        self.left_border = QFrame()
        self.left_border.setFixedWidth(20)
        self.left_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        middle_layout.addWidget(self.left_border)
        
        self.center_area = QWidget()
        self.center_area.setStyleSheet("background: transparent;")
        middle_layout.addWidget(self.center_area, 1)
        
        self.right_border = QFrame()
        self.right_border.setFixedWidth(20)
        self.right_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        middle_layout.addWidget(self.right_border)
        
        main_layout.addLayout(middle_layout, 1)
        
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        self.bottom_border = QFrame()
        self.bottom_border.setFixedHeight(20)
        self.bottom_border.setStyleSheet("background-color: rgba(255, 200, 150, 150);")
        bottom_layout.addWidget(self.bottom_border)
        
        self.button_area = QWidget()
        self.button_area.setFixedHeight(40)
        self.button_area.setStyleSheet("background: transparent;")
        
        self.button_layout = QHBoxLayout(self.button_area)
        self.button_layout.setContentsMargins(20, 0, 20, 5)
        self.button_layout.setSpacing(10)
        
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
        
        self.button_layout.addStretch(1)
        bottom_layout.addWidget(self.button_area)
        main_layout.addLayout(bottom_layout)
        self.original_border_style = "background-color: rgba(255, 200, 150, 150);"

    def get_transparent_area_coords(self):
        center_rect = self.center_area.geometry()
        global_top_left = self.center_area.mapToGlobal(QPoint(0, 0))
        global_bottom_right = self.center_area.mapToGlobal(
            QPoint(center_rect.width(), center_rect.height()))
        
        mainWindowPosition.x, mainWindowPosition.y = global_top_left.x(), global_top_left.y()
        return global_top_left, global_bottom_right

    def capture_transparent_area(self):
        try:
            top_left, bottom_right = self.get_transparent_area_coords()
            width = bottom_right.x() - top_left.x()
            height = bottom_right.y() - top_left.y()
            
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, 
                top_left.x(), top_left.y(), 
                width, height
            )
            
            # Create and show screenshot window
            screenshot_window = ScreenshotWindow(screenshot)
            screenshot_window.show()
            self.screenshot_windows.append(screenshot_window)
            
            # Convert to OpenCV format
            img = screenshot.toImage()
            ptr = img.bits()
            ptr.setsize(img.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)
            cv_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            # Save image temporarily
            script_dir = os.path.dirname(os.path.abspath(__file__))
            temp_path = os.path.join(script_dir, "temp_screenshot.png")
            cv2.imwrite(temp_path, cv_img)
            
            # Process image (example - show with OpenCV)
            cv2.imshow("Captured Image", cv_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"截图失败: {str(e)}")

    def button_clicked(self, button_num):
        if button_num == 2:
            for window in self.screenshot_windows:
                window.close()
            self.screenshot_windows = []
        else:
            QMessageBox.information(self, "按钮点击", f"按下按钮{button_num}")

    def set_borders_transparent(self):
        transparent_style = "background-color: rgba(255, 200, 150, 0);"
        self.top_border.setStyleSheet(transparent_style)
        self.left_border.setStyleSheet(transparent_style)
        self.right_border.setStyleSheet(transparent_style)
        self.bottom_border.setStyleSheet(transparent_style)
    
    def restore_borders(self):
        self.top_border.setStyleSheet(self.original_border_style)
        self.left_border.setStyleSheet(self.original_border_style)
        self.right_border.setStyleSheet(self.original_border_style)
        self.bottom_border.setStyleSheet(self.original_border_style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            rect = self.rect()
            pos = event.pos()
            
            top_left = QRect(0, 0, self._edge_size, self._edge_size)
            top_right = QRect(rect.width() - self._edge_size, 0, self._edge_size, self._edge_size)
            bottom_left = QRect(0, rect.height() - self._edge_size, self._edge_size, self._edge_size)
            bottom_right = QRect(rect.width() - self._edge_size, rect.height() - self._edge_size, 
                                self._edge_size, self._edge_size)
            
            top_edge = QRect(self._edge_size, 0, rect.width() - 2 * self._edge_size, self._edge_size)
            left_edge = QRect(0, self._edge_size, self._edge_size, rect.height() - 2 * self._edge_size)
            right_edge = QRect(rect.width() - self._edge_size, self._edge_size, 
                              self._edge_size, rect.height() - 2 * self._edge_size)
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
                
            if self._drag_edge is None:
                if self.top_border.rect().contains(self.top_border.mapFromParent(event.pos())):
                    self._is_dragging_window = True
                elif (self.bottom_border.rect().contains(self.bottom_border.mapFromParent(event.pos())) and
                      not self.button_area.rect().contains(self.button_area.mapFromParent(event.pos()))):
                    self._is_dragging_window = True
        
        event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self._is_dragging_window:
                self.move(event.globalPos() - self._drag_pos)
            elif self._drag_edge is not None:
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
        
        self.update_cursor_shape(event.pos())
        event.accept()
    
    def mouseReleaseEvent(self, event):
        self._drag_edge = None
        self._is_dragging_window = False
        event.accept()
    
    def update_cursor_shape(self, pos):
        if self._is_dragging_window:
            self.setCursor(Qt.ArrowCursor)
            return
            
        rect = self.rect()
        
        top_left = QRect(0, 0, self._edge_size, self._edge_size)
        top_right = QRect(rect.width() - self._edge_size, 0, self._edge_size, self._edge_size)
        bottom_left = QRect(0, rect.height() - self._edge_size, self._edge_size, self._edge_size)
        bottom_right = QRect(rect.width() - self._edge_size, rect.height() - self._edge_size, 
                            self._edge_size, self._edge_size)
        
        top_edge = QRect(self._edge_size, 0, rect.width() - 2 * self._edge_size, self._edge_size)
        left_edge = QRect(0, self._edge_size, self._edge_size, rect.height() - 2 * self._edge_size)
        right_edge = QRect(rect.width() - self._edge_size, self._edge_size, 
                          self._edge_size, rect.height() - 2 * self._edge_size)
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