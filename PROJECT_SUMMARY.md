# Excel筛选器项目总结

## 项目概述

Excel筛选器是一个专业的Excel数据处理工具，主要功能包括：

- 📁 **多文件数据源管理** - 支持批量加载和处理Excel文件
- 🔗 **智能数据映射** - 基于查找匹配的数据复制功能
- 🎯 **灵活配置管理** - 支持方案的保存、加载和管理
- 📊 **结果导出** - 支持将处理结果导出为Excel文件
- 🖥️ **用户友好界面** - 基于PySide6的现代化图形界面

## 核心功能模块

### ✅ 已完成功能

- [x] 增强Excel处理器 (enhanced_excel_processor.py)
- [x] 数据映射引擎 (data_mapping_engine.py)
- [x] 配置管理器 (config_manager.py)
- [x] 用户界面组件
  - [x] 主窗口 (main_window.py)
  - [x] 文件上传组件 (upload_widget.py)
  - [x] 数据映射组件 (data_mapping_widget.py)
  - [x] 结果展示组件 (result_widget.py)
  - [x] 配置管理组件 (config_widget.py)

### 🗂️ 项目结构

```
Excel筛选器/
├── main.py                    # 程序入口
├── src/
│   ├── core/                  # 核心功能模块
│   │   ├── enhanced_excel_processor.py  # 增强Excel处理器 ✅
│   │   ├── data_mapping_engine.py       # 数据映射引擎 ✅
│   │   └── config_manager.py            # 配置管理器 ✅
│   ├── database/              # 数据模型
│   │   ├── connection.py      # 数据库连接
│   │   ├── dao.py            # 数据访问对象
│   │   └── models.py         # 数据模型定义
│   ├── ui/                   # 用户界面
│   │   ├── main_window.py    # 主窗口 ✅
│   │   └── widgets/          # UI组件
│   │       ├── upload_widget.py         # 文件上传 ✅
│   │       ├── data_mapping_widget.py   # 数据映射 ✅
│   │       ├── result_widget.py         # 结果展示 ✅
│   │       └── config_widget.py         # 配置管理 ✅
│   └── utils/                # 工具模块
│       ├── logger.py         # 日志系统
│       ├── constants.py      # 常量定义
│       ├── exceptions.py     # 异常定义
│       └── helpers.py        # 辅助函数
├── tests/                    # 测试模块
├── docs/                     # 文档
├── resources/                # 资源文件
└── requirements.txt          # 依赖包
```

## 核心算法说明

### 数据映射引擎

**文件**: src/core/data_mapping_engine.py

数据映射引擎实现了"查找匹配并复制数据"的核心功能：

1. **源数据查找**: 在源文件的指定列中查找匹配条件的行
2. **数据提取**: 从匹配行的指定列提取需要的值
3. **目标定位**: 在目标文件中找到匹配的插入位置
4. **数据插入**: 将提取的值插入到目标位置

支持多种匹配操作符：
- 等于 (=)、不等于 (≠)
- 包含、不包含
- 大于、小于、大于等于、小于等于
- 为空、不为空

### 增强Excel处理器

**文件**: src/core/enhanced_excel_processor.py

提供了强大的Excel文件处理能力：

1. **多文件加载**: 支持批量加载多个Excel文件
2. **智能解析**: 自动识别文件格式和工作表
3. **数据标准化**: 统一数据格式和结构
4. **元数据提取**: 提取文件和数据的元信息

## 数据模型

### 数据映射模型 (DataMapping)

```python
class DataMapping:
    name: str                    # 映射名称
    source_file: str            # 源文件路径
    target_file: str            # 目标文件路径
    source_match_coordinate: ExcelCoordinate  # 源匹配坐标
    source_match_value: Any     # 源匹配值
    source_value_coordinate: ExcelCoordinate  # 源取值坐标
    target_match_coordinate: ExcelCoordinate  # 目标匹配坐标
    target_match_value: Any     # 目标匹配值
    target_insert_coordinate: ExcelCoordinate # 目标插入坐标
    match_operator: FilterOperator            # 匹配操作符
    overwrite_existing: bool    # 是否覆盖已有数据
```

## 开发环境

### 技术栈
- **Python 3.8+**
- **PySide6** - GUI框架
- **Pandas** - 数据处理
- **SQLAlchemy** - 数据库ORM
- **Openpyxl** - Excel文件处理

### 开发工具
- **IDE**: VS Code / PyCharm
- **版本控制**: Git
- **包管理**: pip
- **测试框架**: pytest

## 部署说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

### 打包发布

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 许可证

本项目使用 MIT 许可证
