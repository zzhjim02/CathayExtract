"""输出 TXT 命名规则（按源 PDF 文件名的后缀自动判定）

**核心规则：只动末尾那一小段后缀，文件名前面的一切原样保留。**

``_全1册``、8 位编号、``_unlocked``、``扫描版`` 这些**不是后缀**，它们是文件名的一部分，
在 TXT 名里**原样保留**；会被处理的只有末尾的后缀：

============  ==========================================================
源 PDF 名                                      导出的 TXT
============  ==========================================================
``X_layered.pdf``                              ``X_result.txt``（固定配对）
``X_PD6AIFOCR.pdf``                            ``X_PD6AIFOCR.txt``（同名同后缀）
``X_PD6AIFOCR_opt.pdf``                        ``X_PD6AIFOCR.txt``（``_opt`` 只在 PDF 上，TXT 里不要）
``X_全1册_PD6AIFOCR.pdf``                       ``X_全1册_PD6AIFOCR.txt``（``_全1册`` 保留）
``X_10117362_PD6AIOCR.pdf``                    ``X_10117362_PD6AIOCR.txt``（编号保留）
``X_扫描版_unlocked_PD6AIOCR.pdf``              ``X_扫描版_unlocked_PD6AIOCR.txt``
``X_PD6AIFOCR_【繁转简】.pdf``                   ``X_PD6AIFOCR_【繁转简】.txt``（繁简尾巴原样保留）
``X.pdf``（无标准后缀）                          ``X_result.txt``
============  ==========================================================

标准后缀 = ``_layered`` / ``_result`` /
``_<版本>AI[F]OCR``（``_PD6AIFOCR`` / ``_PD6AIOCR`` / ``_PD5AIOCR`` / ``_PD5AIFOCR`` /
``_PD7AIOCR`` / ``_PD7AIFOCR`` / ``_PDVL6AIOCR`` / ``_PDVL6AIFOCR`` / ``_AIFOCR`` /
``_AIOCR`` / ``_FOCR`` / ``_OCR``，版本段可省略）。
"""
import re

#: 命名方式
MODE_AUTO = "auto"      # 按源文件名自动判定（默认，推荐）
MODE_RESULT = "result"  # 统一 <原名>_result.txt
MODE_SAME = "same"      # 与源文件完全同名（只换扩展名）
NAME_MODES = (MODE_AUTO, MODE_RESULT, MODE_SAME)

#: 繁简尾巴（_【繁转简】/【繁转简】/_【简转繁】/【简转繁】/繁转繁）
T2S_TAIL_RE = re.compile(r'_?【\s*(?:繁转简|简转繁|繁转繁)\s*】$')

#: ``_opt`` 尾巴（只在 PDF 上有用，生成 TXT 名时丢掉）
OPT_TAIL_RE = re.compile(r'[ _]?_opt$', re.IGNORECASE)

#: 标准后缀：_<版本>AI[F]OCR / _layered / _result（大小写不敏感）
STD_TAIL_RE = re.compile(
    r'(?P<suf>_(?:pd(?:vl)?\d*)?(?:ai)?f?ocr|_layered|_result)$', re.IGNORECASE)

#: 后缀剥掉后可能残留的首尾分隔符（只收尾；开头的符号原样保留）
EDGE_SEPS = ' _-—+.、，。'


def strip_pdf_ext(name: str) -> str:
    """去掉 .pdf 扩展名"""
    return name[:-4] if name.lower().endswith('.pdf') else name


def tidy_base(core: str) -> str:
    """后缀剥掉后收一下尾部残留的分隔符；其余一律原样保留"""
    return (core or '').rstrip(EDGE_SEPS)


def split_suffix(stem: str):
    """拆分源文件名 → (base, suffix, tail)

    Args:
        stem: 源 PDF 文件名（不含扩展名）

    Returns:
        base:   去掉标准后缀与繁简尾巴后的名字（**原样，未做任何清洗**）
        suffix: 末尾标准后缀（已丢掉 ``_opt``），没有则为 ''
        tail:   繁简尾巴（原样），没有则为 ''
    """
    stem = stem or ''
    tail = ''
    m = T2S_TAIL_RE.search(stem)
    if m:
        tail = m.group(0)
        stem = stem[:m.start()]
    core = stem
    while True:                      # _opt 直接丢掉（只在 PDF 上需要）
        m = OPT_TAIL_RE.search(core)
        if not m:
            break
        core = core[:m.start()]
    suffix = ''
    m = STD_TAIL_RE.search(core)
    if m:
        suffix = m.group('suf')
        core = core[:m.start()]
    return core, suffix, tail


def txt_name_for_pdf(pdf_name: str, mode: str = MODE_AUTO) -> str:
    """按规则给出该 PDF 的 TXT 输出文件名

    规则：**只替换/补末尾的后缀，文件名前面的一切原样保留**。

    Args:
        pdf_name: 源 PDF 文件名（含或不含 .pdf 都可）
        mode: auto（默认）/ result / same

    Returns:
        输出文件名，如 ``甲书_PD6AIFOCR.txt``
    """
    stem = strip_pdf_ext(pdf_name)
    if mode == MODE_SAME:
        return stem + '.txt'                     # 字面同名，只换扩展名

    core, suffix, tail = split_suffix(stem)
    base = tidy_base(core) or tidy_base(stem) or 'untitled'

    if mode == MODE_RESULT:
        suf = '_result'
    elif suffix:
        # _layered.pdf ↔ _result.txt 是固定配对；其余标准后缀原样保留
        suf = '_result' if suffix.lower() == '_layered' else suffix
    else:
        suf = '_result'                          # 没有标准后缀 → 补 _result

    return base + suf + tail + '.txt'
