"""TextFileWriter单元测试"""
import pytest
from pathlib import Path
import tempfile
import shutil

from src.writer import TextFileWriter
from src.core.config import ExtractedText


class TestTextFileWriter:
    """TextFileWriter测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_write_basic(self, temp_dir):
        """测试基本写入功能"""
        writer = TextFileWriter(temp_dir, overwrite=True)

        extracted_text = ExtractedText(text="测试文本内容", page_count=1, has_text=True)
        relative_path = Path("test.pdf")

        output_path = writer.write(relative_path, extracted_text)

        assert output_path.exists()
        assert output_path.name == "test.txt"
        assert output_path.read_text(encoding="utf-8") == "测试文本内容"

    def test_write_with_subdirectory(self, temp_dir):
        """测试写入子目录"""
        writer = TextFileWriter(temp_dir, overwrite=True)

        extracted_text = ExtractedText(text="子目录测试", page_count=1, has_text=True)
        relative_path = Path("subdir/test.pdf")

        output_path = writer.write(relative_path, extracted_text)

        assert output_path.exists()
        assert output_path.parent.name == "subdir"

    def test_overwrite_false(self, temp_dir):
        """测试不覆盖已存在的文件"""
        writer = TextFileWriter(temp_dir, overwrite=False)

        extracted_text = ExtractedText(text="第一次写入", page_count=1, has_text=True)
        relative_path = Path("test.pdf")

        # 第一次写入
        writer.write(relative_path, extracted_text)

        # 第二次写入相同文件
        extracted_text2 = ExtractedText(text="第二次写入", page_count=1, has_text=True)
        with pytest.raises(Exception):  # 应该抛出FileWriteError
            writer.write(relative_path, extracted_text2)

    def test_overwrite_true(self, temp_dir):
        """测试覆盖已存在的文件"""
        writer = TextFileWriter(temp_dir, overwrite=True)

        extracted_text = ExtractedText(text="第一次写入", page_count=1, has_text=True)
        relative_path = Path("test.pdf")

        # 第一次写入
        writer.write(relative_path, extracted_text)

        # 第二次写入相同文件(应该覆盖)
        extracted_text2 = ExtractedText(text="第二次写入", page_count=1, has_text=True)
        output_path = writer.write(relative_path, extracted_text2)

        assert output_path.read_text(encoding="utf-8") == "第二次写入"
