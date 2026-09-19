"""主窗口实现"""
import fnmatch
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
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QAbstractItemView,
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

APP_TITLE = "CathayExtract · PDF OCR 文本提取器"
APP_VERSION = "v1.2.1"


class PendingListWidget(QListWidget):
    """待处理文件列表（可拖入文件/文件夹，可多选删除）"""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setToolTip("把 PDF 文件或整个文件夹拖到这里；选中若干行可单独移除")

    # ---------- 拖放 ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
            self.window.add_pending_paths(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.task_coordinator = None
        self._pending = []  # 待处理路径（有序、去重）
        self._pending_set = set()
        self.setAcceptDrops(True)  # 整个窗口都能接拖放
        self.setup_ui()
        self.setup_menu()

    # ================= 菜单 =================
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

    # ================= 界面 =================
    def setup_ui(self):
        """设置UI布局"""
        self.setWindowTitle("%s %s" % (APP_TITLE, APP_VERSION))
        self.setMinimumSize(880, 660)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # 0. 待处理文件区（拖入 / 添加 / 移除）
        pending_group = QGroupBox("待处理文件（可直接把 PDF 文件或文件夹拖进窗口）")
        pending_layout = QVBoxLayout()

        self.pending_list = PendingListWidget(self)
        self.pending_list.setMinimumHeight(130)
        pending_layout.addWidget(self.pending_list)

        pending_btn_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("添加文件...")
        self.add_files_btn.clicked.connect(self.on_add_files)
        pending_btn_layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("添加文件夹...")
        self.add_folder_btn.clicked.connect(self.on_add_folder)
        pending_btn_layout.addWidget(self.add_folder_btn)

        self.remove_selected_btn = QPushButton("移除选中")
        self.remove_selected_btn.clicked.connect(self.on_remove_selected)
        pending_btn_layout.addWidget(self.remove_selected_btn)

        self.clear_pending_btn = QPushButton("清空列表")
        self.clear_pending_btn.clicked.connect(self.on_clear_pending)
        pending_btn_layout.addWidget(self.clear_pending_btn)

        pending_btn_layout.addStretch()
        self.pending_count_label = QLabel("待处理 0 个文件")
        pending_btn_layout.addWidget(self.pending_count_label)
        pending_layout.addLayout(pending_btn_layout)

        pending_group.setLayout(pending_layout)
        main_layout.addWidget(pending_group)

        # 1. 配置区域
        config_group = QGroupBox("配置")
        config_layout = QVBoxLayout()

        # 源目录选择
        self.source_selector = PathSelector("源目录:", mode="dir")
        self.source_selector.path_edit.setPlaceholderText(
            "留空则只处理上面的列表；列表为空时按此目录递归扫描"
        )
        config_layout.addWidget(self.source_selector)

        # 输出目录选择（留空 = 原地输出）
        self.output_selector = PathSelector("输出目录:", mode="dir")
        self.output_selector.path_edit.setPlaceholderText(
            "留空 = 输出到每个 PDF 的原目录（输出文件名 = 原文件名.txt）"
        )
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

        # 跳过已存在文件选项（不覆盖时按跳过处理）
        self.skip_existing_checkbox = QCheckBox("已存在的 TXT 自动跳过（不覆盖）")
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

    # ================= 拖放 =================
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
            self.add_pending_paths(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # ================= 待处理列表 =================
    def pending_paths(self):
        """当前待处理文件列表（Path 列表）"""
        return [Path(p) for p in self._pending]

    def _update_pending_count(self):
        total = len(self._pending)
        size = sum(p.stat().st_size for p in map(Path, self._pending) if p.exists())
        self.pending_count_label.setText(
            "待处理 %d 个文件（%.1f MB）" % (total, size / 1048576.0)
        )

    def add_pending_paths(self, paths):
        """添加文件/文件夹到待处理列表（文件夹递归展开为 PDF）

        Returns:
            (新增文件数, 忽略路径数)
        """
        added = 0
        ignored = 0
        pattern = (self.filter_edit.text().strip() or "*")
        candidates = []
        for raw in paths:
            p = Path(raw)
            if p.is_dir():
                for f in sorted(p.rglob("*.pdf")):
                    if f.is_file() and (pattern == "*" or fnmatch.fnmatch(f.name, pattern)):
                        candidates.append(f)
            elif p.is_file() and p.suffix.lower() == ".pdf":
                candidates.append(p)  # 手动拖入的单个文件不受过滤限制
            else:
                ignored += 1

        for f in candidates:
            key = str(f.resolve())
            if key in self._pending_set:
                continue
            self._pending_set.add(key)
            self._pending.append(key)
            item = QListWidgetItem(key)
            item.setToolTip(key)
            self.pending_list.addItem(item)
            added += 1

        if added:
            self._update_pending_count()
        if ignored and not added:
            QMessageBox.information(self, "提示", "拖入的内容里没有找到 PDF 文件（只支持 *.pdf）。")
        return added, ignored

    def on_add_files(self):
        """添加文件按钮"""
        files, _ = QFileDialog.getOpenFileNames(self, "选择 PDF 文件", "", "PDF 文件 (*.pdf)")
        if files:
            self.add_pending_paths(files)

    def on_add_folder(self):
        """添加文件夹按钮"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            n, _ = self.add_pending_paths([folder])
            if not n:
                QMessageBox.information(self, "提示", "该文件夹里没有找到 PDF 文件。")

    def on_remove_selected(self):
        """把选中的文件移出待处理列表"""
        rows = sorted({i.row() for i in self.pending_list.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "提示", "请先在列表里选中要移除的文件（可多选）。")
            return
        for r in rows:
            item = self.pending_list.takeItem(r)
            if item is not None:
                key = item.text()
                self._pending_set.discard(key)
                if key in self._pending:
                    self._pending.remove(key)
        self._update_pending_count()

    def on_clear_pending(self):
        """清空待处理列表"""
        self.pending_list.clear()
        self._pending = []
        self._pending_set = set()
        self._update_pending_count()

    # ================= 状态与配置 =================
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
        for btn in (self.add_files_btn, self.add_folder_btn,
                    self.remove_selected_btn, self.clear_pending_btn):
            btn.setEnabled(not is_processing)
        self.pending_list.setEnabled(not is_processing)

    def get_config(self) -> ExtractorConfig:
        """
        从UI获取配置信息

        Returns:
            ExtractorConfig对象

        Raises:
            ValueError: 配置无效
        """
        # 待处理列表优先；列表为空时退回「源目录」扫描
        pending = self.pending_paths()
        src_text = self.source_selector.path_edit.text().strip()
        source_dir = Path(src_text) if src_text else None

        if pending:
            if source_dir is None or not source_dir.is_dir():
                source_dir = pending[0].parent
            file_list = pending
        else:
            if source_dir is None:
                raise ValueError("请先拖入文件/文件夹，或选择源目录")
            if not source_dir.exists():
                raise ValueError(f"源目录不存在: {source_dir}")
            if not source_dir.is_dir():
                raise ValueError(f"源路径不是目录: {source_dir}")
            file_list = None

        # 输出目录：留空 = 输出到每个 PDF 的原目录
        out_text = self.output_selector.path_edit.text().strip()
        output_dir = None
        if out_text:
            output_dir = Path(out_text)
            if not output_dir.exists():
                raise ValueError(f"输出目录不存在: {output_dir}")
            if not output_dir.is_dir():
                raise ValueError(f"输出路径不是目录: {output_dir}")

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
            file_list=file_list,
        )

        return config

    # ================= 运行 =================
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
