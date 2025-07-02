#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel筛选器桌面应用程序
主程序入口文件
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QDir
    from PySide6.QtGui import QIcon
    
    from src.ui.main_window import MainWindow
    from src.utils.logger import setup_logger
    from src.utils.constants import APP_NAME, VERSION
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def setup_application():
    """初始化应用程序设置"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("开发团队")
    
    # 设置应用程序图标
    icon_path = current_dir / "resources" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 设置Qt插件路径（用于PyInstaller打包）
    if hasattr(sys, '_MEIPASS'):
        plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
        QApplication.addLibraryPath(plugin_path)
    
    # 移除已弃用的高DPI支持设置，PySide6已默认启用
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    return app


def main():
    """主函数"""
    try:
        # 设置日志
        setup_logger()
        
        # 创建应用程序
        app = setup_application()
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 