"""性能跟踪器"""
import time
import threading
from typing import Optional

from ..core.config import PerformanceStatistics, ExtractionMethod


class PerformanceTracker:
    """性能跟踪器"""

    def __init__(self):
        """初始化性能跟踪器"""
        self._statistics = PerformanceStatistics()
        self._lock = threading.Lock()
        self._current_start_time: Optional[float] = None
        self._current_method: Optional[ExtractionMethod] = None

    def start_tracking(self, method: ExtractionMethod):
        """
        开始跟踪

        Args:
            method: 提取方法
        """
        with self._lock:
            self._current_start_time = time.time()
            self._current_method = method

    def end_tracking(self, success: bool):
        """
        结束跟踪

        Args:
            success: 是否成功
        """
        with self._lock:
            if self._current_start_time is not None and self._current_method is not None:
                elapsed_time = time.time() - self._current_start_time
                self._statistics.update(self._current_method, success, elapsed_time)

                # 重置当前跟踪状态
                self._current_start_time = None
                self._current_method = None

    def get_statistics(self) -> PerformanceStatistics:
        """
        获取性能统计数据

        Returns:
            PerformanceStatistics对象
        """
        with self._lock:
            return self._statistics

    def get_summary(self) -> str:
        """
        获取性能统计摘要

        Returns:
            性能统计摘要字符串
        """
        with self._lock:
            return self._statistics.get_summary()

    def reset(self):
        """重置性能统计"""
        with self._lock:
            self._statistics = PerformanceStatistics()
            self._current_start_time = None
            self._current_method = None
