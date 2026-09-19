"""文本文件写入器实现

输出格式与 **CathayOCR Pro 默认导出格式**一致：

    OCR文本提取结果
    ============================================================
    源文件: xxx
    总页数: N
    渲染倍数: -
    提取时间: 2026-09-19 16:40:00
    ============================================================

    ============================================================
    第 1 页
    ============================================================

    行1
    行2
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.config import ExtractedText
from ..core.exceptions import FileWriteError
from .directory_creator import DirectoryCreator

#: 与 CathayOCR Pro 一致的分隔线
SEP = "=" * 60
#: 与 CathayOCR Pro 一致的标题行
HEADER_TITLE = "OCR文本提取结果"
#: 提取工具不涉及图像渲染，渲染倍数一栏保留该行以完全对齐格式
DEFAULT_SCALE_NOTE = "-"


def format_result_txt(source_stem: str, extracted: ExtractedText,
                      scale_note: str = DEFAULT_SCALE_NOTE) -> str:
    """按 CathayOCR Pro 默认格式拼装 TXT 内容

    Args:
        source_stem: 源 PDF 文件名(不含扩展名)
        extracted: 提取结果(需带 page_texts)
        scale_note: 渲染倍数栏内容

    Returns:
        TXT 文本内容
    """
    lines = [
        HEADER_TITLE,
        SEP,
        f"源文件: {source_stem}",
        f"总页数: {extracted.page_count}",
        f"渲染倍数: {scale_note}",
        f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        SEP,
        "",
    ]
    for page_num, page_text in enumerate(extracted.page_texts or [], 1):
        if not (page_text or "").strip():
            continue  # 无文字的页不输出，与 CathayOCR 行为一致
        lines.append("")
        lines.append(SEP)
        lines.append(f"第 {page_num} 页")
        lines.append(SEP)
        lines.append("")
        lines.extend(page_text.splitlines())
    return "\n".join(lines) + "\n"


class TextFileWriter:
    """文本文件写入器"""

    def __init__(self, output_dir: Path, overwrite: bool = False, formatted: bool = True):
        """
        初始化文件写入器

        Args:
            output_dir: 输出目录
            overwrite: 是否覆盖已存在的文件
            formatted: 是否按 CathayOCR Pro 格式输出(有分页信息时生效)
        """
        self.output_dir = Path(output_dir)
        self.overwrite = overwrite
        self.formatted = formatted
        self.directory_creator = DirectoryCreator(self.output_dir)

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

        content = extracted_text.text
        if self.formatted and getattr(extracted_text, "page_texts", None):
            content = format_result_txt(relative_path.stem, extracted_text)

        try:
            # 写入文件(使用UTF-8编码)
            output_path.write_text(content, encoding="utf-8")
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

    def target_path(self, relative_path: Path) -> Path:
        """计算输出文件路径(不创建、不写入)"""
        return self.output_dir / relative_path.parent / (relative_path.stem + ".txt")
