"""CathayExtract · PDF OCR 文本提取器 - 主程序入口"""
import os
import sys

APP_TITLE = 'CathayExtract · PDF OCR 文本提取器'
APP_VERSION = 'v1.2.0'


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
