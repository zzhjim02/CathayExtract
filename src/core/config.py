"""核心数据结构定义"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ExtractionMethod(Enum):
    """提取方法枚举"""
    PYMUPDF = "pymupdf"
    PDFPLUMBER = "pdfplumber"
    PYPDF2 = "pypdf2"
    AUTO = "auto"


class MethodSelectionMode(Enum):
    """方法选择模式"""
    AUTO = "auto"
    MANUAL_PYMUPDF = "pymupdf"
    MANUAL_PDFPLUMBER = "pdfplumber"
    MANUAL_PYPDF2 = "pypdf2"


@dataclass
class PDFCharacteristics:
    """PDF文件特征"""
    file_path: Path
    file_size: int
    page_count: int
    has_images: bool
    has_tables: bool
    has_complex_layout: bool
    text_density: float
    is_scanned: bool
    metadata: Dict = field(default_factory=dict)


@dataclass
class MethodPerformance:
    """单个方法的性能数据"""
    method: ExtractionMethod
    total_files: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0

    def update(self, success: bool, elapsed_time: float):
        """更新性能数据"""
        self.total_files += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_time += elapsed_time
        self.avg_time = self.total_time / self.total_files if self.total_files > 0 else 0.0


@dataclass
class PerformanceStatistics:
    """性能统计数据"""
    statistics: Dict[ExtractionMethod, MethodPerformance] = field(default_factory=dict)

    def __post_init__(self):
        """初始化所有方法的性能数据"""
        for method in [ExtractionMethod.PYMUPDF, ExtractionMethod.PDFPLUMBER, ExtractionMethod.PYPDF2]:
            if method not in self.statistics:
                self.statistics[method] = MethodPerformance(method=method)

    def update(self, method: ExtractionMethod, success: bool, elapsed_time: float):
        """更新指定方法的性能数据"""
        if method in self.statistics:
            self.statistics[method].update(success, elapsed_time)

    def get_summary(self) -> str:
        """获取性能统计摘要"""
        lines = ["=== 性能统计摘要 ==="]
        for method, perf in self.statistics.items():
            if perf.total_files > 0:
                success_rate = perf.success_count / perf.total_files * 100
                lines.append(
                    f"{method.value}: 处理{perf.total_files}个文件, "
                    f"成功率{success_rate:.1f}%, "
                    f"平均耗时{perf.avg_time:.3f}秒"
                )
        return "\n".join(lines)

    def get_best_method(self) -> Optional[ExtractionMethod]:
        """获取性能最好的方法"""
        best_method = None
        best_avg_time = float('inf')
        for method, perf in self.statistics.items():
            if perf.success_count > 0 and perf.avg_time < best_avg_time:
                best_avg_time = perf.avg_time
                best_method = method
        return best_method


@dataclass
class ExtractorConfig:
    """提取器配置类"""

    source_dir: Path  # 源目录路径
    output_dir: Path  # 输出目录路径
    file_pattern: str = "*"  # 文件名过滤模式,支持通配符
    overwrite: bool = False  # 是否覆盖已存在的文件
    verbose: bool = True  # 是否显示详细日志
    use_multithreading: bool = True  # 是否使用多线程处理
    max_threads: int = 4  # 最大线程数
    skip_existing: bool = True  # 是否跳过已处理的文件
    method_selection_mode: MethodSelectionMode = MethodSelectionMode.AUTO  # 方法选择模式
    enable_performance_stats: bool = True  # 是否启用性能统计
    fallback_on_failure: bool = True  # 失败时是否自动降级

    def __post_init__(self):
        """验证配置参数"""
        if not isinstance(self.source_dir, Path):
            self.source_dir = Path(self.source_dir)
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)


@dataclass
class PDFFileInfo:
    """PDF文件信息类"""

    file_path: Path  # PDF文件的完整路径
    relative_path: Path  # 相对于源目录的路径
    file_size: int  # 文件大小(字节)
    is_valid: bool = True  # 文件是否有效
    error_message: Optional[str] = None  # 错误信息(如果文件无效)


@dataclass
class ExtractedText:
    """提取的文本信息类"""

    text: str  # 提取的文本内容
    encoding: str = "utf-8"  # 文本编码
    page_count: int = 0  # PDF页数
    has_text: bool = True  # 是否包含文本


@dataclass
class ProcessingResult:
    """处理结果类"""

    total_files: int = 0  # 总文件数
    success_count: int = 0  # 成功处理的文件数
    failed_count: int = 0  # 失败的文件数
    skipped_count: int = 0  # 跳过的文件数
    errors: List[str] = field(default_factory=list)  # 错误信息列表
    start_time: datetime = field(default_factory=datetime.now)  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间

    @property
    def duration(self) -> float:
        """获取处理时长(秒)"""
        if self.end_time is None:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    def add_error(self, error_message: str):
        """添加错误信息"""
        self.errors.append(error_message)

    def get_summary(self) -> str:
        """获取处理结果摘要"""
        summary = (
            f"处理完成!\n"
            f"总文件数: {self.total_files}\n"
            f"成功: {self.success_count}\n"
            f"失败: {self.failed_count}\n"
            f"跳过: {self.skipped_count}\n"
            f"耗时: {self.duration:.2f}秒"
        )
        if self.errors:
            summary += f"\n错误数: {len(self.errors)}"
        return summary
