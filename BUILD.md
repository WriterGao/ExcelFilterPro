# ExcelFilterPro 构建和打包指南

## 🚀 快速开始

### 本地构建

使用我们提供的构建脚本，一键完成项目构建：

```bash
# 完整构建（清理、安装依赖、测试、打包）
python scripts/build.py

# 或者分步骤构建
python scripts/build.py --clean    # 清理构建目录
python scripts/build.py --deps     # 安装依赖
python scripts/build.py --test     # 运行测试
python scripts/build.py --wheel    # 构建Python包
python scripts/build.py --exe      # 构建可执行文件
```

### 手动构建

如果您喜欢手动控制构建过程：

#### 1. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install build pyinstaller
```

#### 2. 运行测试
```bash
pytest tests/ -v
```

#### 3. 构建Python包
```bash
python -m build
```

#### 4. 构建可执行文件

**Windows:**
```bash
pyinstaller --onefile --windowed --name ExcelFilterPro main.py
```

**macOS:**
```bash
pyinstaller --onefile --windowed --name ExcelFilterPro main.py
```

**Linux:**
```bash
pyinstaller --onefile --name ExcelFilterPro main.py
```

**使用spec文件（推荐）:**
```bash
pyinstaller ExcelFilterPro.spec
```

## 📦 发布到PyPI

### 测试发布（TestPyPI）
```bash
# 构建包
python -m build

# 上传到TestPyPI
python -m twine upload --repository testpypi dist/*
```

### 正式发布
```bash
# 上传到PyPI
python -m twine upload dist/*
```

## 🏷️ GitHub发布

### 自动发布
项目配置了GitHub Actions，当您推送tag时会自动构建和发布：

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

### 手动发布
1. 在GitHub仓库页面点击"Releases"
2. 点击"Create a new release"
3. 选择标签版本或创建新标签
4. 填写发布说明
5. 上传构建好的文件

## 🛠️ 构建配置

### PyInstaller配置
项目包含 `ExcelFilterPro.spec` 文件，配置了：
- 隐含导入的模块
- 资源文件打包
- 图标设置
- 平台特定设置

### 项目配置
- `pyproject.toml`: 现代Python项目配置
- `setup.py`: 传统setuptools配置（备用）
- `requirements.txt`: 运行时依赖
- `requirements-dev.txt`: 开发时依赖

## 🔧 常见问题

### Q: 可执行文件太大怎么办？
A: 可以尝试以下优化：
```bash
# 排除不需要的模块
pyinstaller --exclude-module matplotlib --exclude-module scipy ExcelFilterPro.spec

# 使用UPX压缩
pyinstaller --upx-dir=/path/to/upx ExcelFilterPro.spec
```

### Q: 在某些平台上运行出错？
A: 检查依赖和系统要求：
- Python 3.8+
- 对应平台的PySide6二进制文件
- 足够的内存和磁盘空间

### Q: 如何添加图标？
A: 将图标文件放在 `resources/icons/app.ico`，spec文件会自动使用。

## 📋 支持的平台

| 平台 | Python版本 | 状态 |
|------|------------|------|
| Windows 10/11 | 3.8-3.11 | ✅ 支持 |
| macOS 10.15+ | 3.8-3.11 | ✅ 支持 |
| Ubuntu 20.04+ | 3.8-3.11 | ✅ 支持 |

## 📞 获取帮助

如果在构建过程中遇到问题：
1. 查看构建日志
2. 检查依赖版本
3. 在GitHub Issues中报告问题 