@echo off
REM Excel筛选器开发环境设置脚本 (Windows)

echo 🚀 开始设置Excel筛选器开发环境...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python版本检查通过

REM 创建虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
) else (
    echo ✅ 虚拟环境已存在
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
pip install --upgrade pip

REM 安装依赖
echo 📦 安装项目依赖...
pip install -r requirements.txt

echo 📦 安装开发依赖...
pip install -r requirements-dev.txt

REM 创建目录
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

echo 🎉 开发环境设置完成！
echo.
echo 📋 下一步操作：
echo 1. 激活虚拟环境: venv\Scripts\activate.bat
echo 2. 运行应用程序: python main.py
echo 3. 运行测试: pytest tests/
echo 4. 代码格式化: black src/ tests/
echo 5. 代码检查: flake8 src/ tests/
echo.
echo 📚 查看文档：
echo - 用户手册: docs\user-manual.md
echo - 开发指南: docs\dev-guide.md
echo.
pause 