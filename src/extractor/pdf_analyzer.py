"""PDF文件特征分析器"""
from pathlib import Path

from ..core.config import PDFCharacteristics

try:
    import fitz  # pymupdf
except ImportError:
    fitz = None


class PDFAnalyzer:
    """PDF文件特征分析器"""

    def analyze(self, pdf_path: Path) -> PDFCharacteristics:
        """
        分析PDF文件特征

        Args:
            pdf_path: PDF文件路径

        Returns:
            PDFCharacteristics对象
        """
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0

        if not fitz:
            # 如果PYMUPDF不可用，返回默认特征
            return PDFCharacteristics(
                file_path=pdf_path,
                file_size=file_size,
                page_count=0,
                has_images=False,
                has_tables=False,
                has_complex_layout=False,
                text_density=0.5,
                is_scanned=False,
                metadata={}
            )

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)

            has_images = False
            has_text = False
            text_chars = 0

            for page in doc:
                # 检查是否有图像
                images = page.get_images()
                if images:
                    has_images = True

                # 检查是否有文本
                text = page.get_text()
                if text.strip():
                    has_text = True
                    text_chars += len(text)

            doc.close()

            # 计算文本密度
            text_density = text_chars / (file_size / 10) if file_size > 0 else 0
            text_density = min(1.0, text_density)

            # 判断是否为扫描件
            is_scanned = has_images and not has_text

            return PDFCharacteristics(
                file_path=pdf_path,
                file_size=file_size,
                page_count=page_count,
                has_images=has_images,
                has_tables=False,  # 简化处理，暂不检测表格
                has_complex_layout=False,  # 简化处理，暂不检测复杂布局
                text_density=text_density,
                is_scanned=is_scanned,
                metadata={}
            )

        except Exception:
            # 分析失败时返回默认特征
            return PDFCharacteristics(
                file_path=pdf_path,
                file_size=file_size,
                page_count=0,
                has_images=False,
                has_tables=False,
                has_complex_layout=False,
                text_density=0.5,
                is_scanned=False,
                metadata={}
            )
