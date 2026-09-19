"""PyPDF2提取策略"""
from pathlib import Path
from typing import Dict

from .extraction_strategy import ExtractionStrategy
from ..core.config import ExtractedText, ExtractionMethod
from ..core.exceptions import PDFExtractionError

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class PyPDF2Strategy(ExtractionStrategy):
    """PyPDF2提取策略"""

    @property
    def method_name(self) -> ExtractionMethod:
        """获取提取方法名称"""
        return ExtractionMethod.PYPDF2

    @property
    def is_available(self) -> bool:
        """检查PyPDF2是否可用"""
        return PyPDF2 is not None

    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        使用PyPDF2从PDF文件中提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象

        Raises:
            PDFExtractionError: 提取失败
        """
        if not self.is_available:
            raise PDFExtractionError("PyPDF2库未安装")

        if not pdf_path.exists():
            raise PDFExtractionError(f"PDF文件不存在: {pdf_path}")

        try:
            reader = PyPDF2.PdfReader(pdf_path)
            page_count = len(reader.pages)
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
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

        except PyPDF2.PdfReadError as e:
            raise PDFExtractionError(f"PDF文件损坏或格式错误: {e}")
        except Exception as e:
            raise PDFExtractionError(f"PyPDF2提取失败: {e}")

    def get_method_info(self) -> Dict[str, any]:
        """获取方法信息"""
        return {
            "name": "PyPDF2",
            "version": PyPDF2.__version__ if self.is_available else "未安装",
            "description": "纯Python实现的PDF库",
            "best_for": "简单PDF、兼容性好",
            "available": self.is_available
        }
