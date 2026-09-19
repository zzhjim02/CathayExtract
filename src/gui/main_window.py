"""主窗口实现"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QLabel,
    QMessageBox,
    QTabWidget,
    QGroupBox,
    QSpinBox,
    QMenuBar,
    QMenu,
)
from PyQt6.QtCore import Qt

from ..core.config import ExtractorConfig
from ..coordinator import TaskCoordinator
from .path_selector import PathSelector
from .progress_widget import ProgressWidget
from .result_display import ResultDisplay
from .error_log_viewer import ErrorLogViewer
from .about_dialog import AboutDialog
from .method_selector_widget import MethodSelectorWidget
from .performance_stats_widget import PerformanceStatsWidget


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.task_coordinator = None
        self.setup_ui()
        self.setup_menu()

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于动作
        about_action = help_menu.addAction("关于(&A)")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def setup_ui(self):
        """设置UI布局"""
        self.setWindowTitle("CathayExtract · PDF OCR 文本提取器 v1.2.0")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # 1. 配置区域
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout()

        # 源目录选择
        self.source_selector = PathSelector("源目录:", mode="dir")
        config_layout.addWidget(self.source_selector)

        # 输出目录选择
        self.output_selector = PathSelector("输出目录:", mode="dir")
        config_layout.addWidget(self.output_selector)

        # 文件名过滤
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("文件名过滤:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("例如: *.pdf 或 report_*.pdf")
        self.filter_edit.setText("*")
        filter_layout.addWidget(self.filter_edit)
        config_layout.addLayout(filter_layout)

        # 覆盖选项
        self.overwrite_checkbox = QCheckBox("覆盖已存在的文件")
        config_layout.addWidget(self.overwrite_checkbox)

        # 多线程选项
        threading_layout = QHBoxLayout()
        self.multithread_checkbox = QCheckBox("启用多线程处理")
        self.multithread_checkbox.setChecked(True)
        threading_layout.addWidget(self.multithread_checkbox)

        threading_layout.addWidget(QLabel("线程数:"))
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setMinimum(1)
        self.thread_count_spin.setMaximum(16)
        self.thread_count_spin.setValue(4)
        threading_layout.addWidget(self.thread_count_spin)

        config_layout.addLayout(threading_layout)

        # 跳过已处理文件选项
        self.skip_existing_checkbox = QCheckBox("跳过已处理的文件")
        self.skip_existing_checkbox.setChecked(True)
        config_layout.addWidget(self.skip_existing_checkbox)

        # 方法选择控件
        self.method_selector_widget = MethodSelectorWidget()
        config_layout.addWidget(self.method_selector_widget)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # 2. 控制按钮区域
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始提取")
        self.start_btn.clicked.connect(self.on_start_clicked)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # 3. 进度显示区域
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)

        # 4. 结果和日志显示区域(使用标签页)
        tab_widget = QTabWidget()

        # 结果页
        self.result_display = ResultDisplay()
        tab_widget.addTab(self.result_display, "处理结果")

        # 日志页
        self.error_log_viewer = ErrorLogViewer()
        tab_widget.addTab(self.error_log_viewer, "错误日志")

        # 性能统计页
        self.performance_stats_widget = PerformanceStatsWidget()
        tab_widget.addTab(self.performance_stats_widget, "性能统计")

        main_layout.addWidget(tab_widget)

        central_widget.setLayout(main_layout)

        # 初始化状态
        self.update_ui_state(False)

    def update_ui_state(self, is_processing: bool):
        """
        更新UI状态

        Args:
            is_processing: 是否正在处理
        """
        self.start_btn.setEnabled(not is_processing)
        self.stop_btn.setEnabled(is_processing)
        self.source_selector.browse_btn.setEnabled(not is_processing)
        self.output_selector.browse_btn.setEnabled(not is_processing)

    def get_config(self) -> ExtractorConfig:
        """
        从UI获取配置信息

        Returns:
            ExtractorConfig对象

        Raises:
            ValueError: 配置无效
        """
        source_dir = self.source_selector.get_path()
        output_dir = self.output_selector.get_path()

        # 验证路径
        valid, msg = self.source_selector.validate_path()
        if not valid:
            raise ValueError(f"源目录无效: {msg}")

        valid, msg = self.output_selector.validate_path()
        if not valid:
            raise ValueError(f"输出目录无效: {msg}")

        # 创建配置对象
        config = ExtractorConfig(
            source_dir=source_dir,
            output_dir=output_dir,
            file_pattern=self.filter_edit.text().strip() or "*",
            overwrite=self.overwrite_checkbox.isChecked(),
            verbose=True,
            use_multithreading=self.multithread_checkbox.isChecked(),
            max_threads=self.thread_count_spin.value(),
            skip_existing=self.skip_existing_checkbox.isChecked(),
            method_selection_mode=self.method_selector_widget.get_selection_mode(),
            enable_performance_stats=self.method_selector_widget.is_performance_stats_enabled(),
            fallback_on_failure=self.method_selector_widget.is_fallback_enabled(),
        )

        return config

    def on_start_clicked(self):
        """开始提取按钮点击事件"""
        try:
            # 获取配置
            config = self.get_config()

            # 重置UI
            self.progress_widget.reset()
            self.result_display.clear()
            self.error_log_viewer.clear()
            self.performance_stats_widget.clear()

            # 创建任务协调器
            self.task_coordinator = TaskCoordinator(config)

            # 连接信号
            self.task_coordinator.progress_updated.connect(self.on_progress_updated)
            self.task_coordinator.file_processed.connect(self.on_file_processed)
            self.task_coordinator.processing_completed.connect(self.on_processing_completed)
            self.task_coordinator.error_occurred.connect(self.on_error_occurred)
            self.task_coordinator.performance_stats_updated.connect(self.on_performance_stats_updated)

            # 更新UI状态
            self.update_ui_state(True)

            # 启动任务
            self.task_coordinator.start()

        except ValueError as e:
            QMessageBox.warning(self, "配置错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")

    def on_stop_clicked(self):
        """停止按钮点击事件"""
        if self.task_coordinator and self.task_coordinator.is_running():
            self.task_coordinator.stop()

    def on_progress_updated(self, current: int, total: int, file_path: str):
        """进度更新事件"""
        self.progress_widget.set_progress(current, total)
        self.progress_widget.set_status(f"正在处理: {Path(file_path).name}")

    def on_file_processed(self, file_path: str, status: str, success: bool):
        """文件处理完成事件"""
        # 在日志中显示
        icon = "✓" if success else "✗"
        self.error_log_viewer.append_error(f"{icon} {Path(file_path).name}: {status}")

    def on_processing_completed(self, result):
        """处理完成事件"""
        self.progress_widget.set_status("处理完成")
        self.result_display.display_result(result)
        self.update_ui_state(False)

        # 显示完成消息
        QMessageBox.information(self, "完成", result.get_summary())

    def on_error_occurred(self, error_message: str):
        """错误发生事件"""
        self.error_log_viewer.append_error(f"错误: {error_message}")

    def on_performance_stats_updated(self, summary: str):
        """性能统计更新事件"""
        self.performance_stats_widget.display_summary(summary)

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止正在运行的任务
        if self.task_coordinator and self.task_coordinator.is_running():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "任务正在运行中,确定要退出吗?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.task_coordinator.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
