"""结果展示组件实现"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class ResultDisplay(QWidget):
    """结果展示组件"""

    def __init__(self):
        """初始化结果展示组件"""
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 结果标签
        self.result_label = QLabel("等待处理...")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def display_result(self, result):
        """
        显示处理结果

        Args:
            result: ProcessingResult对象
        """
        summary = result.get_summary()

        # 使用HTML格式化文本
        html_text = f"""
        <h2>处理完成</h2>
        <p><b>总文件数:</b> {result.total_files}</p>
        <p><b>成功:</b> <span style="color: green;">{result.success_count}</span></p>
        <p><b>失败:</b> <span style="color: red;">{result.failed_count}</span></p>
        <p><b>跳过:</b> <span style="color: orange;">{result.skipped_count}</span></p>
        <p><b>耗时:</b> {result.duration:.2f}秒</p>
        """

        if result.failed_count > 0:
            html_text += f'<p style="color: red;"><b>警告:</b> 有{result.failed_count}个文件处理失败,请查看错误日志</p>'

        self.result_label.setText(html_text)

    def clear(self):
        """清除结果显示"""
        self.result_label.setText("等待处理...")
