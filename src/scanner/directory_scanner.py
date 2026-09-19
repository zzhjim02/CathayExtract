"""目录扫描器实现"""
from pathlib import Path
from typing import List, Generator
import fnmatch

from ..core.config import ExtractorConfig, PDFFileInfo
from ..core.exceptions import PermissionError


class DirectoryScanner:
    """目录扫描器,支持递归扫描和文件过滤"""

    def __init__(self, config: ExtractorConfig):
        """
        初始化目录扫描器

        Args:
            config: 提取器配置对象
        """
        self.config = config

    def scan(self) -> List[PDFFileInfo]:
        """
        扫描目录,返回所有PDF文件信息

        若配置里带显式待处理清单(拖入的文件/文件夹),优先使用该清单。

        Returns:
            PDFFileInfo列表
        """
        if self.config.file_list:
            return self.scan_paths(self.config.file_list)

        if not self.config.source_dir.exists():
            raise FileNotFoundError(f"源目录不存在: {self.config.source_dir}")

        if not self.config.source_dir.is_dir():
            raise ValueError(f"源路径不是目录: {self.config.source_dir}")

        pdf_files = []
        for pdf_info in self._scan_recursive():
            if self._matches_pattern(pdf_info.file_path.name):
                pdf_files.append(pdf_info)

        return pdf_files

    def scan_paths(self, paths) -> List[PDFFileInfo]:
        """
        扫描「拖入的文件 / 文件夹」混合列表

        - 文件夹：递归取其下的 PDF（受 file_pattern 过滤）
        - 文件：只要是 .pdf 就直接收（不受过滤影响）

        Args:
            paths: 路径列表（Path 或字符串，可混排）

        Returns:
            PDFFileInfo列表
        """
        pdf_files = []
        seen = set()
        for raw in paths:
            path = Path(raw)
            if path.is_dir():
                for item in sorted(path.rglob("*.pdf")):
                    if not item.is_file() or item in seen:
                        continue
                    if not self._matches_pattern(item.name):
                        continue
                    seen.add(item)
                    pdf_files.append(self._create_pdf_info(item, base=path))
            elif path.is_file() and path.suffix.lower() == ".pdf":
                if path in seen:
                    continue
                seen.add(path)
                pdf_files.append(self._create_pdf_info(path))
        return pdf_files

    def _scan_recursive(self) -> Generator[PDFFileInfo, None, None]:
        """
        递归扫描目录

        Yields:
            PDFFileInfo对象
        """
        try:
            for item in self.config.source_dir.rglob("*.pdf"):
                try:
                    if item.is_file():
                        file_info = self._create_pdf_info(item)
                        if file_info.is_valid:
                            yield file_info
                except PermissionError:
                    # 跳过无权限访问的文件
                    continue
                except Exception as e:
                    # 记录错误但继续处理其他文件
                    error_info = PDFFileInfo(
                        file_path=item,
                        relative_path=item.relative_to(self.config.source_dir),
                        file_size=0,
                        is_valid=False,
                        error_message=str(e),
                    )
                    yield error_info
        except PermissionError:
            raise PermissionError(f"无权限访问目录: {self.config.source_dir}")

    def _create_pdf_info(self, file_path: Path, base: Path = None) -> PDFFileInfo:
        """
        创建PDF文件信息

        Args:
            file_path: PDF文件路径
            base: 相对路径的基准目录（默认源目录；不在基准下时只用文件名）

        Returns:
            PDFFileInfo对象
        """
        base = Path(base) if base is not None else self.config.source_dir
        try:
            try:
                relative_path = file_path.relative_to(base)
            except ValueError:
                relative_path = Path(file_path.name)
            file_size = file_path.stat().st_size

            if file_size == 0:
                return PDFFileInfo(
                    file_path=file_path,
                    relative_path=relative_path,
                    file_size=file_size,
                    is_valid=False,
                    error_message="文件为空",
                )

            return PDFFileInfo(
                file_path=file_path,
                relative_path=relative_path,
                file_size=file_size,
                is_valid=True,
            )
        except Exception as e:
            return PDFFileInfo(
                file_path=file_path,
                relative_path=file_path,
                file_size=0,
                is_valid=False,
                error_message=str(e),
            )

    def _matches_pattern(self, filename: str) -> bool:
        """
        检查文件名是否匹配过滤模式

        Args:
            filename: 文件名

        Returns:
            是否匹配
        """
        if not self.config.file_pattern or self.config.file_pattern == "*":
            return True
        return fnmatch.fnmatch(filename, self.config.file_pattern)
