"""文本文件写入器实现"""
from pathlib import Path

from ..core.config import ExtractedText
from ..core.exceptions import FileWriteError
from .directory_creator import DirectoryCreator


class TextFileWriter:
    """文本文件写入器"""

    def __init__(self, output_dir: Path, overwrite: bool = False):
        """
        初始化文件写入器

        Args:
            output_dir: 输出目录
            overwrite: 是否覆盖已存在的文件
        """
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.directory_creator = DirectoryCreator(output_dir)

    def write(self, relative_path: Path, extracted_text: ExtractedText) -> Path:
        """
        将提取的文本写入TXT文件

        Args:
            relative_path: 相对于输出根目录的路径
            extracted_text: 提取的文本信息

        Returns:
            写入的文件路径

        Raises:
            FileWriteError: 文件写入失败
        """
        # 创建目标目录结构
        target_dir = self.directory_creator.create_structure(relative_path)

        # 生成输出文件名(保持原文件名,仅扩展名改为.txt)
        output_filename = relative_path.stem + ".txt"
        output_path = target_dir / output_filename

        # 检查文件是否已存在
        if output_path.exists() and not self.overwrite:
            raise FileWriteError(f"文件已存在且不允许覆盖: {output_path}")

        try:
            # 写入文件(使用UTF-8编码)
            output_path.write_text(extracted_text.text, encoding="utf-8")
            return output_path
        except PermissionError:
            raise FileWriteError(f"无权限写入文件: {output_path}")
        except Exception as e:
            raise FileWriteError(f"文件写入失败: {e}")

    def exists(self, relative_path: Path) -> bool:
        """
        检查输出文件是否已存在

        Args:
            relative_path: 相对于输出根目录的路径

        Returns:
            文件是否存在
        """
        output_filename = relative_path.stem + ".txt"
        output_path = self.output_dir / relative_path.parent / output_filename
        return output_path.exists()
