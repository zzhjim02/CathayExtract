"""CathayOCR 格式输出 / 原地输出 / 拖入清单 的单元测试"""
import shutil
import tempfile
from pathlib import Path

import pytest

from src.core.config import ExtractedText, ExtractorConfig
from src.core.output_naming import txt_name_for_pdf
from src.scanner import DirectoryScanner
from src.writer import TextFileWriter
from src.writer.text_file_writer import format_result_txt

SEP = "=" * 60


class TestResultFormat:
    """输出格式与 CathayOCR Pro 一致"""

    def test_header_lines(self):
        et = ExtractedText(text="x", page_count=2, has_text=True,
                           page_texts=["第一页", "第二页"])
        txt = format_result_txt("甲书", et)
        lines = txt.splitlines()
        assert lines[0] == "OCR文本提取结果"
        assert lines[1] == SEP
        assert lines[2] == "源文件: 甲书"
        assert lines[3] == "总页数: 2"
        assert lines[4] == "渲染倍数: -"
        assert lines[5].startswith("提取时间: ")
        assert lines[6] == SEP

    def test_page_blocks(self):
        et = ExtractedText(text="x", page_count=2, has_text=True,
                           page_texts=["第一页", "第二页"])
        txt = format_result_txt("甲书", et)
        assert ("\n" + SEP + "\n第 1 页\n" + SEP + "\n\n第一页\n") in txt
        assert ("\n" + SEP + "\n第 2 页\n" + SEP + "\n\n第二页\n") in txt

    def test_empty_pages_skipped(self):
        et = ExtractedText(text="x", page_count=3, has_text=True,
                           page_texts=["", "有字", ""])
        txt = format_result_txt("甲书", et)
        assert "第 2 页" in txt and "第 1 页" not in txt and "第 3 页" not in txt


class TestWriterFormat:
    """写入器：有分页信息时用 CathayOCR 格式，没有时原样写"""

    @pytest.fixture
    def temp_dir(self):
        p = Path(tempfile.mkdtemp())
        yield p
        shutil.rmtree(p)

    def test_write_page_texts_uses_cathay_format(self, temp_dir):
        writer = TextFileWriter(temp_dir, overwrite=True)
        et = ExtractedText(text="fallback", page_count=1, has_text=True, page_texts=["正文"])
        out = writer.write(Path("书.pdf"), et)
        txt = out.read_text(encoding="utf-8")
        assert out.name == "书_result.txt"
        assert txt.startswith("OCR文本提取结果\n")
        assert "源文件: 书" in txt and "第 1 页" in txt and "正文" in txt

    def test_write_without_page_texts_is_raw(self, temp_dir):
        writer = TextFileWriter(temp_dir, overwrite=True)
        et = ExtractedText(text="纯文本", page_count=1, has_text=True)
        out = writer.write(Path("书.pdf"), et)
        assert out.read_text(encoding="utf-8") == "纯文本"


class TestOutputNaming:
    """输出 TXT 命名规则（与 Cathay 工具链后缀约定一致）"""

    @pytest.mark.parametrize("pdf_name,expected", [
        # 固定配对：_layered.pdf ↔ _result.txt
        ("甲书_layered.pdf", "甲书_result.txt"),
        ("甲书_Layered.pdf", "甲书_result.txt"),
        # _opt 丢掉
        ("甲书_PD6AIFOCR_opt.pdf", "甲书_PD6AIFOCR.txt"),
        ("甲书_FOCR_opt.pdf", "甲书_FOCR.txt"),
        # 同名同后缀
        ("甲书_PD6AIFOCR.pdf", "甲书_PD6AIFOCR.txt"),
        ("甲书_PD6AIOCR.pdf", "甲书_PD6AIOCR.txt"),
        ("甲书_PD5AIFOCR.pdf", "甲书_PD5AIFOCR.txt"),
        ("甲书_PD7AIOCR.pdf", "甲书_PD7AIOCR.txt"),
        ("甲书_PDVL6AIFOCR.pdf", "甲书_PDVL6AIFOCR.txt"),
        ("甲书_AIFOCR.pdf", "甲书_AIFOCR.txt"),
        ("甲书_AIOCR.pdf", "甲书_AIOCR.txt"),
        ("甲书_FOCR.pdf", "甲书_FOCR.txt"),
        ("甲书_OCR.pdf", "甲书_OCR.txt"),
        ("甲书_result.pdf", "甲书_result.txt"),
        # 繁简尾巴原样保留
        ("甲书_PD6AIFOCR_【繁转简】.pdf", "甲书_PD6AIFOCR_【繁转简】.txt"),
        ("甲书_layered_【繁转简】.pdf", "甲书_result_【繁转简】.txt"),
        ("甲书_PD6AIFOCR【简转繁】.pdf", "甲书_PD6AIFOCR【简转繁】.txt"),
        # 8 位编号 / _全1册 / _unlocked / 扫描版 等不是后缀（是文件名的一部分）→ 原样保留
        ("甲书_10117362_PD6AIOCR.pdf", "甲书_10117362_PD6AIOCR.txt"),
        ("甲书_全1册_PD6AIFOCR.pdf", "甲书_全1册_PD6AIFOCR.txt"),
        ("甲书_unlocked_PD6AIOCR.pdf", "甲书_unlocked_PD6AIOCR.txt"),
        ("甲书 12564425 F_ORPALIS优化_PD6AIOCR.pdf", "甲书 12564425 F_ORPALIS优化_PD6AIOCR.txt"),
        ("26 古文献学四讲.黄永年.清晰扫描版_PD6AIOCR.pdf",
         "26 古文献学四讲.黄永年.清晰扫描版_PD6AIOCR.txt"),
        ("中华大典 农业典 茶业分典 上_全1册_PD6AIFOCR.pdf",
         "中华大典 农业典 茶业分典 上_全1册_PD6AIFOCR.txt"),
        # 无标准后缀 → _result
        ("甲书.pdf", "甲书_result.txt"),
        ("中华大典 民俗典 风俗民俗分典 2.pdf", "中华大典 民俗典 风俗民俗分典 2_result.txt"),
        # 原名开头的分隔符保留（不要吃掉文件名的第一个字符）
        ("_神秘湘西_旅游品牌核心价值的构建理念_PD6AIOCR.pdf",
         "_神秘湘西_旅游品牌核心价值的构建理念_PD6AIOCR.txt"),
    ])
    def test_auto_mode(self, pdf_name, expected):
        assert txt_name_for_pdf(pdf_name) == expected

    def test_forced_modes(self):
        assert txt_name_for_pdf("甲书_PD6AIFOCR.pdf", "result") == "甲书_result.txt"
        assert txt_name_for_pdf("甲书_layered.pdf", "result") == "甲书_result.txt"
        assert txt_name_for_pdf("甲书_PD6AIFOCR.pdf", "same") == "甲书_PD6AIFOCR.txt"
        assert txt_name_for_pdf("甲书.pdf", "same") == "甲书.txt"

    @pytest.fixture
    def temp_dir(self):
        p = Path(tempfile.mkdtemp())
        yield p
        shutil.rmtree(p)

    def test_writer_uses_name_mode(self, temp_dir):
        et = ExtractedText(text="x", page_count=1, has_text=True, page_texts=["正"])
        w_auto = TextFileWriter(temp_dir / "a", overwrite=True, name_mode="auto")
        w_res = TextFileWriter(temp_dir / "b", overwrite=True, name_mode="result")
        w_same = TextFileWriter(temp_dir / "c", overwrite=True, name_mode="same")
        assert w_auto.write(Path("甲书_PD6AIFOCR.pdf"), et).name == "甲书_PD6AIFOCR.txt"
        assert w_res.write(Path("甲书_PD6AIFOCR.pdf"), et).name == "甲书_result.txt"
        assert w_same.write(Path("甲书_PD6AIFOCR.pdf"), et).name == "甲书_PD6AIFOCR.txt"


class TestScannerPaths:
    """拖入的「文件 + 文件夹」混合清单扫描"""

    @pytest.fixture
    def temp_dir(self):
        p = Path(tempfile.mkdtemp())
        (p / "甲.pdf").write_bytes(b"x")
        (p / "子").mkdir()
        (p / "子" / "乙.pdf").write_bytes(b"y")
        (p / "说明.txt").write_text("no", encoding="utf-8")
        yield p
        shutil.rmtree(p)

    def test_scan_paths_mixed(self, temp_dir):
        cfg = ExtractorConfig(source_dir=temp_dir, output_dir=None,
                              file_list=[temp_dir / "甲.pdf", temp_dir / "子",
                                         temp_dir / "说明.txt"])
        scanner = DirectoryScanner(cfg)
        files = scanner.scan()
        names = set(f.file_path.name for f in files)
        assert names == {"甲.pdf", "乙.pdf"}  # txt 被忽略，子目录里的 PDF 被展开

    def test_in_place_flag(self, temp_dir):
        assert ExtractorConfig(source_dir=temp_dir, output_dir=None).in_place is True
        assert ExtractorConfig(source_dir=temp_dir, output_dir="").in_place is True
        assert ExtractorConfig(source_dir=temp_dir, output_dir=temp_dir).in_place is False
