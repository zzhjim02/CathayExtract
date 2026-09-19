"""PYMUPDF提取策略"""
from pathlib import Path
from typing import Dict

from .extraction_strategy import ExtractionStrategy
from ..core.config import ExtractedText, ExtractionMethod
from ..core.exceptions import PDFExtractionError

try:
    import fitz  # pymupdf
except ImportError:
    fitz = None


class PyMuPDFStrategy(ExtractionStrategy):
    """PYMUPDF提取策略"""

    @property
    def method_name(self) -> ExtractionMethod:
        """获取提取方法名称"""
        return ExtractionMethod.PYMUPDF

    @property
    def is_available(self) -> bool:
        """检查PYMUPDF是否可用"""
        return fitz is not None

    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        使用PYMUPDF从PDF文件中提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象

        Raises:
            PDFExtractionError: 提取失败
        """
        if not self.is_available:
            raise PDFExtractionError("PYMUPDF库未安装")

        if not pdf_path.exists():
            raise PDFExtractionError(f"PDF文件不存在: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            text_parts = []

            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text and text.strip():
                    text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{text}\n")

            doc.close()

            full_text = "\n".join(text_parts)
            return ExtractedText(
                text=full_text,
                page_count=page_count,
                has_text=bool(text_parts)
            )

        except Exception as e:
            raise PDFExtractionError(f"PYMUPDF提取失败: {e}")

    def get_method_info(self) -> Dict[str, any]:
        """获取方法信息"""
        return {
            "name": "PYMUPDF",
            "version": fitz.__version__ if self.is_available else "未安装",
            "description": "高性能PDF提取库，速度最快",
            "best_for": "纯文本PDF、大文件处理",
            "available": self.is_available
        }
