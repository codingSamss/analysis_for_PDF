#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))

# 读取README.md
readme_path = os.path.join(root_dir, "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt
requirements_path = os.path.join(root_dir, "textbook_analyzer", "requirements.txt")
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="textbook_analyzer",
    version="0.1.0",
    author="Author",
    author_email="author@example.com",
    description="一个用于分析教材内容的工具，特别专注于提取和分析教材中的文化词条",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/textbook_analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "textbook-analyzer=textbook_analyzer.main:main",
        ],
    },
    include_package_data=True,
) 