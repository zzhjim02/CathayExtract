"""路径选择器实现"""
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
from PyQt6.QtCore import pyqtSignal


class PathSelector(QWidget):
    """路径选择器组件"""

    path_changed = pyqtSignal(str)  # 路径变化信号

    def __init__(self, label_text: str, mode: str = "dir"):
        """
        初始化路径选择器

        Args:
            label_text: 标签文本
            mode: 选择模式,"dir"表示选择目录,"file"表示选择文件
        """
        super().__init__()
        self.mode = mode
        self.setup_ui(label_text)

    def setup_ui(self, label_text: str):
        """设置UI布局"""
        layout = QHBoxLayout()

        # 标签
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)

        # 路径输入框
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择路径...")
        self.path_edit.textChanged.connect(self._on_path_changed)
        layout.addWidget(self.path_edit)

        # 浏览按钮
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_path)
        layout.addWidget(self.browse_btn)

        self.setLayout(layout)

    def _browse_path(self):
        """打开路径选择对话框"""
        if self.mode == "dir":
            path = QFileDialog.getExistingDirectory(self, "选择目录")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件")

        if path:
            self.set_path(path)

    def _on_path_changed(self, text: str):
        """路径变化处理"""
        self.path_changed.emit(text)

    def get_path(self) -> Path:
        """
        获取用户选择的路径

        Returns:
            Path对象
        """
        return Path(self.path_edit.text())

    def set_path(self, path: str):
        """
        设置路径

        Args:
            path: 路径字符串
        """
        self.path_edit.setText(path)

    def validate_path(self) -> tuple[bool, str]:
        """
        验证路径是否有效

        Returns:
            (是否有效, 错误消息)
        """
        path = self.get_path()

        if not path:
            return False, "路径不能为空"

        if not path.exists():
            return False, "路径不存在"

        if self.mode == "dir" and not path.is_dir():
            return False, "选择的路径不是目录"

        if self.mode == "file" and not path.is_file():
            return False, "选择的路径不是文件"

        return True, ""
