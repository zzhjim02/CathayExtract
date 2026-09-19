"""PDFTextExtractor单元测试"""
import pytest
from pathlib import Path
import tempfile
import shutil

from src.extractor import PDFTextExtractor
from src.core.exceptions import PDFExtractionError


class TestPDFTextExtractor:
    """PDFTextExtractor测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_extract_nonexistent_file(self):
        """测试提取不存在的文件"""
        extractor = PDFTextExtractor()

        with pytest.raises(PDFExtractionError):
            extractor.extract(Path("nonexistent.pdf"))

    def test_extractor_initialization(self):
        """测试提取器初始化"""
        extractor = PDFTextExtractor(use_pdfplumber_fallback=True)
        assert extractor.use_pdfplumber_fallback is True

        extractor2 = PDFTextExtractor(use_pdfplumber_fallback=False)
        assert extractor2.use_pdfplumber_fallback is False
