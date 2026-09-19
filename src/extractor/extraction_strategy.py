"""提取策略抽象基类"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from ..core.config import ExtractedText, ExtractionMethod
from ..core.exceptions import PDFExtractionError


class ExtractionStrategy(ABC):
    """提取策略抽象基类"""

    @property
    @abstractmethod
    def method_name(self) -> ExtractionMethod:
        """获取提取方法名称"""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """检查提取方法是否可用"""
        pass

    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        从PDF文件中提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象

        Raises:
            PDFExtractionError: 提取失败
        """
        pass

    @abstractmethod
    def get_method_info(self) -> Dict[str, any]:
        """
        获取方法信息

        Returns:
            包含方法名称、版本、描述等信息的字典
        """
        pass
