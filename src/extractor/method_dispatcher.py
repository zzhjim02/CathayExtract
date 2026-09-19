"""方法调度器"""
from pathlib import Path
from typing import Optional, Tuple

from .method_selector import MethodSelector
from .strategy_factory import StrategyFactory
from .performance_tracker import PerformanceTracker
from ..core.config import ExtractedText, MethodSelectionMode, ExtractionMethod
from ..core.exceptions import PDFExtractionError, AllMethodsFailedError


class MethodDispatcher:
    """方法调度器"""

    def __init__(
        self,
        mode: MethodSelectionMode = MethodSelectionMode.AUTO,
        enable_performance_stats: bool = True,
        fallback_on_failure: bool = True
    ):
        """
        初始化方法调度器

        Args:
            mode: 方法选择模式
            enable_performance_stats: 是否启用性能统计
            fallback_on_failure: 失败时是否自动降级
        """
        self.mode = mode
        self.enable_performance_stats = enable_performance_stats
        self.fallback_on_failure = fallback_on_failure
        self.selector = MethodSelector()
        self.tracker = PerformanceTracker() if enable_performance_stats else None

    def dispatch(self, pdf_path: Path) -> Tuple[ExtractedText, Optional[ExtractionMethod]]:
        """
        调度提取方法

        Args:
            pdf_path: PDF文件路径

        Returns:
            (ExtractedText对象, 使用的方法)

        Raises:
            AllMethodsFailedError: 所有方法都失败
        """
        # 选择方法
        selected_method = self.selector.select_method(pdf_path, self.mode)

        if selected_method is None:
            raise AllMethodsFailedError("没有可用的提取方法")

        # 尝试使用选中的方法提取
        result, success = self._try_extract(pdf_path, selected_method)

        if success:
            return result, selected_method

        # 如果失败且启用了降级，尝试其他方法
        if self.fallback_on_failure:
            fallback_methods = self._get_fallback_methods(selected_method)
            for fallback_method in fallback_methods:
                result, success = self._try_extract(pdf_path, fallback_method)
                if success:
                    return result, fallback_method

        # 所有方法都失败
        raise AllMethodsFailedError(f"所有提取方法都失败: {pdf_path}")

    def _try_extract(
        self,
        pdf_path: Path,
        method: ExtractionMethod
    ) -> Tuple[Optional[ExtractedText], bool]:
        """
        尝试使用指定方法提取

        Args:
            pdf_path: PDF文件路径
            method: 提取方法

        Returns:
            (ExtractedText对象或None, 是否成功)
        """
        strategy = StrategyFactory.get_strategy(method)

        if strategy is None:
            return None, False

        # 开始性能跟踪
        if self.tracker:
            self.tracker.start_tracking(method)

        try:
            result = strategy.extract(pdf_path)

            # 结束性能跟踪
            if self.tracker:
                self.tracker.end_tracking(success=True)

            return result, True

        except Exception:
            # 结束性能跟踪
            if self.tracker:
                self.tracker.end_tracking(success=False)

            return None, False

    def _get_fallback_methods(self, failed_method: ExtractionMethod) -> list:
        """
        获取降级方法列表

        Args:
            failed_method: 失败的方法

        Returns:
            降级方法列表
        """
        all_methods = [
            ExtractionMethod.PYMUPDF,
            ExtractionMethod.PDFPLUMBER,
            ExtractionMethod.PYPDF2
        ]

        # 移除已失败的方法
        fallback_methods = [m for m in all_methods if m != failed_method]

        # 只返回可用的方法
        return [
            m for m in fallback_methods
            if StrategyFactory.get_strategy(m) is not None
        ]

    def get_performance_summary(self) -> Optional[str]:
        """
        获取性能统计摘要

        Returns:
            性能统计摘要字符串，如果未启用性能统计则返回None
        """
        if self.tracker:
            return self.tracker.get_summary()
        return None

    def reset_performance_stats(self):
        """重置性能统计"""
        if self.tracker:
            self.tracker.reset()
