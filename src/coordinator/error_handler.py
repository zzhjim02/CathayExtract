"""错误处理器实现"""
from datetime import datetime
from pathlib import Path
from typing import List


class ErrorHandler:
    """错误处理器,统一管理错误信息的记录和输出"""

    def __init__(self, log_file_path: Path = None):
        """
        初始化错误处理器

        Args:
            log_file_path: 日志文件路径(可选)
        """
        self.log_file_path = log_file_path
        self.errors: List[dict] = []

    def log_error(self, file_path: str, error_type: str, error_message: str):
        """
        记录错误信息

        Args:
            file_path: 发生错误的文件路径
            error_type: 错误类型
            error_message: 错误详情
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "error_type": error_type,
            "error_message": error_message,
        }
        self.errors.append(error_info)

    def get_error_messages(self) -> List[str]:
        """
        获取所有错误信息列表

        Returns:
            错误信息字符串列表
        """
        return [
            f"[{e['timestamp']}] {e['file_path']}: {e['error_type']} - {e['error_message']}"
            for e in self.errors
        ]

    def get_error_count(self) -> int:
        """
        获取错误总数

        Returns:
            错误数量
        """
        return len(self.errors)

    def write_log_file(self, output_path: Path):
        """
        将错误信息写入日志文件

        Args:
            output_path: 输出目录路径
        """
        if not self.errors:
            # 没有错误,不创建日志文件
            return

        log_file = output_path / "error_log.txt"

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("PDF OCR提取错误日志\n")
                f.write("=" * 50 + "\n\n")

                for error in self.errors:
                    f.write(f"时间: {error['timestamp']}\n")
                    f.write(f"文件: {error['file_path']}\n")
                    f.write(f"类型: {error['error_type']}\n")
                    f.write(f"详情: {error['error_message']}\n")
                    f.write("-" * 50 + "\n")

                f.write(f"\n总计: {len(self.errors)} 个错误\n")

        except Exception as e:
            # 日志写入失败不应影响主流程
            print(f"警告: 无法写入错误日志文件: {e}")

    def clear(self):
        """清空所有错误信息"""
        self.errors.clear()
