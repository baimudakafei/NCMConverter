@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo   NCM转MP3转换器 - 打包EXE
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 激活虚拟环境...
if not exist "venv" (
    echo 错误: 未找到虚拟环境，请先运行 install_dependencies.bat
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 激活虚拟环境失败！
    pause
    exit /b 1
)

echo.
echo [2/4] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装PyInstaller...
    pip install pyinstaller
)

echo.
echo [3/4] 开始打包...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "NCM转MP3转换器" ^
    --add-data "venv\Lib\site-packages\pydub\*;pydub" ^
    --add-data "venv\Lib\site-packages\mutagen\*;mutagen" ^
    --add-data "venv\Lib\site-packages\Crypto\*;Crypto" ^
    --hidden-import=pydub ^
    --hidden-import=mutagen ^
    --hidden-import=Crypto ^
    --hidden-import=Crypto.Cipher ^
    --hidden-import=Crypto.Util.Padding ^
    --clean ^
    ncm_converter.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 输出文件: dist\NCM转MP3转换器.exe
    echo.
    echo 测试方式:
    echo   1. 将 dist\NCM转MP3转换器.exe 复制到其他电脑
    echo   2. 双击运行（无需安装Python）
    echo.
) else (
    echo.
    echo ❌ 打包失败！
    echo.
)

echo ========================================
pause
