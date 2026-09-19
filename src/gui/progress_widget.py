"""进度显示组件实现"""
from PyQt6.QtWidgets import QWidget, QLabel, QProgressBar, QVBoxLayout


class ProgressWidget(QWidget):
    """进度显示组件"""

    def __init__(self):
        """初始化进度显示组件"""
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_progress(self, current: int, total: int):
        """
        更新进度条

        Args:
            current: 当前进度
            total: 总数
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{current}/{total} ({percentage}%)")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0/0")

    def set_status(self, status: str):
        """
        更新状态文本

        Args:
            status: 状态文本
        """
        self.status_label.setText(status)

    def reset(self):
        """重置进度显示"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0/0")
        self.status_label.setText("准备就绪")
