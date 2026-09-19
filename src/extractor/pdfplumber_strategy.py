"""PDFPLUMBER提取策略"""
from pathlib import Path
from typing import Dict

from .extraction_strategy import ExtractionStrategy
from ..core.config import ExtractedText, ExtractionMethod
from ..core.exceptions import PDFExtractionError

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


class PDFPlumberStrategy(ExtractionStrategy):
    """PDFPLUMBER提取策略"""

    @property
    def method_name(self) -> ExtractionMethod:
        """获取提取方法名称"""
        return ExtractionMethod.PDFPLUMBER

    @property
    def is_available(self) -> bool:
        """检查PDFPLUMBER是否可用"""
        return pdfplumber is not None

    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        使用PDFPLUMBER从PDF文件中提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象

        Raises:
            PDFExtractionError: 提取失败
        """
        if not self.is_available:
            raise PDFExtractionError("PDFPLUMBER库未安装")

        if not pdf_path.exists():
            raise PDFExtractionError(f"PDF文件不存在: {pdf_path}")

        try:
            text_parts = []
            page_count = 0

            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(f"=== 第 {page_num} 页 ===\n{page_text}\n")
                    except Exception:
                        # 跳过无法提取的页面
                        continue

            if not text_parts:
                return ExtractedText(text="", page_count=page_count, has_text=False)

            full_text = "\n".join(text_parts)
            return ExtractedText(text=full_text, page_count=page_count, has_text=True)

        except Exception as e:
            raise PDFExtractionError(f"PDFPLUMBER提取失败: {e}")

    def get_method_info(self) -> Dict[str, any]:
        """获取方法信息"""
        return {
            "name": "PDFPLUMBER",
            "version": pdfplumber.__version__ if self.is_available else "未安装",
            "description": "擅长处理复杂布局和表格",
            "best_for": "复杂布局、表格、扫描件",
            "available": self.is_available
        }
