from setuptools import setup, find_packages

setup(
    name="cathay-extract",
    version="1.1.0",
    author="浮生＆2cm",
    author_email="zzhjim@qq.com",
    description="CathayExtract · PDF OCR 文本提取器 - 专业的PDF OCR文本提取工具",
    long_description="一个专业的PDF OCR文本提取工具,支持批量处理、多线程并行、智能跳过等功能。"
    "\n作者: 浮生＆2cm (湖北大学历史文化学院)"
    "\n技术支持: 华为云CodeArts Agent",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6>=6.6.0",
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "chardet>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "cathay-extract=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
