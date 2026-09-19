"""目录结构创建器实现"""
from pathlib import Path

from ..core.exceptions import FileWriteError


class DirectoryCreator:
    """目录结构创建器"""

    def __init__(self, output_dir: Path):
        """
        初始化目录创建器

        Args:
            output_dir: 输出根目录
        """
        self.output_dir = output_dir

    def create_structure(self, relative_path: Path) -> Path:
        """
        根据相对路径创建目录结构

        Args:
            relative_path: 相对于输出根目录的路径

        Returns:
            创建的目录路径

        Raises:
            FileWriteError: 目录创建失败
        """
        if not relative_path or relative_path == Path("."):
            # 根目录下的文件,不需要创建子目录
            return self.output_dir

        target_dir = self.output_dir / relative_path.parent

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            return target_dir
        except PermissionError:
            raise FileWriteError(f"无权限创建目录: {target_dir}")
        except Exception as e:
            raise FileWriteError(f"目录创建失败: {e}")
