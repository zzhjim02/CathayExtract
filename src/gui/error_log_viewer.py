"""错误日志查看器实现"""
from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt


class ErrorLogViewer(QWidget):
    """错误日志查看器"""

    def __init__(self):
        """初始化错误日志查看器"""
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("日志信息将显示在这里...")
        layout.addWidget(self.log_text)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("清除日志")
        self.clear_btn.clicked.connect(self.clear)
        button_layout.addWidget(self.clear_btn)

        self.save_btn = QPushButton("保存日志")
        self.save_btn.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def append_error(self, error_message: str):
        """
        添加错误信息到日志视图

        Args:
            error_message: 错误信息
        """
        self.log_text.append(error_message)

    def clear(self):
        """清空日志视图"""
        self.log_text.clear()

    def save_log(self):
        """将日志保存到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "error_log.txt", "文本文件 (*.txt);;所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.toPlainText())
            except Exception as e:
                self.log_text.append(f"保存失败: {str(e)}")
