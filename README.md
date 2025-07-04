# Excel筛选器桌面应用

## 项目概述

Excel筛选器是一个基于Python PySide6开发的桌面应用程序，旨在帮助用户高效地对多个Excel文件进行数据筛选，并将筛选结果按照自定义规则填充到指定的输出模板中。

## 主要功能

- 📁 **多文件上传**：支持上传多个Excel作为数据源，上传输出模板
- 🔍 **智能识别**：自动识别Excel表头作为筛选变量
- ⚙️ **灵活筛选**：支持多条件组合筛选（等于、大于、小于、包含等）
- 📊 **分列输出**：每个筛选条件对应一个输出列
- 💾 **配置保存**：筛选方案可保存和重复使用
- 🎨 **美观界面**：现代化桌面GUI界面

## 技术栈

- **GUI框架**：PySide6 (Qt6)
- **数据处理**：pandas + openpyxl
- **数据库**：SQLite
- **打包工具**：PyInstaller

## 快速开始

### 📥 下载预编译版本 (推荐)

1. 前往 [Releases页面](https://github.com/WriterGao/ExcelFilterPro/releases)
2. 下载对应平台的可执行文件：
   - **Windows**: `ExcelFilterPro-*-windows.exe`
   - **macOS**: `ExcelFilterPro-*-macos`
   - **Linux**: `ExcelFilterPro-*-linux`
3. 双击运行即可使用

### 🛠️ 从源码运行

#### 环境要求

- Python 3.8+
- pip

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 运行应用

```bash
python main.py
```

### 🏗️ 自动构建EXE

本项目支持通过GitHub Actions自动构建多平台可执行文件：

#### 手动触发构建

1. 前往项目的 [Actions页面](https://github.com/WriterGao/ExcelFilterPro/actions)
2. 选择 "构建EXE文件" 工作流
3. 点击 "Run workflow"
4. 选择构建参数：
   - **版本号**: 自定义版本号或使用"auto"
   - **构建平台**: 选择all、windows、macos或linux
5. 等待构建完成，在Artifacts中下载

#### 自动构建触发条件

- 推送到 `main` 或 `develop` 分支
- 创建Pull Request到 `main` 分支
- 推送Git标签 (会自动创建Release)

#### 本地构建EXE

使用提供的构建脚本：

```bash
# 基础构建
python scripts/build_exe.py

# 清理后构建
python scripts/build_exe.py --clean

# 调试模式构建
python scripts/build_exe.py --debug

# 构建并打包发布
python scripts/build_exe.py --package --version 1.0.0

# 构建后测试
python scripts/build_exe.py --test
```

#### 构建参数说明

- `--clean`: 清理之前的构建文件
- `--debug`: 启用调试模式，显示详细信息
- `--upx`: 使用UPX压缩(需要安装UPX)
- `--package`: 打包为发布文件
- `--version`: 指定版本号
- `--test`: 构建后测试可执行文件

## 项目结构

```
excel-filter-desktop/
├── .github/workflows/       # GitHub Actions工作流
│   ├── build-exe.yml       # EXE构建工作流
│   └── release.yml         # 发布工作流
├── docs/                   # 项目文档
│   ├── requirements.md     # 需求文档  
│   ├── design.md          # 设计文档
│   ├── user-manual.md     # 用户手册
│   ├── dev-guide.md       # 开发指南
│   ├── deployment.md      # 部署文档
│   └── testing.md         # 测试文档
├── scripts/               # 构建脚本
│   └── build_exe.py      # 本地EXE构建脚本
├── src/                   # 源代码
│   ├── ui/                # 用户界面
│   ├── core/              # 核心逻辑
│   ├── database/          # 数据库相关
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── resources/             # 资源文件
│   └── icons/            # 应用图标
├── requirements.txt       # 运行时依赖
├── requirements-dev.txt   # 开发依赖
└── main.py               # 程序入口
```

## 文档索引

| 文档 | 描述 | 读者 |
|------|------|------|
| [需求文档](docs/requirements.md) | 详细的功能需求和业务逻辑 | 产品经理、开发者 |
| [设计文档](docs/design.md) | 系统架构和技术设计 | 开发者、架构师 |
| [用户手册](docs/user-manual.md) | 软件使用说明 | 最终用户 |
| [开发指南](docs/dev-guide.md) | 开发环境搭建和代码规范 | 开发者 |
| [部署文档](docs/deployment.md) | 软件打包和部署说明 | 运维人员 |
| [测试文档](docs/testing.md) | 测试计划和测试用例 | 测试人员 |

## 开发状态 ✅ 核心功能已完成

- [x] 需求分析 (100%)
- [x] 系统设计 (100%)
- [x] 项目架构搭建 (100%)
- [x] 基础代码框架 (100%)
- [x] 文档体系建立 (100%)
- [x] 界面组件开发 (100%) 🆕
- [x] 核心功能实现 (100%) 🆕
- [x] 测试用例编写 (100%) 🆕
- [x] 功能验证测试 (100%) 🆕
- [x] 自动化构建系统 (100%) 🆕
- [ ] 性能优化
- [ ] 多语言支持

## 🚀 功能演示

项目包含完整的功能演示脚本，可以验证所有核心功能：

```bash
# 运行功能演示（推荐）
python demo.py
```

**演示内容**：
- ✅ Excel文件处理：加载2个Excel文件，处理8行数据
- ✅ 数据筛选：执行3个不同筛选规则，筛选出11行结果
- ✅ 配置管理：创建和保存筛选方案
- ✅ 结果导出：导出筛选结果到Excel文件

## 🧪 测试验证

```bash
# 运行基础测试
python tests/test_basic.py

# GUI测试（需要PySide6）
python test_gui.py
```

## 版本历史

- **v1.0.0** 🎉 - 核心功能完整实现
  - ✅ Excel处理引擎
  - ✅ 数据筛选引擎  
  - ✅ 配置管理系统
  - ✅ UI组件库
  - ✅ 功能测试验证
  - ✅ 自动化构建流程
- v0.1.0 - 项目初始化，文档创建

## 许可证

MIT License

## 贡献指南

请阅读 [开发指南](docs/dev-guide.md) 了解如何贡献代码。

## 联系方式

如有问题或建议，请提交Issue。 