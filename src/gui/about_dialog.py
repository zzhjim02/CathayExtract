"""关于对话框实现"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
from PyQt6.QtCore import Qt


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        """初始化关于对话框"""
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        # 软件名称和版本
        title = QLabel("CathayExtract · PDF OCR 文本提取器")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        version = QLabel("版本: v1.2.1")
        version.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(version)

        content_layout.addSpacing(20)

        # 软件描述
        description = QLabel(
            "一个专业的PDF OCR文本提取工具,支持批量处理、多线程并行、智能跳过等功能。"
            "\n\n"
            "主要功能:"
            "\n• 直接拖入 PDF 文件或整个文件夹"
            "\n• 待处理列表可单独移除某个文件"
            "\n• 输出目录留空 = 输出到原目录（文件名 = 原文件名.txt）"
            "\n• 输出格式与 CathayOCR Pro 一致（含分页标记）"
            "\n• 递归扫描文件夹中的所有PDF文件"
            "\n• 提取PDF文件中的OCR文本层内容"
            "\n• 保持原有的文件名和目录结构"
            "\n• 支持文件名过滤(通配符匹配)"
            "\n• 多线程并行处理,大幅提升速度"
            "\n• 智能跳过已处理文件,避免重复工作"
            "\n• 不覆盖已存在的文件时自动跳过"
            "\n• 多种提取方法支持(PYMUPDF/PDFPLUMBER/PyPDF2)"
            "\n• 智能方法选择,自动选择最优方法"
            "\n• 性能统计,实时监控处理性能"
            "\n• 自动降级,失败时尝试其他方法"
            "\n• 实时显示处理进度"
            "\n• 详细的错误日志记录"
            "\n• 友好的图形化用户界面"
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #34495e;")
        content_layout.addWidget(description)

        content_layout.addSpacing(30)

        # 版权信息
        copyright = QLabel(
            "版权信息"
            "\n"
            "\n作者: 浮生＆2cm"
            "\n单位: 湖北大学历史文化学院"
            "\n联系方式: zzhjim@qq.com"
        )
        copyright.setWordWrap(True)
        copyright.setStyleSheet("font-size: 12px; color: #34495e; font-weight: bold;")
        content_layout.addWidget(copyright)

        content_layout.addSpacing(20)

        # 技术支持
        tech_support = QLabel(
            "技术支持: 华为云CodeArts Agent"
        )
        tech_support.setStyleSheet("font-size: 12px; color: #27ae60; font-weight: bold;")
        tech_support.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(tech_support)

        content_layout.addSpacing(30)

        # 许可证
        license_text = QLabel(
            "许可协议: GPL-3.0"
            "\n"
            "\n本软件采用GPL-3.0 许可证,您可以自由使用、修改和分发。"
        )
        license_text.setWordWrap(True)
        license_text.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        content_layout.addWidget(license_text)

        content_layout.addStretch()

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(35)
        layout.addWidget(close_btn)

        self.setLayout(layout)
