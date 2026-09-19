"""编码检测器实现"""
import chardet
from typing import Optional


class EncodingDetector:
    """文本编码检测器"""

    # 常见中文编码列表
    COMMON_ENCODINGS = ["utf-8", "gbk", "gb18030", "big5", "utf-16", "utf-32"]

    @staticmethod
    def detect(data: bytes) -> str:
        """
        检测文本编码

        Args:
            data: 文本字节序列

        Returns:
            检测到的编码名称,默认返回"utf-8"
        """
        if not data:
            return "utf-8"

        try:
            # 使用chardet检测编码
            result = chardet.detect(data)
            encoding = result.get("encoding", "utf-8")
            confidence = result.get("confidence", 0)

            # 如果置信度太低,尝试常见编码
            if confidence < 0.7:
                for enc in EncodingDetector.COMMON_ENCODINGS:
                    try:
                        data.decode(enc)
                        return enc
                    except UnicodeDecodeError:
                        continue

            return encoding if encoding else "utf-8"

        except Exception:
            # 检测失败,返回默认编码
            return "utf-8"
