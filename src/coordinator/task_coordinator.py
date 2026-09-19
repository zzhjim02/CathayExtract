"""任务协调器实现"""
from datetime import datetime
from PyQt6.QtCore import QThread, QThreadPool, QRunnable, pyqtSignal, QObject
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..core.config import ExtractorConfig, ProcessingResult
from ..core.exceptions import PDFExtractorError
from ..scanner import DirectoryScanner
from ..extractor import PDFTextExtractor, EncodingConverter, MethodDispatcher
from ..writer import TextFileWriter
from .error_handler import ErrorHandler


class WorkerSignals(QObject):
    """工作线程信号"""
    progress_updated = pyqtSignal(int, int, str)  # 当前进度,总数,当前文件路径
    file_processed = pyqtSignal(str, str, bool)  # 文件路径,状态消息,是否成功


class PDFProcessingTask(QRunnable):
    """PDF处理任务,用于多线程执行"""

    def __init__(self, pdf_info, extractor, encoding_converter, writer, config, signals):
        """
        初始化PDF处理任务

        Args:
            pdf_info: PDF文件信息
            extractor: PDF文本提取器
            encoding_converter: 编码转换器
            writer: 文件写入器
            config: 配置对象
            signals: 信号对象
        """
        super().__init__()
        self.pdf_info = pdf_info
        self.extractor = extractor
        self.encoding_converter = encoding_converter
        self.writer = writer
        self.config = config
        self.signals = signals
        self.should_stop = False
        self.result = {"success": False, "skipped": False, "error": None}

    def run(self):
        """执行PDF处理任务"""
        file_path = self.pdf_info.file_path

        try:
            # 检查是否应该停止
            if self.should_stop:
                return

            # 检查文件是否有效
            if not self.pdf_info.is_valid:
                error_msg = f"文件无效: {self.pdf_info.error_message}"
                self.result["error"] = error_msg
                self.signals.file_processed.emit(str(file_path), error_msg, False)
                return

            # 检查文件是否已处理(跳过已处理的文件)
            if self.config.skip_existing and not self.config.overwrite:
                if self.writer.exists(self.pdf_info.relative_path):
                    self.result["skipped"] = True
                    msg = "文件已存在,跳过"
                    self.signals.file_processed.emit(str(file_path), msg, True)
                    return

            # 提取文本
            extracted_text = self.extractor.extract(file_path)

            # 检查是否包含文本
            if not extracted_text.has_text:
                error_msg = "PDF文件不包含可提取的文本"
                self.result["error"] = error_msg
                self.signals.file_processed.emit(str(file_path), error_msg, False)
                return

            # 转换编码
            if extracted_text.encoding != "utf-8":
                try:
                    text_bytes = extracted_text.text.encode(extracted_text.encoding)
                    extracted_text.text = self.encoding_converter.convert_to_utf8(
                        text_bytes, extracted_text.encoding
                    )
                except Exception as e:
                    # 编码转换失败,使用原始文本
                    pass

            # 写入文件
            output_path = self.writer.write(self.pdf_info.relative_path, extracted_text)
            msg = f"提取成功 -> {output_path}"
            self.result["success"] = True
            self.signals.file_processed.emit(str(file_path), msg, True)

        except PDFExtractorError as e:
            error_msg = str(e)
            self.result["error"] = error_msg
            self.signals.file_processed.emit(str(file_path), error_msg, False)
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self.result["error"] = error_msg
            self.signals.file_processed.emit(str(file_path), error_msg, False)

    def stop(self):
        """停止任务"""
        self.should_stop = True


class TaskCoordinator(QThread):
    """任务协调器,支持多线程处理"""

    # 信号定义
    progress_updated = pyqtSignal(int, int, str)  # 当前进度,总数,当前文件路径
    file_processed = pyqtSignal(str, str, bool)  # 文件路径,状态消息,是否成功
    processing_completed = pyqtSignal(object)  # ProcessingResult对象
    error_occurred = pyqtSignal(str)  # 错误信息
    performance_stats_updated = pyqtSignal(str)  # 性能统计摘要

    def __init__(self, config: ExtractorConfig):
        """
        初始化任务协调器

        Args:
            config: 提取器配置对象
        """
        super().__init__()
        self.config = config
        self._is_running = False
        self._should_stop = False
        self.worker_signals = WorkerSignals()
        self.tasks = []  # 存储所有任务,用于停止

        # 初始化组件
        self.scanner = DirectoryScanner(config)
        self.extractor = PDFTextExtractor()
        self.encoding_converter = EncodingConverter()
        self.error_handler = ErrorHandler()

        # 初始化方法调度器
        self.method_dispatcher = MethodDispatcher(
            mode=config.method_selection_mode,
            enable_performance_stats=config.enable_performance_stats,
            fallback_on_failure=config.fallback_on_failure
        )

        # 连接工作线程信号
        self.worker_signals.progress_updated.connect(self.progress_updated.emit)
        self.worker_signals.file_processed.connect(self.file_processed.emit)

    def stop(self):
        """停止正在运行的任务"""
        self._should_stop = True
        # 停止所有任务
        for task in self.tasks:
            task.stop()

    def run(self):
        """执行PDF处理流程"""
        self._is_running = True
        self._should_stop = False
        result = ProcessingResult()

        try:
            # 1. 扫描PDF文件
            if self._should_stop:
                return

            self.error_occurred.emit("正在扫描PDF文件...")
            pdf_files = self.scanner.scan()
            result.total_files = len(pdf_files)

            if result.total_files == 0:
                self.error_occurred.emit("未找到PDF文件")
                self.processing_completed.emit(result)
                return

            # 2. 处理PDF文件
            writer = TextFileWriter(self.config.output_dir, self.config.overwrite)

            if self.config.use_multithreading:
                # 多线程处理
                self._process_with_multithreading(pdf_files, writer, result)
            else:
                # 单线程处理
                self._process_single_thread(pdf_files, writer, result)

            # 3. 写入错误日志
            if self.error_handler.get_error_count() > 0:
                self.error_handler.write_log_file(self.config.output_dir)

            # 4. 发送性能统计
            performance_summary = self.method_dispatcher.get_performance_summary()
            if performance_summary:
                self.performance_stats_updated.emit(performance_summary)

            # 5. 发送完成信号
            result.end_time = datetime.now()
            self.processing_completed.emit(result)

        except PDFExtractorError as e:
            self.error_occurred.emit(f"处理错误: {str(e)}")
            result.add_error(str(e))
            result.failed_count = result.total_files - result.success_count
            result.end_time = datetime.now()
            self.processing_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"未知错误: {str(e)}")
            result.add_error(str(e))
            result.end_time = datetime.now()
            self.processing_completed.emit(result)
        finally:
            self._is_running = False
            self.tasks.clear()

    def _process_single_thread(self, pdf_files, writer: TextFileWriter, result: ProcessingResult):
        """
        单线程处理PDF文件

        Args:
            pdf_files: PDF文件列表
            writer: 文件写入器
            result: 处理结果对象
        """
        for idx, pdf_info in enumerate(pdf_files, 1):
            if self._should_stop:
                self.error_occurred.emit("任务已取消")
                break

            # 发送进度更新
            self.progress_updated.emit(idx, result.total_files, str(pdf_info.file_path))

            # 处理文件
            task_result = self._process_single_file(pdf_info, writer, result)

            if task_result["success"]:
                result.success_count += 1
            elif task_result["skipped"]:
                result.skipped_count += 1
            else:
                result.failed_count += 1

    def _process_with_multithreading(self, pdf_files, writer: TextFileWriter, result: ProcessingResult):
        """
        多线程处理PDF文件

        Args:
            pdf_files: PDF文件列表
            writer: 文件写入器
            result: 处理结果对象
        """
        # 确定线程数
        max_threads = min(self.config.max_threads, len(pdf_files))
        self.error_occurred.emit(f"使用 {max_threads} 个线程进行并行处理...")

        # 使用线程池
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # 提交所有任务
            future_to_pdf = {}
            for idx, pdf_info in enumerate(pdf_files, 1):
                if self._should_stop:
                    break

                # 创建任务
                task = PDFProcessingTask(
                    pdf_info,
                    self.extractor,
                    self.encoding_converter,
                    writer,
                    self.config,
                    self.worker_signals
                )
                self.tasks.append(task)

                # 提交到线程池
                future = executor.submit(task.run)
                future_to_pdf[future] = (idx, pdf_info)

            # 等待任务完成
            completed_count = 0
            for future in as_completed(future_to_pdf):
                if self._should_stop:
                    break

                idx, pdf_info = future_to_pdf[future]
                completed_count += 1

                # 发送进度更新
                self.progress_updated.emit(completed_count, result.total_files, str(pdf_info.file_path))

                try:
                    # 获取任务结果
                    task = self.tasks[idx - 1] if idx - 1 < len(self.tasks) else None
                    if task:
                        if task.result["success"]:
                            result.success_count += 1
                        elif task.result["skipped"]:
                            result.skipped_count += 1
                        else:
                            result.failed_count += 1
                            if task.result["error"]:
                                self.error_handler.log_error(
                                    str(pdf_info.file_path),
                                    "ProcessingError",
                                    task.result["error"]
                                )
                except Exception as e:
                    result.failed_count += 1
                    self.error_handler.log_error(
                        str(pdf_info.file_path),
                        "ThreadError",
                        str(e)
                    )

    def _process_single_file(self, pdf_info, writer: TextFileWriter, result: ProcessingResult) -> dict:
        """
        处理单个PDF文件(单线程版本)

        Args:
            pdf_info: PDF文件信息
            writer: 文件写入器
            result: 处理结果对象

        Returns:
            处理结果字典
        """
        file_path = pdf_info.file_path

        try:
            # 检查文件是否有效
            if not pdf_info.is_valid:
                error_msg = f"文件无效: {pdf_info.error_message}"
                self.error_handler.log_error(str(file_path), "FileInvalid", error_msg)
                self.file_processed.emit(str(file_path), error_msg, False)
                return {"success": False, "skipped": False, "error": error_msg}

            # 检查文件是否已处理(跳过已处理的文件)
            if self.config.skip_existing and not self.config.overwrite:
                if writer.exists(pdf_info.relative_path):
                    msg = "文件已存在,跳过"
                    self.file_processed.emit(str(file_path), msg, True)
                    return {"success": False, "skipped": True, "error": None}

            # 提取文本
            extracted_text = self.extractor.extract(file_path)

            # 检查是否包含文本
            if not extracted_text.has_text:
                msg = "PDF文件不包含可提取的文本"
                self.error_handler.log_error(str(file_path), "NoText", msg)
                self.file_processed.emit(str(file_path), msg, False)
                return {"success": False, "skipped": False, "error": msg}

            # 转换编码
            if extracted_text.encoding != "utf-8":
                try:
                    text_bytes = extracted_text.text.encode(extracted_text.encoding)
                    extracted_text.text = self.encoding_converter.convert_to_utf8(
                        text_bytes, extracted_text.encoding
                    )
                except Exception as e:
                    # 编码转换失败,使用原始文本
                    pass

            # 写入文件
            output_path = writer.write(pdf_info.relative_path, extracted_text)
            msg = f"提取成功 -> {output_path}"
            self.file_processed.emit(str(file_path), msg, True)

            return {"success": True, "skipped": False, "error": None}

        except PDFExtractorError as e:
            error_msg = str(e)
            self.error_handler.log_error(str(file_path), type(e).__name__, error_msg)
            self.file_processed.emit(str(file_path), error_msg, False)
            return {"success": False, "skipped": False, "error": error_msg}
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self.error_handler.log_error(str(file_path), "ProcessingError", error_msg)
            self.file_processed.emit(str(file_path), error_msg, False)
            return {"success": False, "skipped": False, "error": error_msg}

    def is_running(self) -> bool:
        """检查任务是否正在运行"""
        return self._is_running
