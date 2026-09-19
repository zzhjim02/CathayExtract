"""方法选择器"""
from pathlib import Path
from typing import Optional

from .pdf_analyzer import PDFAnalyzer
from .strategy_factory import StrategyFactory
from ..core.config import PDFCharacteristics, MethodSelectionMode, ExtractionMethod


class MethodSelector:
    """方法选择器"""

    def __init__(self):
        """初始化方法选择器"""
        self.analyzer = PDFAnalyzer()

    def select_method(
        self,
        pdf_path: Path,
        mode: MethodSelectionMode = MethodSelectionMode.AUTO
    ) -> Optional[ExtractionMethod]:
        """
        选择提取方法

        Args:
            pdf_path: PDF文件路径
            mode: 选择模式

        Returns:
            选择的提取方法
        """
        # 手动模式：直接返回指定的方法
        if mode == MethodSelectionMode.MANUAL_PYMUPDF:
            return ExtractionMethod.PYMUPDF
        elif mode == MethodSelectionMode.MANUAL_PDFPLUMBER:
            return ExtractionMethod.PDFPLUMBER
        elif mode == MethodSelectionMode.MANUAL_PYPDF2:
            return ExtractionMethod.PYPDF2

        # 自动模式：根据PDF特征选择最优方法
        characteristics = self.analyzer.analyze(pdf_path)
        return self._select_by_characteristics(characteristics)

    def _select_by_characteristics(self, characteristics: PDFCharacteristics) -> ExtractionMethod:
        """
        根据PDF特征选择最优方法

        Args:
            characteristics: PDF特征

        Returns:
            选择的提取方法
        """
        # 检查各方法是否可用
        pymupdf_available = StrategyFactory.get_strategy(ExtractionMethod.PYMUPDF) is not None
        pdfplumber_available = StrategyFactory.get_strategy(ExtractionMethod.PDFPLUMBER) is not None
        pypdf2_available = StrategyFactory.get_strategy(ExtractionMethod.PYPDF2) is not None

        # 如果只有一个方法可用，直接返回
        if not pymupdf_available and not pdfplumber_available and pypdf2_available:
            return ExtractionMethod.PYPDF2
        if not pymupdf_available and pdfplumber_available and not pypdf2_available:
            return ExtractionMethod.PDFPLUMBER
        if pymupdf_available and not pdfplumber_available and not pypdf2_available:
            return ExtractionMethod.PYMUPDF

        # 如果没有方法可用，返回PyPDF2（会在执行时报错）
        if not pymupdf_available and not pdfplumber_available and not pypdf2_available:
            return ExtractionMethod.PYPDF2

        # 根据特征选择方法
        # 1. 扫描件优先使用PDFPLUMBER
        if characteristics.is_scanned and pdfplumber_available:
            return ExtractionMethod.PDFPLUMBER

        # 2. 复杂布局或表格优先使用PDFPLUMBER
        if (characteristics.has_complex_layout or characteristics.has_tables) and pdfplumber_available:
            return ExtractionMethod.PDFPLUMBER

        # 3. 文本密度高的文档使用PYMUPDF（性能更好）
        if characteristics.text_density > 0.7 and pymupdf_available:
            return ExtractionMethod.PYMUPDF

        # 4. 默认使用PYMUPDF（如果可用）
        if pymupdf_available:
            return ExtractionMethod.PYMUPDF

        # 5. 其次使用PDFPLUMBER
        if pdfplumber_available:
            return ExtractionMethod.PDFPLUMBER

        # 6. 最后使用PyPDF2
        return ExtractionMethod.PYPDF2
