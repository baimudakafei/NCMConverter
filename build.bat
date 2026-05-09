@echo off
chcp 65001 >nul
echo ==============================================
echo           NCM Converter 打包脚本
echo ==============================================
echo.

set "VENV_DIR=venv"
set "DIST_DIR=dist"
set "BUILD_DIR=build"
set "APP_NAME=NCMConverter"
set "MAIN_SCRIPT=ncm_converter.py"

echo [1/5] 检查并创建虚拟环境...
if not exist "%VENV_DIR%" (
    echo 正在创建虚拟环境...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo 错误: 无法创建虚拟环境，请确保已安装 Python
        pause
        exit /b 1
    )
)

echo [2/5] 激活虚拟环境并安装依赖...
call "%VENV_DIR%\Scripts\activate.bat"

echo 正在安装依赖...
pip install pycryptodome mutagen pydub pyinstaller
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo [3/5] 检查并下载 FFmpeg...
set "FFMPEG_DIR=ffmpeg"
if not exist "%FFMPEG_DIR%" (
    echo 正在下载 FFmpeg...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    if %errorlevel% neq 0 (
        echo 错误: 下载 FFmpeg 失败
        pause
        exit /b 1
    )

    echo 正在解压 FFmpeg...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force"

    for /d %%i in (ffmpeg_temp\*) do (
        move "%%i" "%FFMPEG_DIR%"
    )
    rmdir /s /q ffmpeg_temp
    del ffmpeg.zip
)

echo [4/5] 使用 PyInstaller 打包...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%APP_NAME%.spec" del "%APP_NAME%.spec"

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "%APP_NAME%" ^
    --add-data "ffmpeg/bin/ffmpeg.exe;ffmpeg/bin" ^
    --add-data "ffmpeg/bin/ffplay.exe;ffmpeg/bin" ^
    --add-data "ffmpeg/bin/ffprobe.exe;ffmpeg/bin" ^
    --icon=NONE ^
    "%MAIN_SCRIPT%"

if %errorlevel% neq 0 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo [5/5] 复制额外文件到输出目录...
copy "README.md" "%DIST_DIR%\" 2>nul
copy "LICENSE" "%DIST_DIR%\" 2>nul

echo.
echo ==============================================
echo 打包完成!
echo ==============================================
echo 输出文件位于: %DIST_DIR%\%APP_NAME%.exe
echo.
echo 使用说明:
echo 1. 双击 %APP_NAME%.exe 即可运行
echo 2. 无需安装 Python 或其他依赖
echo.
pause