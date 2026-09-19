# 快速启动指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 如果安装失败,尝试使用国内镜像源:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2. 运行程序

```bash
python main.py
```

## 3. 基本使用

1. 点击"源目录"后的"浏览..."按钮,选择包含PDF文件的文件夹
2. 点击"输出目录"后的"浏览..."按钮,选择保存TXT文件的文件夹
3. (可选)在"文件名过滤"输入框中输入过滤模式,例如: `*.pdf`
4. 点击"开始提取"按钮
5. 等待处理完成
6. 在"处理结果"标签页查看统计信息

## 4. 运行测试

```bash
pytest tests/
```

## 5. 打包为可执行文件

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed CathayExtract.spec

# 可执行文件位于 dist/ 目录
```

## 常见问题

### 问题: 提示"未找到PDF文件"
- 确保源目录中有.pdf文件
- 检查文件扩展名是否为.pdf

### 问题: 提取的文本为空
- PDF文件可能不包含文本层(仅包含图像)
- 确保PDF文件是双层PDF格式

### 问题: 程序无法启动
- 检查Python版本(需要3.8+)
- 确保所有依赖已安装: `pip check`

更多问题请查看:
- [用户手册](docs/user_guide.md)
- [故障排查指南](docs/troubleshooting.md)

---

**项目完成!** 🎉
