<div align="center">

# 🔎 CathayExtract

**PDF OCR 文本提取器 · 把双层 PDF 里的文字层抠出来**

*开箱即用 · 双击即开 · 纯本地 · 不联网 · 不改动原件*

[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2B-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![GitHub release](https://img.shields.io/github/v/release/zzhjim02/CathayExtract)]()

**已有双层 PDF（里面带 OCR 文字层）→ 一本一个 TXT，输出格式与 CathayOCR Pro 一致。**

不必重跑 OCR，也不必安装 Python：**把文件或文件夹拖进窗口**，点一下「开始提取」就行——
TXT 默认就写在原 PDF 旁边，名字**沿用源文件的后缀**（`书_PD6AIFOCR.pdf → 书_PD6AIFOCR.txt`，
`书_layered.pdf → 书_result.txt`，没有后缀则 `书_result.txt`）——**只动末尾那一段后缀，文件名前面的一切原样保留**。

</div>

---


## 🔗 Cathay 人文社科工具链

> 🧭 主线一句话：**CathayIndex 建本地库 → CathayFinder 查书 → CathayPDG 把查到的书（读秀/超星 PDG）转成 PDF → CathayOCR 识别 → CathayShelf 著录归架 → CathayReader 双栏校勘。**

| 步骤 | 工具 | 功能 | 状态 |
|:---:|---|---|---|
| ① | [CathayIndex](https://github.com/zzhjim02/CathayIndex) | v1.0.0 | 把本地文件夹建成可检索的「本地文件库」 |
| ② | [CathayFinder](https://github.com/zzhjim02/CathayFinder) | v1.0.0 | 综合性图书检索引擎：11 个渠道精准查书（找 SSID / 找路径） |
| ③ | [CathayPDG](https://github.com/zzhjim02/CathayPDG) | v0.1.5 | 读秀/超星 **PDG 批量转 PDF**：解压解密、横竖排分柜（把查到的书变成 PDF） |
| ④ | [CathayOCR](https://github.com/zzhjim02/CathayOCR) | v1.2.4 | 扫描件 OCR，产出可搜索文字层 PDF |
| ⑤ | [CathayShelf](https://github.com/zzhjim02/CathayShelf) | v0.4.5 | 图书著录自动化整理（一 PDF 一夹、命名规范化） |
| ⑥ | [CathayReader](https://github.com/zzhjim02/CathayReader) | v1.0.0 | 双栏校勘阅读器 |

**备用软件（四个，按需取用）**

| 工具 | 什么时候用 |
|---|---|
| [CathayRepair](https://github.com/zzhjim02/CathayRepair) | ④ OCR 前：PDF 目录结构坏了先修一下 |
| [CathayRestore](https://github.com/zzhjim02/CathayRestore) | ④ 之后：把 OCR 的 TXT 写回成竖排可搜索文字层 |
| [CathayExtract](https://github.com/zzhjim02/CathayExtract) | ④ 的替代入口：已经有字层的双层 PDF，直接抽 TXT |
| [CathaySimplify](https://github.com/zzhjim02/CathaySimplify) | 繁简转换 / 编码规范化（功能已并入 ⑤ CathayShelf） |

---

## ❓ 这个仓库是什么？

一个**纯图形界面**的批量工具：把 PDF 里的 OCR 文字层（不是图像层的识别，而是已经嵌在 PDF 里的那层文字）**提取成 TXT 文件**。
典型的用途：手里一堆双层 PDF（扫描图 + 隐藏文字层），想要可编辑、可检索的纯文本。

## ✨ 功能特性

- **拖入即用**：直接把 **PDF 文件 / 整个文件夹**拖进窗口（文件夹会递归展开成待处理列表）
- **待处理列表**：所见即所得，可**单独把某个文件移出列表**（多选、清空都支持）
- **输出到原目录（默认）**：输出目录留空 = TXT 写在每个 PDF 旁边，文件名**按源文件名后缀自动判定**（见下方「输出规则」）
- **输出格式与 CathayOCR Pro 一致**：抬头（源文件 / 总页数 / 渲染倍数 / 提取时间）+ `第 N 页` 分页块
- **递归扫描**：自动扫描所选文件夹及其所有子文件夹
- **保持目录结构**：指定输出目录时，TXT 的相对路径与来源 PDF 一一对应
- **文件名过滤**：支持通配符（如 `*.pdf`、`古代*`）只处理想处理的文件
- **多线程并行**：可设线程数（默认 4），大幅提速
- **智能跳过**：默认跳过已经提取过的文件（已存在的 TXT **不覆盖就跳过**），重复跑不会白干
- **三种提取方法**：PyMuPDF / pdfplumber / PyPDF2，可选可换
- **智能方法选择 + 自动降级**：先按 PDF 特征挑最优方法，失败自动换下一个
- **性能统计**：实时显示各方法的耗时与命中情况
- **进度与错误日志**：处理进度可见，出错可查（界面内可看错误日志）
- **图形化界面**：PyQt6 编写，标签页式（配置 / 结果 / 性能 / 日志）

## 🚀 一分钟快速上手

1. 双击 **`启动.bat`**（便携版自带运行时；也会自动回退到系统 Python）
2. **把 PDF 或文件夹拖进窗口**（或用「添加文件 / 添加文件夹」按钮）——列表里就是待处理文件，
   不想要哪本就选中它点「**移除选中**」
3. **输出目录留空**即可（默认写到每个 PDF 的原目录，文件名按源文件名后缀自动判定）；
   想集中存放再选一个输出目录
4. （可选）填**文件名过滤**、设**线程数**、决定是否**覆盖已存在的文件**
5. 点 **开始提取**，等进度条走完，去结果标签页看统计

## ⚙️ 提取方法与自动降级

| 方法 | 适合 | 说明 |
|:----|:----|:----|
| **PyMuPDF** | 大多数双层 PDF | 最快，默认首选 |
| **pdfplumber** | 版面复杂、需要更细的文本排序 | 较慢但稳 |
| **PyPDF2** | 简单结构、老式 PDF | 兜底 |

界面里可以指定单一方法，也可以交给**智能选择**；某个方法失败时自动降级到下一个，不影响整批任务。

## 📂 输出规则（重要）

- 输出 **TXT** 用 **UTF-8** 保存；文件名按**源文件名的后缀**自动判定（界面里「TXT 命名」默认就是这个规则，也可强制改成统一 `_result` 或与源文件完全同名）：

| 源 PDF 名 | 导出的 TXT |
|:----|:----|
| `X_layered.pdf` | `X_result.txt`（固定配对：`_layered.pdf ↔ _result.txt`） |
| `X_PD6AIFOCR.pdf`、`X_PD6AIOCR.pdf`（版本段 `PD5` / `PD6` / `PD7` / `PDVL6` × 繁简 `AIFOCR` / `AIOCR` 的**所有组合**，如 `_PD6AIOCR`、`_PD5AIOCR`、`_PD5AIFOCR`、`_PDVL6AIOCR`、`_PDVL6AIFOCR`、`_PD7AIOCR`、`_PD7AIFOCR`；以及无版本 `_AIFOCR` / `_AIOCR` / `_FOCR` / `_OCR`） | `X_PD6AIFOCR.txt` / `X_PD6AIOCR.txt`（**同名同后缀**） |
| `X_<任意后缀>_opt.pdf`（**任何标准后缀后面都能再跟 `_opt`**：`X_PD6AIOCR_opt.pdf`、`X_PD6AIFOCR_opt.pdf`、`X_FOCR_opt.pdf`、`X_OCR_opt.pdf`、`X_PDVL6AIFOCR_opt.pdf`、`X_layered_opt.pdf` …） | `X_PD6AIOCR.txt` 等（**`_opt` 一律丢掉**；`_layered_opt.pdf → _result.txt`） |
| `X_全1册_PD6AIFOCR.pdf`、`X_10117362_PD6AIOCR.pdf`、`X_..._unlocked_PD6AIOCR.pdf` | **原样保留**（`_全1册`、8 位编号、`_unlocked`、`扫描版` 这些**不是后缀**，是文件名的一部分）：`X_全1册_PD6AIFOCR.txt` 等 |
| `X_PD6AIFOCR_【繁转简】.pdf` | `X_PD6AIFOCR_【繁转简】.txt`（**PDF 一般不带这个尾巴**，它是 TXT 侧的后缀；真带了则原样保留） |
| `X.pdf`（没有任何标准后缀） | `X_result.txt` |

  > 规则一句话：**只替换/补末尾的那一段后缀，其余一字不改**（`_opt` 是例外——它属于 PDF 侧，TXT 里丢掉）。
  > 这样导出的 TXT 与 [CathayOCR](https://github.com/zzhjim02/CathayOCR) / [CathayShelf](https://github.com/zzhjim02/CathayShelf) / [CathayRestore](https://github.com/zzhjim02/CathayRestore) 的后缀约定完全一致，**不用再转换**就能被工具链直接识别。
- **输出目录留空 = 原地输出**：TXT 直接写在每个 PDF 所在目录；指定了输出目录则目录结构照搬（`A/B/书.pdf → 输出根/A/B/书_PD6AIFOCR.txt`）
- **输出格式与 [CathayOCR Pro](https://github.com/zzhjim02/CathayOCR) 默认导出一致**：

```
OCR文本提取结果
============================================================
源文件: 书
总页数: 128
渲染倍数: -
提取时间: 2026-09-19 16:40:57
============================================================

============================================================
第 1 页
============================================================

（该页的文本，一行一段）
```

- 无文字的页不输出（与 CathayOCR 行为一致）；提取工具不涉及图像渲染，「渲染倍数」一栏保留该行、值写 `-`
- **只读 PDF，绝不修改原件**；已存在的 TXT：勾选「**已存在的 TXT 自动跳过（不覆盖）**」（默认勾选）时按跳过处理，勾选「覆盖已存在的文件」则重新写出

## 📦 下载

> 单文件 EXE 与便携版都**自带 Python 运行时 + 全部依赖**，解压即用，无需安装任何东西。

| 下载方式 | 链接 |
|:-------|:-----|
| 📥 **百度网盘**（密码 2026） | <待填：百度网盘分享链接> |
| 🐙 **GitHub Releases** | [CathayExtract v1.2.3](https://github.com/zzhjim02/CathayExtract/releases/tag/v1.2.3)（Assets 里直接下 `CathayExtract.exe`） |
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
│   ├── writer\              # TXT 写出（CathayOCR 同款格式）、目录创建
│   ├── coordinator\         # 任务调度、错误处理
├── core\                # 配置、异常、输出命名规则（output_naming.py）、设置持久化
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

可以，两种办法：
- 在**待处理列表**里选中不要的文件，点「**移除选中**」（本次不处理它们）；
- 或者用「文件名过滤」填通配符，例如 `卷一*.pdf`。
</details>

<details>
<summary>TXT 写到哪了？</summary>

**输出目录留空**时，TXT 就写在与 PDF **同一个文件夹**里，名字按源文件名后缀自动判定：
`甲书_PD6AIFOCR.pdf → 甲书_PD6AIFOCR.txt`、`甲书_layered.pdf → 甲书_result.txt`、`甲书.pdf → 甲书_result.txt`。
指定了输出目录则写到那里（目录结构照搬）。
</details>

## 📝 更新日志

- **v1.2.3**：**修正命名规则**——只替换/补**末尾那一段后缀**，文件名前面的一切（`_全1册`、8 位编号、`_unlocked`、`扫描版` 等）**原样保留**；`_opt` 属 PDF 侧后缀，TXT 里丢掉（`X_PD6AIFOCR_opt.pdf → X_PD6AIFOCR.txt`）；`_layered.pdf → _result.txt` 固定配对；繁简尾巴 `_【繁转简】` 原样保留；没有标准后缀才补 `_result`。自检覆盖 18 条命名用例，单元测试 51 项全过
- **v1.2.2**：TXT 命名改为**按源文件名后缀自动判定**（`_layered.pdf → _result.txt`、`_opt` 丢掉、同名同后缀、无后缀补 `_result`）；界面新增「**TXT 命名**」下拉（自动 / 统一 `_result` / 与源文件同名），选择会被记住
- **v1.2.1**：**支持拖入文件与文件夹**；新增**待处理列表**（可单独移除某个文件）；**输出目录默认留空 = 输出到原目录**；**导出格式对齐 CathayOCR Pro**（抬头 + `第 N 页` 分页）；不覆盖已存在的 TXT 时**自动跳过**；自检新增「原地输出 + 格式」检查
- **v1.2.0**：加入提取方法选择与性能统计、自动降级；更名 **CathayExtract** 并入 Cathay 工具链，许可由 MIT 调整为 **GPL-3.0**；加入便携运行时与 `启动.bat`、图标、`--selftest` 自检
- **v1.1.0**：多线程并行、智能跳过已处理文件、UI 调整
- **v1.0.0**：首版（PyMuPDF / pdfplumber / PyPDF2 三种提取方式，递归扫描，保持目录结构）

## ⚖️ 许可

[GPL-3.0](LICENSE) © 2026 浮生＆2cm（湖北大学历史文化学院）
