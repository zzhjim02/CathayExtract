"""PDF文本提取器实现"""
from pathlib import Path
from typing import Optional

from ..core.config import ExtractedText
from ..core.exceptions import PDFExtractionError

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


class PDFTextExtractor:
    """PDF文本提取器,支持多种提取策略"""

    def __init__(self, use_pdfplumber_fallback: bool = True):
        """
        初始化PDF文本提取器

        Args:
            use_pdfplumber_fallback: 是否在PyPDF2失败时使用pdfplumber作为备选
        """
        self.use_pdfplumber_fallback = use_pdfplumber_fallback

    def extract(self, pdf_path: Path) -> ExtractedText:
        """
        从PDF文件中提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象

        Raises:
            PDFExtractionError: PDF文件损坏或提取失败
        """
        if not pdf_path.exists():
            raise PDFExtractionError(f"PDF文件不存在: {pdf_path}")

        # 首先尝试使用PyPDF2
        try:
            if PyPDF2:
                return self._extract_using_pypdf2(pdf_path)
        except Exception as e:
            if self.use_pdfplumber_fallback and pdfplumber:
                # 如果PyPDF2失败,尝试使用pdfplumber
                try:
                    return self._extract_using_pdfplumber(pdf_path)
                except Exception as e2:
                    raise PDFExtractionError(f"PDF文本提取失败: {e2}")
            else:
                raise PDFExtractionError(f"PDF文本提取失败: {e}")

        # 如果PyPDF2未安装,直接使用pdfplumber
        if pdfplumber:
            return self._extract_using_pdfplumber(pdf_path)
        else:
            raise PDFExtractionError("未安装PDF处理库(PyPDF2或pdfplumber)")

    def _extract_using_pypdf2(self, pdf_path: Path) -> ExtractedText:
        """
        使用PyPDF2提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象
        """
        try:
            reader = PyPDF2.PdfReader(pdf_path)
            page_count = len(reader.pages)
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"=== 第 {page_num} 页 ===\n{page_text}\n")
                except Exception as e:
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

    def _extract_using_pdfplumber(self, pdf_path: Path) -> ExtractedText:
        """
        使用pdfplumber提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            ExtractedText对象
        """
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
                    except Exception as e:
                        # 跳过无法提取的页面
                        continue

            if not text_parts:
                return ExtractedText(text="", page_count=page_count, has_text=False)

            full_text = "\n".join(text_parts)
            return ExtractedText(text=full_text, page_count=page_count, has_text=True)

        except Exception as e:
            raise PDFExtractionError(f"pdfplumber提取失败: {e}")
