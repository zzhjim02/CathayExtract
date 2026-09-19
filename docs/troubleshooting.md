# CathayExtract - 故障排查指南

## 目录
1. [安装问题](#安装问题)
2. [运行问题](#运行问题)
3. [处理问题](#处理问题)
4. [性能问题](#性能问题)
5. [其他问题](#其他问题)

---

## 安装问题

### 问题1: pip install 失败

**症状**: 运行 `pip install -r requirements.txt` 时出现错误

**可能原因**:
- 网络连接问题
- pip版本过旧
- Python版本不兼容

**解决方案**:
```bash
# 1. 升级pip
python -m pip install --upgrade pip

# 2. 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 检查Python版本(需要3.8+)
python --version
```

### 问题2: PyQt6安装失败

**症状**: 安装PyQt6时出现编译错误

**解决方案**:
```bash
# 使用预编译的wheel包
pip install PyQt6 --only-binary :all:

# 如果仍然失败,尝试使用conda
conda install pyqt
```

### 问题3: 依赖冲突

**症状**: 安装时提示依赖版本冲突

**解决方案**:
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 然后重新安装依赖
pip install -r requirements.txt
```

---

## 运行问题

### 问题1: 程序无法启动

**症状**: 运行 `python main.py` 无反应或立即退出

**可能原因**:
- 缺少依赖库
- Python路径问题
- 权限问题

**解决方案**:
```bash
# 1. 检查依赖是否完整
pip check

# 2. 查看详细错误信息
python main.py --verbose

# 3. 检查Python路径
which python  # Linux/macOS
where python  # Windows
```

### 问题2: 界面显示异常

**症状**: 窗口显示不正常或控件错位

**解决方案**:
```bash
# 1. 更新显卡驱动
# 2. 尝试禁用高DPI缩放
# 在main.py中注释掉以下两行:
# app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
# app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
```

### 问题3: 中文显示乱码

**症状**: 界面中的中文显示为乱码

**解决方案**:
```bash
# 1. 安装中文字体
# 2. 设置系统编码为UTF-8
# 3. 在Windows上,确保系统区域设置正确
```

---

## 处理问题

### 问题1: 扫描不到PDF文件

**症状**: 选择源目录后,提示"未找到PDF文件"

**可能原因**:
- 目录中没有PDF文件
- PDF文件扩展名不是.pdf
- 权限问题

**解决方案**:
```bash
# 1. 检查目录中是否有.pdf文件
ls /path/to/source/*.pdf  # Linux/macOS
dir "C:\path\to\source\*.pdf"  # Windows

# 2. 检查文件权限
chmod -R 755 /path/to/source  # Linux/macOS

# 3. 检查文件是否为PDF格式
file /path/to/source/file.pdf  # Linux/macOS
```

### 问题2: 提取的文本为空

**症状**: 处理成功但TXT文件为空

**可能原因**:
- PDF文件不包含文本层(仅包含图像)
- PDF文件损坏
- 文本层被加密

**解决方案**:
```bash
# 1. 使用PDF查看器检查文件是否包含可选文本
# 2. 尝试使用其他PDF处理工具验证
# 3. 检查PDF文件是否为双层PDF格式
```

### 问题3: 提取的文本乱码

**症状**: TXT文件中的文本显示为乱码

**可能原因**:
- PDF使用特殊编码
- 编码检测失败

**解决方案**:
```bash
# 1. 尝试手动指定编码
# 2. 使用文本编辑器(如Notepad++)打开,尝试不同编码
# 3. 联系开发者反馈问题
```

### 问题4: 部分文件处理失败

**症状**: 处理结果中显示有失败的文件

**解决方案**:
```bash
# 1. 查看"错误日志"标签页,获取详细错误信息
# 2. 保存错误日志文件到本地
# 3. 根据错误信息逐个排查失败的文件
```

---

## 性能问题

### 问题1: 处理速度慢

**症状**: 处理大量文件时速度很慢

**可能原因**:
- PDF文件很大
- 计算机性能不足
- 磁盘I/O瓶颈

**解决方案**:
```bash
# 1. 分批处理文件,避免一次性处理过多
# 2. 关闭其他占用资源的程序
# 3. 使用SSD存储源文件和输出文件
# 4. 增加系统内存
```

### 问题2: 内存占用过高

**症状**: 处理过程中内存占用持续增长

**解决方案**:
```bash
# 1. 减少同时处理的文件数量
# 2. 分批处理大文件
# 3. 重启程序释放内存
```

### 问题3: 程序卡死

**症状**: 程序界面无响应

**解决方案**:
```bash
# 1. 等待一段时间,可能是处理大文件
# 2. 点击"停止"按钮取消当前任务
# 3. 如果仍然卡死,强制结束程序并重启
```

---

## 其他问题

### 问题1: 如何获取帮助?

**解决方案**:
- 查看用户手册 (docs/user_guide.md)
- 查看故障排查指南 (本文档)
- 在项目仓库提交Issue
- 联系技术支持

### 问题2: 如何卸载程序?

**解决方案**:
```bash
# 1. 删除项目文件夹
rm -rf cathay-extract  # Linux/macOS
rmdir /s /q cathay-extract  # Windows

# 2. (可选)卸载Python包
pip uninstall PyQt6 PyPDF2 pdfplumber chardet
```

### 问题3: 如何更新到最新版本?

**解决方案**:
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
pip install -r requirements.txt --upgrade

# 3. 重新运行程序
python main.py
```

### 问题4: 如何贡献代码?

**解决方案**:
1. Fork项目仓库
2. 创建特性分支
3. 提交代码
4. 创建Pull Request

---

## 联系支持

如果以上解决方案都无法解决您的问题,请提供以下信息:
- 操作系统版本
- Python版本
- 程序版本
- 详细的错误信息
- 复现步骤

联系方式:
- 项目仓库: [GitHub Issues]
- 邮箱: support@example.com

---

## 附录: 常用命令

### Windows
```bash
# 查看Python版本
python --version

# 查看已安装的包
pip list

# 检查依赖
pip check

# 运行程序
python main.py
```

### Linux/macOS
```bash
# 查看Python版本
python3 --version

# 查看已安装的包
pip3 list

# 检查依赖
pip3 check

# 运行程序
python3 main.py
```
