<div align="center">

# 🔎 CathayExtract

**PDF OCR 文本提取器 · 把双层 PDF 里的文字层抠出来**

*开箱即用 · 双击即开 · 纯本地 · 不联网 · 不改动原件*

[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2B-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![GitHub release](https://img.shields.io/github/v/release/zzhjim02/CathayExtract)]()

**已有双层 PDF（里面带 OCR 文字层）→ 一本一个 TXT，目录结构原样保留。**

不必重跑 OCR，也不必安装 Python：把文件夹拖进去，点一下「开始提取」就行。

</div>

---

## 🔗 Cathay 人文研究工具链

<div align="center">

| 步骤 | 工具 | 功能 | 状态 |
|:----:|:----|:----|:----:|
| ① | [**CathayOCR** →](https://github.com/zzhjim02/CathayOCR) | 📄 多引擎 GPU 加速古籍 PDF 批处理 OCR | ✅ v1.2.4 |
| ② | [**CathayRestore** →](https://github.com/zzhjim02/CathayRestore) | 🔎 TXT 文本层写回 PDF（竖排/透明/可搜索） | ✅ v1.0.0 |
| ③ | [**CathaySimplify** →](https://github.com/zzhjim02/CathaySimplify) | 🔄 TXT 繁简体批量双向转换 · 编码智能适配 | ✅ v1.0.0 |
| ④ | [**CathayShelf** →](https://github.com/zzhjim02/CathayShelf) | 🗂️ 图书著录建夹 · 后缀替换 · 繁简转换+编码规范化 | ✅ v0.4.3 |
| ⑤ | [**CathayReader** →](https://github.com/zzhjim02/CathayReader) | 📖 PDF/TXT 双栏同步古籍校勘阅读器 | ✅ v1.0.0 |
| ✳ | **⭐ CathayExtract（你在这里）** | 🔎 **已有双层 PDF → 提取文字层成 TXT** | 🆕 **v1.2.0** |

</div>

**本工具是第 ① 步的旁支入口：** 如果 PDF 里**已经有** OCR 文字层（自己跑过 [CathayOCR](https://github.com/zzhjim02/CathayOCR)，或拿到的是别人做好的双层 PDF），
就不必重跑 OCR——用 CathayExtract 直接把文字层提取成 TXT 即可。

> 📌 它原先叫「PDF OCR 文本提取大师」，现更名为 **CathayExtract** 并并入 Cathay 工具链（许可同步由 MIT 调整为 GPL-3.0）。

---

## ❓ 这个仓库是什么？

一个**纯图形界面**的批量工具：把 PDF 里的 OCR 文字层（不是图像层的识别，而是已经嵌在 PDF 里的那层文字）**提取成 TXT 文件**。
典型的用途：手里一堆双层 PDF（扫描图 + 隐藏文字层），想要可编辑、可检索的纯文本。

## ✨ 功能特性

- **递归扫描**：自动扫描所选文件夹及其所有子文件夹
- **保持目录结构**：TXT 的输出路径与来源 PDF 一一对应，文件名不变（只换扩展名）
- **文件名过滤**：支持通配符（如 `*.pdf`、`古代*`）只处理想处理的文件
- **多线程并行**：可设线程数（默认 4），大幅提速
- **智能跳过**：默认跳过已经提取过的文件，重复跑不会白干
- **三种提取方法**：PyMuPDF / pdfplumber / PyPDF2，可选可换
- **智能方法选择 + 自动降级**：先按 PDF 特征挑最优方法，失败自动换下一个
- **性能统计**：实时显示各方法的耗时与命中情况
- **进度与错误日志**：处理进度可见，出错可查（界面内可看错误日志）
- **图形化界面**：PyQt6 编写，标签页式（配置 / 结果 / 性能 / 日志）

## 🚀 一分钟快速上手

1. 双击 **`启动.bat`**（便携版自带运行时；也会自动回退到系统 Python）
2. **源目录**：选放 PDF 的文件夹（可拖入）
3. **输出目录**：选 TXT 存到哪（可与源目录相同）
4. （可选）填**文件名过滤**、设**线程数**、决定是否**跳过已处理**
5. 点 **开始提取**，等进度条走完，去结果标签页看统计

## ⚙️ 提取方法与自动降级

| 方法 | 适合 | 说明 |
|:----|:----|:----|
| **PyMuPDF** | 大多数双层 PDF | 最快，默认首选 |
| **pdfplumber** | 版面复杂、需要更细的文本排序 | 较慢但稳 |
| **PyPDF2** | 简单结构、老式 PDF | 兜底 |

界面里可以指定单一方法，也可以交给**智能选择**；某个方法失败时自动降级到下一个，不影响整批任务。

## 📂 输出规则（重要）

- 输出 **TXT** 用 **UTF-8** 保存；文件名与来源 PDF 同名（`书.pdf → 书.txt`）
- **只读 PDF，绝不修改原件**；已存在的 TXT 默认**跳过**（不覆盖）
- 目录结构照搬：`A/B/书.pdf` → `输出根/A/B/书.txt`

## 📦 下载

> 单文件 EXE 与便携版都**自带 Python 运行时 + 全部依赖**，解压即用，无需安装任何东西。

| 下载方式 | 链接 |
|:-------|:-----|
| 📥 **百度网盘**（密码 2026） | <待填：百度网盘分享链接> |
| 🐙 **GitHub Releases** | [CathayExtract v1.2.0](https://github.com/zzhjim02/CathayExtract/releases/tag/v1.2.0)（Assets 里直接下 `CathayExtract.exe`） |
| 🧰 **便携版（本仓库源码 + runtime）** | 解压后双击 `启动.bat`（自带 `runtime\`） |

## 🖥️ 系统要求

| 项目 | 最低 | 推荐 |
|:----|:----|:----|
| 系统 | Windows 10 64 位 | Windows 10/11 64 位 |
| 内存 | 4 GB | 8 GB 以上 |
| 磁盘 | 300 MB（便携版） | 1 GB 以上 |
| 其他 | 无需 Python、无需联网 | — |

## 🧑💻 从源码运行 / 自己打包

```bash
pip install -r requirements.txt   # PyQt6 / PyPDF2 / pdfplumber / chardet / pymupdf
python main.py                    # 运行
python main.py --selftest         # 环境自检（写 _selftest.txt）

# 打包单文件 EXE
pyinstaller --onefile --windowed --icon app.ico CathayExtract.spec
```

## 📁 文件结构

```
CathayExtract-DEV\
├── main.py                  # 入口（图形界面）
├── 启动.bat                 # 双击启动（优先自带运行时）
├── runtime\                 # 便携 Python 运行时（免安装）
├── src\
│   ├── gui\                 # 界面：主窗口、路径选择、进度、结果、性能、错误日志、关于
│   ├── extractor\           # 提取引擎：策略工厂、方法选择、三种策略、编码转换、性能统计
│   ├── scanner\             # 目录递归扫描
│   ├── writer\              # TXT 写出、目录创建
│   ├── coordinator\         # 任务调度、错误处理
│   └── core\                # 配置、异常
├── docs\                    # 用户手册 / 多线程说明 / 故障排查
├── tests\                   # 单元测试
├── app.ico                  # 图标
└── CathayExtract.spec       # PyInstaller 打包配置
```

## ❓ 常见问题

<details>
<summary>提取出来的 TXT 是空的？</summary>

说明这个 PDF **没有文字层**（纯图像扫描件）——它是给「已经有 OCR 文字层」的 PDF 用的。
纯图像件请先用 [CathayOCR](https://github.com/zzhjim02/CathayOCR) 跑 OCR。
</details>

<details>
<summary>双击 `启动.bat` 报找不到 Python？</summary>

便携版应当自带 `runtime\` 文件夹。若该文件夹缺失，可安装 Python 3 后执行 `pip install -r requirements.txt`，脚本会自动回退到系统 Python。
</details>

<details>
<summary>会不会改动我的 PDF？</summary>

不会。本工具**只读** PDF，输出只写 TXT。
</details>

<details>
<summary>可以只处理一部分文件吗？</summary>

可以，用「文件名过滤」填通配符，例如 `卷一*.pdf`。
</details>

## 📝 更新日志

- **v1.2.0**：加入提取方法选择与性能统计、自动降级；更名 **CathayExtract** 并入 Cathay 工具链，许可由 MIT 调整为 **GPL-3.0**；加入便携运行时与 `启动.bat`、图标、`--selftest` 自检
- **v1.1.0**：多线程并行、智能跳过已处理文件、UI 调整
- **v1.0.0**：首版（PyMuPDF / pdfplumber / PyPDF2 三种提取方式，递归扫描，保持目录结构）

## ⚖️ 许可

[GPL-3.0](LICENSE) © 2026 浮生＆2cm（湖北大学历史文化学院）
