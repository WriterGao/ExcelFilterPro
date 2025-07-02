#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ExcelFilterPro - 专业的Excel数据过滤和映射工具
"""

from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding='utf-8')

setup(
    name="ExcelFilterPro",
    version="1.0.0",
    description="专业的Excel数据过滤和映射工具",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/WriterGao/ExcelFilterPro",
    author="WriterGao",
    author_email="mrgao3306@163.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Office Suites",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.4.0",
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "SQLAlchemy>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
            "pyinstaller>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "excelfilterpro=main:main",
        ],
    },
    package_data={
        "": ["*.json", "*.yml", "*.yaml", "*.ini"],
    },
    include_package_data=True,
    zip_safe=False,
) 