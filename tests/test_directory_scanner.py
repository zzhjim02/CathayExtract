"""DirectoryScanner单元测试"""
import pytest
from pathlib import Path
import tempfile
import shutil

from src.scanner import DirectoryScanner
from src.core.config import ExtractorConfig


class TestDirectoryScanner:
    """DirectoryScanner测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def sample_pdf_files(self, temp_dir):
        """创建示例PDF文件"""
        # 创建一些PDF文件
        (temp_dir / "file1.pdf").write_text("PDF content 1")
        (temp_dir / "file2.pdf").write_text("PDF content 2")

        # 创建子目录和PDF文件
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.pdf").write_text("PDF content 3")

        return temp_dir

    def test_scan_basic(self, sample_pdf_files):
        """测试基本扫描功能"""
        config = ExtractorConfig(source_dir=sample_pdf_files, output_dir=Path("output"))
        scanner = DirectoryScanner(config)

        pdf_files = scanner.scan()

        assert len(pdf_files) == 3
        assert all(pdf.is_valid for pdf in pdf_files)

    def test_scan_with_pattern(self, sample_pdf_files):
        """测试文件名过滤"""
        # 创建额外的PDF文件
        (sample_pdf_files / "report.pdf").write_text("Report content")

        config = ExtractorConfig(
            source_dir=sample_pdf_files, output_dir=Path("output"), file_pattern="report*.pdf"
        )
        scanner = DirectoryScanner(config)

        pdf_files = scanner.scan()

        assert len(pdf_files) == 1
        assert pdf_files[0].file_path.name == "report.pdf"

    def test_scan_nonexistent_dir(self):
        """测试扫描不存在的目录"""
        config = ExtractorConfig(source_dir=Path("nonexistent"), output_dir=Path("output"))
        scanner = DirectoryScanner(config)

        with pytest.raises(FileNotFoundError):
            scanner.scan()

    def test_scan_empty_dir(self, temp_dir):
        """测试扫描空目录"""
        config = ExtractorConfig(source_dir=temp_dir, output_dir=Path("output"))
        scanner = DirectoryScanner(config)

        pdf_files = scanner.scan()

        assert len(pdf_files) == 0
