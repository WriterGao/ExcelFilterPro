# 构建指南

## 📦 EXE文件构建

本项目提供了多种方式来构建可执行文件，让用户无需安装Python环境即可使用。

## 🚀 GitHub Actions 自动构建

### 手动触发构建

1. **访问Actions页面**
   - 前往 [GitHub Actions](https://github.com/WriterGao/ExcelFilterPro/actions)
   - 选择 "构建EXE文件" 工作流

2. **启动构建**
   - 点击 "Run workflow" 按钮
   - 选择构建参数：
     - **版本号**: 输入版本号（如1.0.0）或使用"auto"自动获取
     - **构建平台**: 选择要构建的平台
       - `all`: 构建所有平台
       - `windows`: 仅Windows
       - `macos`: 仅macOS
       - `linux`: 仅Linux

3. **下载构建结果**
   - 等待构建完成（约10-20分钟）
   - 在Actions运行页面底部的 "Artifacts" 区域下载

### 自动构建触发

以下操作会自动触发构建：

- **推送到主分支**: 推送到 `main` 或 `develop` 分支
- **Pull Request**: 向 `main` 分支提交PR
- **标签发布**: 推送Git标签（格式：v1.0.0）

### 发布版本

要创建正式发布版本：

```bash
# 1. 更新版本号
git tag v1.0.0

# 2. 推送标签
git push origin v1.0.0
```

这将自动构建所有平台的可执行文件并创建GitHub Release。

## 🔧 本地构建

### 环境准备

```bash
# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install pyinstaller
```

### 使用构建脚本

```bash
# 基础构建
python scripts/build_exe.py

# 清理后重新构建
python scripts/build_exe.py --clean

# 调试模式构建（显示详细信息）
python scripts/build_exe.py --debug

# 构建并打包发布文件
python scripts/build_exe.py --package --version 1.0.0

# 构建后自动测试
python scripts/build_exe.py --test

# 使用UPX压缩（需要先安装UPX）
python scripts/build_exe.py --upx
```

### 手动构建

```bash
# Windows
pyinstaller --onefile --windowed --name ExcelFilterPro --icon=resources/icons/app.ico main.py

# macOS
pyinstaller --onefile --windowed --name ExcelFilterPro main.py

# Linux
pyinstaller --onefile --name ExcelFilterPro main.py
```

## 📋 构建配置

### PyInstaller 配置选项

| 选项 | 说明 | 使用场景 |
|------|------|----------|
| `--onefile` | 打包为单个文件 | 便于分发 |
| `--windowed` | 隐藏控制台窗口 | GUI应用 |
| `--debug` | 启用调试信息 | 问题排查 |
| `--icon` | 设置程序图标 | 美化界面 |
| `--add-data` | 添加资源文件 | 包含静态资源 |
| `--hidden-import` | 显式导入模块 | 解决导入问题 |

### 资源文件

构建时会自动包含以下资源：

- `resources/` - 资源文件目录
- `src/` - 源代码目录
- 应用图标文件

### 平台差异

| 平台 | 可执行文件 | 图标格式 | 特殊选项 |
|------|------------|----------|----------|
| Windows | `.exe` | `.ico` | `--windowed` |
| macOS | 无扩展名 | `.icns` | `--windowed` |
| Linux | 无扩展名 | `.png` | 无 |

## 🧪 测试构建

### 自动测试

构建脚本包含自动测试功能：

```bash
python scripts/build_exe.py --test
```

### 手动测试

1. **检查文件存在**
   ```bash
   ls -la dist/
   ```

2. **测试启动**
   ```bash
   # Windows
   dist/ExcelFilterPro.exe
   
   # macOS/Linux
   ./dist/ExcelFilterPro
   ```

3. **检查依赖**
   - 在没有Python环境的机器上测试
   - 验证所有功能正常工作

## 🐛 常见问题

### 构建失败

**问题**: PyInstaller 构建失败
**解决**: 
- 检查所有依赖是否已安装
- 使用 `--debug` 选项查看详细错误
- 清理构建目录后重试

**问题**: 导入模块错误
**解决**: 
- 在构建脚本中添加 `--hidden-import` 选项
- 检查模块是否正确安装

### 运行问题

**问题**: 可执行文件无法启动
**解决**: 
- 检查文件权限（Unix系统）
- 在命令行运行查看错误信息
- 检查是否缺少系统依赖

**问题**: 找不到资源文件
**解决**: 
- 确认资源文件路径正确
- 检查 `--add-data` 选项配置

### 性能优化

**问题**: 文件太大
**解决**: 
- 使用UPX压缩
- 移除不必要的依赖
- 使用 `--exclude-module` 排除无用模块

**问题**: 启动速度慢
**解决**: 
- 这是PyInstaller的正常现象
- 考虑使用目录模式而非单文件模式

## 🔗 相关链接

- [PyInstaller文档](https://pyinstaller.readthedocs.io/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [项目开发指南](dev-guide.md)
- [部署文档](deployment.md) 