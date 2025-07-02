#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ExcelFilterPro 构建脚本
用于本地打包和构建项目
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result

def clean_build():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            if path.is_dir():
                print(f"删除目录: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"删除文件: {path}")
                path.unlink()

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    
    # 安装基础依赖
    run_command("pip install -r requirements.txt")
    
    # 安装开发依赖
    if Path("requirements-dev.txt").exists():
        run_command("pip install -r requirements-dev.txt")
    
    # 安装构建工具
    run_command("pip install build pyinstaller")

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    if Path("tests").exists():
        run_command("pytest tests/ -v", check=False)
    else:
        print("没有找到测试目录，跳过测试")

def build_wheel():
    """构建Python wheel包"""
    print("🛠️ 构建Python包...")
    
    run_command("python -m build")
    print("✅ Python包构建完成，文件位于 dist/ 目录")

def build_executable():
    """构建可执行文件"""
    print("📱 构建可执行文件...")
    
    system = platform.system().lower()
    
    # 检查是否存在spec文件
    spec_file = "ExcelFilterPro.spec"
    if Path(spec_file).exists():
        print(f"使用spec文件: {spec_file}")
        run_command(f"pyinstaller {spec_file}")
    else:
        print("使用默认配置构建...")
        if system == "windows":
            run_command("pyinstaller --onefile --windowed --name ExcelFilterPro main.py")
        elif system == "darwin":  # macOS
            run_command("pyinstaller --onefile --windowed --name ExcelFilterPro main.py")
        else:  # Linux
            run_command("pyinstaller --onefile --name ExcelFilterPro main.py")
    
    print("✅ 可执行文件构建完成，文件位于 dist/ 目录")

def main():
    """主函数"""
    print("🚀 ExcelFilterPro 构建脚本")
    print(f"操作系统: {platform.system()}")
    print(f"Python版本: {sys.version}")
    print("-" * 50)
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"工作目录: {project_root}")
    
    try:
        # 解析命令行参数
        args = sys.argv[1:]
        
        if "--clean" in args or len(args) == 0:
            clean_build()
        
        if "--deps" in args or len(args) == 0:
            install_dependencies()
        
        if "--test" in args or len(args) == 0:
            run_tests()
        
        if "--wheel" in args or len(args) == 0:
            build_wheel()
        
        if "--exe" in args or len(args) == 0:
            build_executable()
        
        print("\n🎉 构建完成！")
        print("构建产物位于 dist/ 目录：")
        
        dist_dir = Path("dist")
        if dist_dir.exists():
            for file in dist_dir.iterdir():
                print(f"  - {file.name}")
        
    except KeyboardInterrupt:
        print("\n❌ 构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 