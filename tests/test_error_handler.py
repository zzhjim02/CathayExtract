"""ErrorHandler单元测试"""
import pytest
from pathlib import Path
import tempfile
import shutil

from src.coordinator import ErrorHandler


class TestErrorHandler:
    """ErrorHandler测试类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_log_error(self):
        """测试记录错误"""
        handler = ErrorHandler()

        handler.log_error("test.pdf", "TestError", "测试错误消息")

        assert handler.get_error_count() == 1

    def test_log_multiple_errors(self):
        """测试记录多个错误"""
        handler = ErrorHandler()

        handler.log_error("file1.pdf", "Error1", "错误1")
        handler.log_error("file2.pdf", "Error2", "错误2")
        handler.log_error("file3.pdf", "Error3", "错误3")

        assert handler.get_error_count() == 3

    def test_get_error_messages(self):
        """测试获取错误消息"""
        handler = ErrorHandler()

        handler.log_error("test.pdf", "TestError", "测试错误消息")

        messages = handler.get_error_messages()

        assert len(messages) == 1
        assert "test.pdf" in messages[0]
        assert "TestError" in messages[0]

    def test_write_log_file(self, temp_dir):
        """测试写入日志文件"""
        handler = ErrorHandler()

        handler.log_error("test.pdf", "TestError", "测试错误消息")

        handler.write_log_file(temp_dir)

        log_file = temp_dir / "error_log.txt"
        assert log_file.exists()

        content = log_file.read_text(encoding="utf-8")
        assert "test.pdf" in content
        assert "TestError" in content

    def test_write_log_file_no_errors(self, temp_dir):
        """测试无错误时不创建日志文件"""
        handler = ErrorHandler()

        handler.write_log_file(temp_dir)

        log_file = temp_dir / "error_log.txt"
        assert not log_file.exists()

    def test_clear(self):
        """测试清除错误"""
        handler = ErrorHandler()

        handler.log_error("test.pdf", "TestError", "测试错误消息")
        assert handler.get_error_count() == 1

        handler.clear()
        assert handler.get_error_count() == 0
