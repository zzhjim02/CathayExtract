"""CathayExtract · PDF OCR 文本提取器 - 主程序入口"""
import os
import sys

APP_TITLE = 'CathayExtract · PDF OCR 文本提取器'
APP_VERSION = 'v1.2.3'


def app_dir():
    """程序所在目录（打包成 exe 时为 exe 目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def icon_path():
    """找同目录下的 app.ico（免安装便携版 / 打包版都能找到）"""
    here = app_dir()
    cands = []
    if getattr(sys, '_MEIPASS', None):
        cands.append(os.path.join(sys._MEIPASS, 'app.ico'))
    cands += [os.path.join(here, 'app.ico'), os.path.join(here, 'src', 'app.ico')]
    for p in cands:
        if os.path.exists(p):
            return p
    return None


def selftest():
    """环境自检：依赖、图标、主窗口能否建起来"""
    out = ['%s %s' % (APP_TITLE, APP_VERSION),
           'frozen=%s' % getattr(sys, 'frozen', False),
           'app_dir=%s' % app_dir(),
           'icon=%s' % (icon_path() or '缺失')]
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
        out.append('PyQt6=%s (Qt %s)' % (PYQT_VERSION_STR, QT_VERSION_STR))
    except Exception as e:
        out.append('PyQt6=缺失(%s)' % e)
    for m in ('fitz', 'pdfplumber', 'PyPDF2', 'chardet', 'PIL'):
        try:
            mod = __import__(m)
            out.append('%s=%s' % (m, getattr(mod, '__version__', '?')))
        except Exception as e:
            out.append('%s=缺失(%s)' % (m, e))
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui import MainWindow
        app = QApplication.instance() or QApplication(sys.argv)
        w = MainWindow()
        w.show()
        app.processEvents()
        out.append('主窗口=OK 标题=%s' % w.windowTitle())
        w.close()

        # 新增能力自检：输出命名规则（与 Cathay 工具链后缀约定一致）
        try:
            from src.core.output_naming import txt_name_for_pdf
            cases = [
                ('甲书_layered.pdf', '甲书_result.txt'),
                ('甲书_layered_【繁转简】.pdf', '甲书_result_【繁转简】.txt'),
                ('甲书_PD6AIFOCR_opt.pdf', '甲书_PD6AIFOCR.txt'),
                ('甲书_PD6AIFOCR.pdf', '甲书_PD6AIFOCR.txt'),
                ('甲书_PD6AIOCR.pdf', '甲书_PD6AIOCR.txt'),
                ('甲书_FOCR.pdf', '甲书_FOCR.txt'),
                ('甲书_OCR.pdf', '甲书_OCR.txt'),
                ('甲书_PD5AIOCR.pdf', '甲书_PD5AIOCR.txt'),
                ('甲书_PD5AIFOCR.pdf', '甲书_PD5AIFOCR.txt'),
                ('甲书_PD7AIFOCR.pdf', '甲书_PD7AIFOCR.txt'),
                ('甲书_PDVL6AIOCR.pdf', '甲书_PDVL6AIOCR.txt'),
                ('甲书_PDVL6AIFOCR.pdf', '甲书_PDVL6AIFOCR.txt'),
                ('甲书_result.pdf', '甲书_result.txt'),
                ('甲书_10117362_PD6AIOCR.pdf', '甲书_10117362_PD6AIOCR.txt'),
                ('甲书_全1册_PD6AIFOCR.pdf', '甲书_全1册_PD6AIFOCR.txt'),
                ('甲书_扫描版_unlocked_PD6AIOCR.pdf', '甲书_扫描版_unlocked_PD6AIOCR.txt'),
                ('甲书_PD6AIFOCR_【繁转简】.pdf', '甲书_PD6AIFOCR_【繁转简】.txt'),
                ('甲书.pdf', '甲书_result.txt'),
            ]
            bad = [(a, b, txt_name_for_pdf(a)) for a, b in cases if txt_name_for_pdf(a) != b]
            out.append('命名规则=%s（%d/%d）' % ('OK' if not bad else 'FAIL %r' % bad,
                                              len(cases) - len(bad), len(cases)))
        except Exception as e:
            out.append('命名规则=FAIL %s: %s' % (type(e).__name__, e))

        # 新增能力自检：原地输出（输出到原目录）+ CathayOCR 格式
        try:
            import tempfile
            import fitz
            from pathlib import Path
            from src.core.config import ExtractorConfig
            from src.coordinator.task_coordinator import TaskCoordinator

            d = Path(tempfile.mkdtemp(prefix='cathayextract_selftest_'))
            pdf = d / '自检样张.pdf'
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 100), '自检文字', fontsize=14, fontname='china-s')
            doc.save(str(pdf))
            doc.close()

            cfg = ExtractorConfig(source_dir=d, output_dir=None, overwrite=True,
                                  skip_existing=True, use_multithreading=False,
                                  file_list=[pdf])
            TaskCoordinator(cfg).run()
            txt = d / '自检样张_result.txt'
            content = txt.read_text(encoding='utf-8') if txt.exists() else ''
            out.append('原地输出=%s (文件名=%s)' % (txt.exists(), txt.name))
            out.append('输出格式=(头=%s 分页=%s)' % (
                content.startswith('OCR文本提取结果'), '第 1 页' in content))
        except Exception as e:
            out.append('输出自检=FAIL %s: %s' % (type(e).__name__, e))

        out.append('result=OK')
    except Exception as e:
        out.append('主窗口=FAIL %s: %s' % (type(e).__name__, e))
        out.append('result=FAIL')
    txt = '\n'.join(out)
    try:
        with open(os.path.join(app_dir(), '_selftest.txt'), 'w', encoding='utf-8') as f:
            f.write(txt + '\n')
    except Exception:
        pass
    return txt


def main():
    """主函数"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon

    from src.gui import MainWindow

    # 创建应用程序实例（PyQt6 默认已启用高DPI支持）
    app = QApplication(sys.argv)

    # 图标（窗口 + 任务栏）
    ico = icon_path()
    if ico:
        app.setWindowIcon(QIcon(ico))

    # 创建并显示主窗口
    window = MainWindow()
    if ico:
        window.setWindowIcon(QIcon(ico))
    window.show()

    # 启动事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print(selftest())
        sys.exit(0)
    try:
        main()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)
