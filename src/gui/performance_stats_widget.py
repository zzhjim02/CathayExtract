"""性能统计显示组件"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
)
from PyQt6.QtCore import Qt

from ..core.config import PerformanceStatistics


class PerformanceStatsWidget(QWidget):
    """性能统计显示组件"""

    def __init__(self, parent=None):
        """初始化性能统计显示组件"""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("性能统计")
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)

        # 统计信息显示区域
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setPlaceholderText("暂无性能统计数据")
        layout.addWidget(self.stats_text)

        self.setLayout(layout)

    def display_statistics(self, statistics: PerformanceStatistics):
        """
        显示性能统计数据

        Args:
            statistics: PerformanceStatistics对象
        """
        summary = statistics.get_summary()
        self.stats_text.setText(summary)

    def display_summary(self, summary: str):
        """
        显示性能统计摘要

        Args:
            summary: 性能统计摘要字符串
        """
        self.stats_text.setText(summary)

    def clear(self):
        """清空显示"""
        self.stats_text.clear()
