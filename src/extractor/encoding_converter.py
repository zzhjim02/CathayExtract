"""编码转换器实现"""
import codecs
from ..core.exceptions import EncodingError
from .encoding_detector import EncodingDetector


class EncodingConverter:
    """文本编码转换器"""

    # 尝试的编码顺序
    ENCODING_TRIAL_ORDER = ["utf-8", "gbk", "gb18030", "big5", "latin-1"]

    @staticmethod
    def convert_to_utf8(data: bytes, source_encoding: Optional[str] = None) -> str:
        """
        将文本数据转换为UTF-8编码

        Args:
            data: 文本字节序列
            source_encoding: 源编码(可选,如果为None则自动检测)

        Returns:
            UTF-8编码的文本字符串

        Raises:
            EncodingError: 编码转换失败
        """
        if not data:
            return ""

        # 如果未指定源编码,自动检测
        if source_encoding is None:
            source_encoding = EncodingDetector.detect(data)

        # 尝试使用检测到的编码解码
        try:
            text = data.decode(source_encoding)
            # 确保是有效的UTF-8
            return text.encode("utf-8", errors="ignore").decode("utf-8")
        except UnicodeDecodeError:
            # 如果检测到的编码失败,尝试其他常见编码
            for enc in EncodingConverter.ENCODING_TRIAL_ORDER:
                if enc == source_encoding:
                    continue
                try:
                    text = data.decode(enc)
                    return text.encode("utf-8", errors="ignore").decode("utf-8")
                except UnicodeDecodeError:
                    continue

            # 所有尝试都失败,使用错误处理模式
            try:
                return data.decode("utf-8", errors="ignore")
            except Exception as e:
                raise EncodingError(f"编码转换失败: {e}")

    @staticmethod
    def convert_text_to_utf8(text: str) -> str:
        """
        将文本字符串转换为UTF-8编码

        Args:
            text: 文本字符串

        Returns:
            UTF-8编码的文本字符串
        """
        if not text:
            return ""

        try:
            # 尝试重新编码为UTF-8
            return text.encode("utf-8", errors="ignore").decode("utf-8")
        except Exception:
            # 如果失败,返回原始文本
            return text
