"""轻量设置持久化

设置文件放在**程序目录**（源码运行时=项目根目录；打包后=exe 所在目录）的
``settings.json``，与 Cathay 工具链其它软件的做法一致：

- 读不到 / 写不了都不致命（返回默认值 / 静默忽略）
- 只存少量界面偏好，例如输出 TXT 的命名方式
"""
import json
import os
import sys
from pathlib import Path


def app_dir() -> Path:
    """程序目录：打包后 = exe 所在目录；源码运行 = 项目根目录"""
    if getattr(sys, "frozen", False):
        return Path(os.path.dirname(os.path.abspath(sys.executable)))
    # __file__ = <root>/src/core/appsettings.py
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def settings_path() -> Path:
    return app_dir() / "settings.json"


#: 默认设置
DEFAULTS = {
    "out_name_mode": "auto",  # auto=按源文件名后缀自动判定 / result=统一 书名_result.txt / same=同名
}


def load_settings() -> dict:
    """读设置（失败返回默认值）"""
    d = dict(DEFAULTS)
    try:
        with open(settings_path(), encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            d.update(data)
    except Exception:
        pass
    return d


def save_settings(patch: dict) -> None:
    """合并写入设置（失败静默忽略）"""
    if not patch:
        return
    d = load_settings()
    d.update(patch)
    try:
        settings_path().write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass
