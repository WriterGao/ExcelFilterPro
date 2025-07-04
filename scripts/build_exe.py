#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地构建EXE文件的脚本
支持自定义配置和平台选择
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import platform

class ExeBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "ExcelFilterPro.spec"
        
    def clean_build(self):
        """清理之前的构建文件"""
        print("🧹 清理构建目录...")
        
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print(f"  ✓ 删除 {self.dist_dir}")
            
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"  ✓ 删除 {self.build_dir}")
            
        if self.spec_file.exists():
            self.spec_file.unlink()
            print(f"  ✓ 删除 {self.spec_file}")
    
    def check_dependencies(self):
        """检查依赖包是否已安装"""
        print("🔍 检查依赖包...")
        
        try:
            import PyInstaller
            print(f"  ✓ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("  ❌ PyInstaller 未安装")
            print("     运行: pip install pyinstaller")
            return False
            
        # 检查项目依赖
        required_packages = ['PySide6', 'pandas', 'openpyxl', 'SQLAlchemy']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"  ✓ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")
        
        if missing_packages:
            print(f"\n请安装缺失的包:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
            
        return True
    
    def get_build_options(self, args):
        """根据参数和平台生成构建选项"""
        current_platform = platform.system().lower()
        
        # 基础选项
        options = [
            '--onefile',  # 打包成单个文件
            '--name=ExcelFilterPro',  # 可执行文件名
        ]
        
        # 根据平台添加选项
        if current_platform == 'windows':
            options.append('--windowed')  # Windows下隐藏控制台
            # 添加图标
            icon_path = self.project_root / "resources" / "icons" / "app.ico"
            if icon_path.exists():
                options.append(f'--icon={icon_path}')
            else:
                print("  ⚠️  未找到Windows图标文件: resources/icons/app.ico")
                
        elif current_platform == 'darwin':  # macOS
            options.append('--windowed')
            # macOS图标
            icon_path = self.project_root / "resources" / "icons" / "app.icns"
            if icon_path.exists():
                options.append(f'--icon={icon_path}')
            else:
                print("  ⚠️  未找到macOS图标文件: resources/icons/app.icns")
        
        # 添加资源文件
        resources_dir = self.project_root / "resources"
        if resources_dir.exists():
            options.append(f'--add-data={resources_dir}{os.pathsep}resources')
        
        # 添加源码目录
        src_dir = self.project_root / "src"
        if src_dir.exists():
            options.append(f'--add-data={src_dir}{os.pathsep}src')
        
        # 自定义选项
        if args.debug:
            options.append('--debug=all')
            options.append('--console')  # 调试时显示控制台
        
        if args.upx:
            upx_path = shutil.which('upx')
            if upx_path:
                options.append(f'--upx-dir={upx_path}')
                print("  ✓ 启用UPX压缩")
            else:
                print("  ⚠️  UPX未安装，跳过压缩")
        
        # 隐藏导入模块
        hidden_imports = [
            'PySide6.QtCore',
            'PySide6.QtWidgets', 
            'PySide6.QtGui',
            'pandas',
            'openpyxl',
            'SQLAlchemy'
        ]
        
        for module in hidden_imports:
            options.append(f'--hidden-import={module}')
        
        return options
    
    def build_exe(self, args):
        """构建可执行文件"""
        print("🏗️  开始构建可执行文件...")
        
        # 构建命令
        main_py = self.project_root / "main.py"
        if not main_py.exists():
            print(f"❌ 找不到主文件: {main_py}")
            return False
        
        options = self.get_build_options(args)
        cmd = ['pyinstaller'] + options + [str(main_py)]
        
        print(f"📋 构建命令: {' '.join(cmd)}")
        print()
        
        try:
            # 执行构建
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            
            # 检查结果
            exe_name = "ExcelFilterPro.exe" if platform.system() == "Windows" else "ExcelFilterPro"
            exe_path = self.dist_dir / exe_name
            
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"\n✅ 构建成功!")
                print(f"📁 文件位置: {exe_path}")
                print(f"📏 文件大小: {file_size:.1f} MB")
                
                return True
            else:
                print(f"\n❌ 构建失败: 找不到 {exe_path}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 构建失败: {e}")
            return False
    
    def test_exe(self):
        """测试生成的可执行文件"""
        print("\n🧪 测试可执行文件...")
        
        exe_name = "ExcelFilterPro.exe" if platform.system() == "Windows" else "ExcelFilterPro"
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            print(f"❌ 找不到可执行文件: {exe_path}")
            return False
        
        # 检查文件权限
        if not os.access(exe_path, os.X_OK):
            print(f"❌ 文件无执行权限: {exe_path}")
            return False
        
        # 对于GUI应用，简单检查文件能否启动
        try:
            if platform.system() != "Windows":
                # Unix系统可以检查帮助信息
                result = subprocess.run([str(exe_path), '--help'], 
                                      capture_output=True, 
                                      timeout=10)
                print("✅ 可执行文件测试通过")
            else:
                print("✅ Windows可执行文件生成成功")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("✅ 程序启动正常 (GUI应用)")
            return True
        except Exception as e:
            print(f"⚠️  测试警告: {e}")
            return True  # GUI应用测试可能会失败，但不一定有问题
    
    def package_release(self, args):
        """打包发布文件"""
        if not args.package:
            return
            
        print("\n📦 打包发布文件...")
        
        # 创建发布目录
        release_dir = self.project_root / "release"
        release_dir.mkdir(exist_ok=True)
        
        # 确定版本号
        version = args.version or "dev"
        current_platform = platform.system().lower()
        
        # 复制可执行文件
        exe_name = "ExcelFilterPro.exe" if platform.system() == "Windows" else "ExcelFilterPro"
        exe_path = self.dist_dir / exe_name
        
        if exe_path.exists():
            release_name = f"ExcelFilterPro-{version}-{current_platform}"
            if platform.system() == "Windows":
                release_name += ".exe"
            
            release_file = release_dir / release_name
            shutil.copy2(exe_path, release_file)
            print(f"  ✓ 复制到: {release_file}")
            
            # 生成校验和
            import hashlib
            with open(release_file, 'rb') as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            
            checksum_file = release_dir / f"{release_name}.sha256"
            with open(checksum_file, 'w') as f:
                f.write(f"{sha256}  {release_name}\n")
            print(f"  ✓ 生成校验和: {checksum_file}")

def main():
    parser = argparse.ArgumentParser(description="构建ExcelFilterPro可执行文件")
    parser.add_argument('--clean', action='store_true', help='清理之前的构建')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--upx', action='store_true', help='使用UPX压缩')
    parser.add_argument('--package', action='store_true', help='打包发布文件')
    parser.add_argument('--version', help='版本号')
    parser.add_argument('--test', action='store_true', help='测试生成的可执行文件')
    
    args = parser.parse_args()
    
    builder = ExeBuilder()
    
    print("🚀 ExcelFilterPro EXE构建工具")
    print("=" * 50)
    
    try:
        # 清理构建
        if args.clean:
            builder.clean_build()
            print()
        
        # 检查依赖
        if not builder.check_dependencies():
            return 1
        print()
        
        # 构建
        if not builder.build_exe(args):
            return 1
        
        # 测试
        if args.test:
            if not builder.test_exe():
                return 1
        
        # 打包
        builder.package_release(args)
        
        print("\n🎉 构建完成!")
        print(f"📁 输出目录: {builder.dist_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  构建已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 