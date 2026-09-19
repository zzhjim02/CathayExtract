"""策略工厂"""
from typing import Optional, List

from .extraction_strategy import ExtractionStrategy
from .pymupdf_strategy import PyMuPDFStrategy
from .pdfplumber_strategy import PDFPlumberStrategy
from .pypdf2_strategy import PyPDF2Strategy
from ..core.config import ExtractionMethod
from ..core.exceptions import MethodNotAvailableError


class StrategyFactory:
    """策略工厂类"""

    _strategies = {
        ExtractionMethod.PYMUPDF: PyMuPDFStrategy(),
        ExtractionMethod.PDFPLUMBER: PDFPlumberStrategy(),
        ExtractionMethod.PYPDF2: PyPDF2Strategy(),
    }

    @classmethod
    def get_strategy(cls, method: ExtractionMethod) -> Optional[ExtractionStrategy]:
        """
        获取指定方法的策略实例

        Args:
            method: 提取方法

        Returns:
            策略实例，如果方法不可用则返回None
        """
        strategy = cls._strategies.get(method)
        if strategy and strategy.is_available:
            return strategy
        return None

    @classmethod
    def get_available_strategies(cls) -> List[ExtractionStrategy]:
        """
        获取所有可用的策略

        Returns:
            可用策略列表
        """
        return [
            strategy for strategy in cls._strategies.values()
            if strategy.is_available
        ]

    @classmethod
    def get_best_available_strategy(cls) -> Optional[ExtractionStrategy]:
        """
        获取性能最好的可用策略

        优先级：PYMUPDF > PDFPLUMBER > PyPDF2

        Returns:
            最佳可用策略
        """
        priority_order = [
            ExtractionMethod.PYMUPDF,
            ExtractionMethod.PDFPLUMBER,
            ExtractionMethod.PYPDF2
        ]

        for method in priority_order:
            strategy = cls.get_strategy(method)
            if strategy:
                return strategy

        return None

    @classmethod
    def get_all_methods_info(cls) -> dict:
        """
        获取所有方法的信息

        Returns:
            方法信息字典
        """
        return {
            method.value: strategy.get_method_info()
            for method, strategy in cls._strategies.items()
        }
