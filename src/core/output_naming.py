"""输出 TXT 命名规则（按源 PDF 文件名的后缀自动判定）

与 Cathay 工具链既有约定完全一致（取自 CathayOCR / CathayShelf / CathayRestore 的代码）：

============  ==========================================================
源 PDF 名                                    导出的 TXT
============  ==========================================================
``X_layered.pdf``                            ``X_result.txt``
``X_PD6AIFOCR_opt.pdf``                      ``X_PD6AIFOCR.txt``（``_opt`` 丢掉）
``X_PD6AIFOCR.pdf``                          ``X_PD6AIFOCR.txt``（同名同后缀）
``X_FOCR.pdf`` / ``X_OCR.pdf`` / ``X_AIOCR.pdf`` / ``X_PD5AIFOCR.pdf`` / ``X_PDVL6AIFOCR.pdf``  同名同后缀
``X_result.pdf``                             ``X_result.txt``
``X_全1册_PD6AIFOCR.pdf``                     ``X_PD6AIFOCR.txt``（``_全1册`` 等属「其他数据」不保留）
``X_10117362_PD6AIOCR.pdf``                  ``X_PD6AIOCR.txt``（8 位编号不保留）
``X_layered_【繁转简】.pdf``                  ``X_result_【繁转简】.txt``（繁简尾巴原样保留）
``X.pdf``（无标准后缀）                       ``X_result.txt``
============  ==========================================================

标准后缀 = ``_layered`` / ``_result`` / ``_opt`` /
``_<版本>AI[F]OCR``（``_PD6AIFOCR``、``_PD6AIOCR``、``_PD5AIFOCR``、``_PDVL6AIFOCR``、
``_AIFOCR``、``_AIOCR``、``_FOCR``、``_OCR`` 等，版本段可省略）。

「其他数据」（生成 TXT 名时一律丢掉）：8 位以上数字编号、``_全1册`` 一类册次、
``_unlocked``、孤立单字母，以及老流水线噪声 ``OCR优化`` / ``OPT`` / ``ORPALIS优化`` /
``ORP优化`` / ``zhelper-search`` / ``清晰扫描版`` / ``扫描版`` / ``纯文本`` / ``可搜索版``。
"""
import re

#: 命名方式
MODE_AUTO = "auto"      # 按源文件名自动判定（默认，推荐）
MODE_RESULT = "result"  # 统一 <书名>_result.txt
MODE_SAME = "same"      # 与源文件完全同名（只换扩展名）
NAME_MODES = (MODE_AUTO, MODE_RESULT, MODE_SAME)

#: 繁简尾巴（_【繁转简】/【繁转简】/_【简转繁】/【简转繁】/繁转繁）
T2S_TAIL_RE = re.compile(r'_?【\s*(?:繁转简|简转繁|繁转繁)\s*】$')

#: ``_opt`` 尾巴（配对时要丢掉）
OPT_TAIL_RE = re.compile(r'_opt$', re.IGNORECASE)

#: 标准后缀：_<版本>AI[F]OCR / _layered / _result（大小写不敏感）
STD_TAIL_RE = re.compile(
    r'(?P<suf>_(?:pd(?:vl)?\d*)?(?:ai)?f?ocr|_layered|_result)$', re.IGNORECASE)

#: 「其他数据」噪声（token 形式，两侧需是分隔符/边界）
JUNK_TOKEN_RE = re.compile(
    r'(?i)[\s_\-—+.（(【\[]*('
    r'\d{6,}'                                   # 6 位以上数字编号
    r'|unlocked'
    r'|全\s*\d+\s*[册集卷部编]'                    # 全1册 / 全2卷 …
    r'|ocr\s*优化版?|opt|orpalis\s*优化版?|orpalis|orp\s*优化版?|orp'
    r'|zhelper[-\s]?search|zhelper|清晰扫描版|扫描版|纯文本|可搜索版'
    r')(?=[\s_\-—+.（(）)【\[]|$|\.)')

#: 孤立单大写字母（如「全篇 F_ORPALIS优化」里的 F；左右必须紧邻里是空格/下划线，避免误伤 [英]G· 这类缩写）
LONE_UPPER_RE = re.compile(r'(?<=[\s_])[A-Z](?=[\s_]|$)')

#: 连续的分隔（只合并「空格/下划线」，不碰书名里的破折号/间隔号）
SEPS_RE = re.compile(r'[ _]{2,}')
#: 被清理噪声后残留的首尾分隔符（含点号、顿号）
EDGE_SEPS = ' _-—+.、，。'


def strip_pdf_ext(name: str) -> str:
    """去掉 .pdf 扩展名"""
    return name[:-4] if name.lower().endswith('.pdf') else name


def clean_junk(stem: str) -> str:
    """去掉文件名里的「其他数据」噪声（保留原名开头的符号，只收尾）"""
    s = stem or ''
    m = re.match(r'[\s_\-—+.]+', s)          # 开头的符号原样保留（不压缩、不删除）
    lead = m.group(0) if m else ''
    rest = s[len(lead):]
    prev = None
    while rest != prev:
        prev = rest
        rest = JUNK_TOKEN_RE.sub('', rest)
        rest = LONE_UPPER_RE.sub('', rest)
        rest = SEPS_RE.sub(' ', rest).rstrip(EDGE_SEPS)
    if not lead:
        rest = rest.lstrip(EDGE_SEPS)
    return lead + rest


def split_suffix(stem: str):
    """拆分源文件名 → (base, suffix, tail)

    Args:
        stem: 源 PDF 文件名（不含扩展名）

    Returns:
        base:   去掉标准后缀与繁简尾巴后的名字（未清噪声）
        suffix: 标准后缀（已丢弃 ``_opt``），没有则为 ''
        tail:   繁简尾巴（原样），没有则为 ''
    """
    stem = stem or ''
    tail = ''
    m = T2S_TAIL_RE.search(stem)
    if m:
        tail = m.group(0)
        stem = stem[:m.start()]
    core = stem
    while True:                      # _opt 直接丢掉
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
    base = clean_junk(core) or clean_junk(stem) or 'untitled'

    if mode == MODE_RESULT:
        suf = '_result'
    elif suffix:
        # _layered.pdf ↔ _result.txt 是固定配对；其余后缀原样保留
        suf = '_result' if suffix.lower() == '_layered' else suffix
    else:
        suf = '_result'                          # 没有标准后缀 → 补 _result

    return base + suf + tail + '.txt'
