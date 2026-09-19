"""自定义异常类定义"""


class PDFExtractorError(Exception):
    """PDF提取工具的基础异常类"""
    pass


class ConfigError(PDFExtractorError):
    """配置错误异常"""
    pass


class FileNotFoundError(PDFExtractorError):
    """文件未找到异常"""
    pass


class PermissionError(PDFExtractorError):
    """权限错误异常"""
    pass


class PDFExtractionError(PDFExtractorError):
    """PDF文本提取错误异常"""
    pass


class EncodingError(PDFExtractorError):
    """编码转换错误异常"""
    pass


class FileWriteError(PDFExtractorError):
    """文件写入错误异常"""
    pass


class MethodNotAvailableError(PDFExtractorError):
    """提取方法不可用异常"""
    pass


class AllMethodsFailedError(PDFExtractorError):
    """所有提取方法都失败异常"""
    pass
