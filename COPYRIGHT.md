# CathayExtract · PDF OCR 文本提取器 — 版权信息

**软件名称**: CathayExtract · PDF OCR 文本提取器
**版本**: v1.2.0
**作者**: 浮生＆2cm（湖北大学历史文化学院）
**联系方式**: zzhjim@qq.com
**技术支持**: 华为云 CodeArts Agent

Copyright (c) 2026 浮生＆2cm

---

## 许可协议

本软件采用 **GNU General Public License v3.0（GPL-3.0）** 开源许可协议，全文见同目录 `LICENSE`。

您可以自由使用、研究、修改和分发本软件；分发本软件或其衍生作品时，须同样以 GPL-3.0 授权并提供完整源码。

> 📌 沿革说明：本软件原名为「PDF OCR 文本提取大师」（v1.0–v1.2.0 期间发布），自并入 **Cathay 人文研究工具链**后更名为
> **CathayExtract**，许可协议同步由 MIT 调整为 GPL-3.0（与工具链其他成员一致）。

---

## Cathay 人文研究工具链

本工具是工具链中「**已有双层 PDF → TXT**」的入口：PDF 里的 OCR 文字层已经存在（自家跑过 OCR，或来自他人整理的双层 PDF），
直接用它把文本提取成 TXT，不必重跑 OCR。

| 步骤 | 工具 | 功能 |
|:----:|:----|:----|
| ① | CathayOCR | 多引擎 GPU 加速古籍 PDF 批处理 OCR |
| ② | CathayRestore | 把 OCR 的 TXT 按页写回 PDF（竖排 / 透明 / 可搜索） |
| ③ | CathaySimplify | TXT 繁简体批量双向转换 · 编码智能适配 |
| ④ | CathayShelf | 图书著录建夹 · 产物后缀替换 · 繁简转换+编码规范化 |
| ⑤ | CathayReader | PDF/TXT 双栏同步古籍校勘阅读器 |

---

## 文件说明

| 文件 | 说明 |
|:-----|:-----|
| `main.py` | 程序入口（图形界面） |
| `src/` | 源码：`gui` 界面、`extractor` 提取引擎、`scanner` 目录扫描、`writer` 文本写出、`coordinator` 任务调度、`core` 配置与异常 |
| `docs/` | 用户手册、多线程说明、故障排查 |
| `tests/` | 单元测试 |
| `runtime/` | 便携 Python 运行时（免安装，自带 PyQt6 / PyMuPDF / pdfplumber / PyPDF2 / chardet / Pillow） |
| `启动.bat` | 双击即用的启动脚本（优先用 `runtime\`，其次系统 Python） |
| `CathayExtract.spec` | PyInstaller 打包配置 |
| `app.ico` | 图标 |
