# 部署文档

## 1. 部署概述

本文档详细介绍了Excel筛选器桌面应用的打包、分发和部署流程。应用支持Windows、macOS和Linux三个平台的部署。

## 2. 打包准备

### 2.1 环境检查
```bash
# 检查Python版本
python --version  # 确保>=3.8

# 检查依赖安装
pip list

# 运行测试确保功能正常
pytest tests/
```

### 2.2 清理项目
```bash
# 清理临时文件
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf build/
rm -rf dist/

# 清理日志文件
rm -rf logs/
```

### 2.3 更新版本信息
```python
# src/utils/constants.py
VERSION = "1.0.0"
BUILD_DATE = "2024-12-01"
```

## 3. PyInstaller打包

### 3.1 安装PyInstaller
```bash
pip install pyinstaller
```

### 3.2 创建spec文件
```python
# excel-filter.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons', 'icons'),
        ('resources/styles', 'styles'),
        ('resources/sql', 'sql'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'pandas',
        'openpyxl',
        'sqlalchemy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExcelFilter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico'
)
```

### 3.3 执行打包
```bash
# 使用spec文件打包
pyinstaller excel-filter.spec

# 或者直接命令行打包
pyinstaller --onefile --windowed --icon=resources/icons/app.ico main.py
```

## 4. 平台特定配置

### 4.1 Windows部署

#### 打包配置
```bash
# Windows特定打包
pyinstaller --onefile --windowed \
    --icon=resources/icons/app.ico \
    --add-data "resources;resources" \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtWidgets \
    main.py
```

#### 创建安装包
```nsis
# installer.nsi (NSIS脚本)
!define APP_NAME "Excel筛选器"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "开发团队"
!define APP_EXE "ExcelFilter.exe"

OutFile "ExcelFilter-${APP_VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "MainSection"
    SetOutPath "$INSTDIR"
    File "dist\ExcelFilter.exe"
    
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd
```

### 4.2 macOS部署

#### 打包配置
```bash
# macOS特定打包
pyinstaller --onefile --windowed \
    --icon=resources/icons/app.icns \
    --add-data "resources:resources" \
    main.py
```

#### 创建DMG文件
```bash
# 创建DMG安装包
create-dmg \
    --volname "Excel筛选器" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "ExcelFilter.app" 175 120 \
    --hide-extension "ExcelFilter.app" \
    --app-drop-link 425 120 \
    "ExcelFilter-1.0.0.dmg" \
    "dist/"
```

### 4.3 Linux部署

#### 打包配置
```bash
# Linux特定打包
pyinstaller --onefile \
    --add-data "resources:resources" \
    main.py
```

#### 创建AppImage
```bash
# 使用AppImage打包
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# 创建AppDir结构
mkdir -p ExcelFilter.AppDir/usr/bin
cp dist/main ExcelFilter.AppDir/usr/bin/ExcelFilter

# 创建桌面文件
cat > ExcelFilter.AppDir/ExcelFilter.desktop << EOF
[Desktop Entry]
Type=Application
Name=Excel筛选器
Exec=ExcelFilter
Icon=ExcelFilter
Categories=Office;
EOF

# 生成AppImage
./appimagetool-x86_64.AppImage ExcelFilter.AppDir
```

## 5. 自动化构建

### 5.1 GitHub Actions配置
```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build
      run: pyinstaller excel-filter.spec
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: ExcelFilter-Windows
        path: dist/ExcelFilter.exe

  build-macos:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build
      run: pyinstaller excel-filter.spec
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: ExcelFilter-macOS
        path: dist/ExcelFilter

  build-linux:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build
      run: pyinstaller excel-filter.spec
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: ExcelFilter-Linux
        path: dist/ExcelFilter
```

### 5.2 本地构建脚本
```bash
#!/bin/bash
# build.sh

set -e

echo "开始构建Excel筛选器..."

# 清理旧文件
rm -rf build/ dist/

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行测试
pytest tests/

# 执行打包
pyinstaller excel-filter.spec

# 检查打包结果
if [ -f "dist/ExcelFilter" ] || [ -f "dist/ExcelFilter.exe" ]; then
    echo "✅ 打包成功！"
    ls -la dist/
else
    echo "❌ 打包失败！"
    exit 1
fi

echo "🎉 构建完成！"
```

## 6. 版本发布

### 6.1 版本号规范
采用语义化版本控制 (Semantic Versioning)：
- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 6.2 发布清单
- [ ] 更新版本号
- [ ] 更新CHANGELOG.md
- [ ] 运行完整测试套件
- [ ] 构建所有平台包
- [ ] 创建发布标签
- [ ] 上传发布文件
- [ ] 更新下载链接

### 6.3 发布模板
```markdown
## Excel筛选器 v1.0.0

### 新功能
- ✨ 支持多Excel文件数据源
- ✨ 可视化筛选条件设置
- ✨ 筛选方案保存和管理
- ✨ 批量数据处理

### 改进
- 🚀 优化大文件处理性能
- 💄 改进用户界面设计
- 📝 完善文档和帮助

### 修复
- 🐛 修复数据类型识别问题
- 🐛 修复内存泄漏问题

### 下载
- [Windows (x64)](link-to-windows-installer)
- [macOS (Universal)](link-to-macos-dmg)  
- [Linux (x64)](link-to-linux-appimage)

### 系统要求
- Windows 10+ / macOS 10.14+ / Ubuntu 18.04+
- 内存：建议4GB以上
- 磁盘：至少100MB可用空间
```

## 7. 分发策略

### 7.1 官方渠道
- **GitHub Releases**：主要分发渠道
- **官方网站**：提供下载链接和文档
- **软件中心**：考虑上架主流软件商店

### 7.2 文件签名
```bash
# Windows代码签名
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com ExcelFilter.exe

# macOS代码签名
codesign --force --verify --verbose --sign "Developer ID Application: Your Name" ExcelFilter.app
```

### 7.3 校验和生成
```bash
# 生成文件校验和
sha256sum ExcelFilter-1.0.0-Windows.exe > checksums.txt
sha256sum ExcelFilter-1.0.0-macOS.dmg >> checksums.txt
sha256sum ExcelFilter-1.0.0-Linux.AppImage >> checksums.txt
```

## 8. 部署验证

### 8.1 安装测试
- [ ] 全新系统安装测试
- [ ] 升级安装测试
- [ ] 卸载功能测试
- [ ] 权限要求验证

### 8.2 功能测试
- [ ] 基本功能完整性
- [ ] 文件关联正确性
- [ ] 快捷方式有效性
- [ ] 错误处理机制

### 8.3 性能测试
- [ ] 启动时间测试
- [ ] 内存使用测试  
- [ ] 大文件处理测试
- [ ] 长时间运行稳定性

## 9. 问题排查

### 9.1 常见打包问题

**Q: 缺少模块错误**
```bash
# 解决方案：添加隐藏导入
pyinstaller --hidden-import=missing_module main.py
```

**Q: 文件路径问题**
```python
# 解决方案：使用资源路径
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

**Q: Qt插件加载失败**
```python
# 解决方案：设置Qt插件路径
import os
import sys
from PySide6 import QtCore

if hasattr(sys, '_MEIPASS'):
    QtCore.QCoreApplication.addLibraryPath(
        os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
    )
```

### 9.2 部署问题

**Q: 杀毒软件误报**
- 提交样本到杀毒软件厂商
- 申请数字证书签名
- 联系用户添加白名单

**Q: 依赖库版本冲突**
- 使用虚拟环境隔离
- 固定依赖库版本
- 提供详细的环境说明

## 10. 维护计划

### 10.1 定期维护
- **每月**：安全更新检查
- **每季度**：依赖库更新
- **每半年**：主要功能更新
- **每年**：架构优化评估

### 10.2 监控指标
- 下载量统计
- 用户反馈收集
- 错误报告分析
- 性能数据监控

---

**维护者**：开发团队  
**最后更新**：2024年12月 