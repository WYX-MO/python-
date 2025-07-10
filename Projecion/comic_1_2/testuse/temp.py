class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ...（其他初始化代码保持不变）...

        # 修改按钮样式和布局策略（在 button_layout 部分）
        self.button_layout = QHBoxLayout(self.button_area)
        self.button_layout.setContentsMargins(10, 0, 10, 5)  # 减少边距
        self.button_layout.setSpacing(5)  # 缩小按钮间距

        # 按钮1 - 截图按钮（动态调整大小）
        self.btn_capture = QPushButton("截图")
        self.btn_capture.setMinimumSize(40, 25)  # 最小宽度40px
        self.btn_capture.setMaximumSize(120, 30)  # 最大宽度120px
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 3px;
                color: black;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 180);
            }
        """)
        self.button_layout.addWidget(self.btn_capture)

        # 按钮2（同上）
        self.btn_2 = QPushButton("按钮2")
        self.btn_2.setMinimumSize(40, 25)
        self.btn_2.setMaximumSize(120, 30)
        self.btn_2.setStyleSheet(self.btn_capture.styleSheet())
        self.button_layout.addWidget(self.btn_2)

        # 按钮3（同上）
        self.btn_3 = QPushButton("按钮3")
        self.btn_3.setMinimumSize(40, 25)
        self.btn_3.setMaximumSize(120, 30)
        self.btn_3.setStyleSheet(self.btn_capture.styleSheet())
        self.button_layout.addWidget(self.btn_3)

        # 退出按钮（固定较小尺寸）
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setFixedSize(50, 25)  # 固定大小（重要按钮不缩放）
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 150, 150, 180);
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 3px;
                color: black;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 200);
            }
        """)
        self.button_layout.addWidget(self.exit_btn)

        # 其他代码保持不变...