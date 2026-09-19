"""方法选择控件"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QCheckBox,
    QLabel,
    QButtonGroup,
)
from PyQt6.QtCore import pyqtSignal

from ..core.config import MethodSelectionMode


class MethodSelectorWidget(QWidget):
    """方法选择控件"""

    # 配置变更信号
    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        """初始化方法选择控件"""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 方法选择标题
        layout.addWidget(QLabel("提取方法:"))

        # 单选按钮组
        self.button_group = QButtonGroup(self)

        # 自动选择
        self.auto_radio = QRadioButton("自动选择 (推荐)")
        self.auto_radio.setChecked(True)
        self.auto_radio.setToolTip("根据PDF特征自动选择最优方法")
        self.button_group.addButton(self.auto_radio, 0)
        layout.addWidget(self.auto_radio)

        # 手动选择方法
        manual_layout = QHBoxLayout()

        self.pymupdf_radio = QRadioButton("PYMUPDF")
        self.pymupdf_radio.setToolTip("高性能提取，适合纯文本PDF和大文件")
        self.button_group.addButton(self.pymupdf_radio, 1)
        manual_layout.addWidget(self.pymupdf_radio)

        self.pdfplumber_radio = QRadioButton("PDFPLUMBER")
        self.pdfplumber_radio.setToolTip("擅长处理复杂布局和表格")
        self.button_group.addButton(self.pdfplumber_radio, 2)
        manual_layout.addWidget(self.pdfplumber_radio)

        self.pypdf2_radio = QRadioButton("PyPDF2")
        self.pypdf2_radio.setToolTip("纯Python实现，兼容性好")
        self.button_group.addButton(self.pypdf2_radio, 3)
        manual_layout.addWidget(self.pypdf2_radio)

        layout.addLayout(manual_layout)

        # 其他选项
        options_layout = QHBoxLayout()

        self.enable_stats_checkbox = QCheckBox("启用性能统计")
        self.enable_stats_checkbox.setChecked(True)
        self.enable_stats_checkbox.setToolTip("记录各方法的处理耗时和成功率")
        options_layout.addWidget(self.enable_stats_checkbox)

        self.fallback_checkbox = QCheckBox("失败时自动降级")
        self.fallback_checkbox.setChecked(True)
        self.fallback_checkbox.setToolTip("当一种方法失败时，自动尝试其他方法")
        options_layout.addWidget(self.fallback_checkbox)

        layout.addLayout(options_layout)

        self.setLayout(layout)

        # 连接信号
        self.button_group.buttonClicked.connect(self._on_button_clicked)
        self.enable_stats_checkbox.stateChanged.connect(lambda: self.config_changed.emit())
        self.fallback_checkbox.stateChanged.connect(lambda: self.config_changed.emit())

    def _on_button_clicked(self):
        """单选按钮点击事件"""
        self.config_changed.emit()

    def get_selection_mode(self) -> MethodSelectionMode:
        """
        获取选择模式

        Returns:
            MethodSelectionMode枚举值
        """
        if self.auto_radio.isChecked():
            return MethodSelectionMode.AUTO
        elif self.pymupdf_radio.isChecked():
            return MethodSelectionMode.MANUAL_PYMUPDF
        elif self.pdfplumber_radio.isChecked():
            return MethodSelectionMode.MANUAL_PDFPLUMBER
        elif self.pypdf2_radio.isChecked():
            return MethodSelectionMode.MANUAL_PYPDF2
        else:
            return MethodSelectionMode.AUTO

    def set_selection_mode(self, mode: MethodSelectionMode):
        """
        设置选择模式

        Args:
            mode: MethodSelectionMode枚举值
        """
        if mode == MethodSelectionMode.AUTO:
            self.auto_radio.setChecked(True)
        elif mode == MethodSelectionMode.MANUAL_PYMUPDF:
            self.pymupdf_radio.setChecked(True)
        elif mode == MethodSelectionMode.MANUAL_PDFPLUMBER:
            self.pdfplumber_radio.setChecked(True)
        elif mode == MethodSelectionMode.MANUAL_PYPDF2:
            self.pypdf2_radio.setChecked(True)

    def is_performance_stats_enabled(self) -> bool:
        """是否启用性能统计"""
        return self.enable_stats_checkbox.isChecked()

    def set_performance_stats_enabled(self, enabled: bool):
        """设置是否启用性能统计"""
        self.enable_stats_checkbox.setChecked(enabled)

    def is_fallback_enabled(self) -> bool:
        """是否启用降级"""
        return self.fallback_checkbox.isChecked()

    def set_fallback_enabled(self, enabled: bool):
        """设置是否启用降级"""
        self.fallback_checkbox.setChecked(enabled)
