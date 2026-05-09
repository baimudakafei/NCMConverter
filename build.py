import os
import sys
import subprocess
import zipfile
import shutil
import urllib.request

def download_ffmpeg():
    ffmpeg_dir = "ffmpeg"
    ffmpeg_exe = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_exe):
        print("✅ FFmpeg已存在")
        return True
    
    print("📥 正在下载FFmpeg...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        urllib.request.urlretrieve(url, "ffmpeg.zip")
        print("✅ 下载完成")
        
        with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        for item in os.listdir("ffmpeg_temp"):
            src = os.path.join("ffmpeg_temp", item)
            if os.path.isdir(src):
                for root, dirs, files in os.walk(src):
                    rel_path = os.path.relpath(root, src)
                    dest_dir = os.path.join(ffmpeg_dir, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)
                        shutil.copy2(src_file, dest_file)
        
        shutil.rmtree("ffmpeg_temp")
        os.remove("ffmpeg.zip")
        print("✅ FFmpeg安装完成")
        return True
        
    except Exception as e:
        print(f"❌ 下载FFmpeg失败: {e}")
        return False

def build_exe():
    print("\n🔨 开始打包EXE...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=NCM转MP3转换器",
        "--add-data=ffmpeg/bin/ffmpeg.exe;ffmpeg/bin",
        "--add-data=ffmpeg/bin/ffplay.exe;ffmpeg/bin",
        "--add-data=ffmpeg/bin/ffprobe.exe;ffmpeg/bin",
        "--hidden-import=pydub",
        "--hidden-import=mutagen",
        "--hidden-import=Crypto",
        "--hidden-import=Crypto.Cipher",
        "--hidden-import=Crypto.Util.Padding",
        "--clean",
        "ncm_converter.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        print(f"\n📁 输出文件: dist/NCM转MP3转换器.exe")
        print("\n🚀 使用方法:")
        print("  1. 将 dist/NCM转MP3转换器.exe 复制到其他电脑")
        print("  2. 双击运行（无需安装Python）")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败:")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    print("=" * 50)
    print("    NCM转MP3转换器 - 打包工具")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if not download_ffmpeg():
        print("⚠️ 继续打包（可能需要系统已安装FFmpeg）")
    
    build_exe()
    
    print("\n" + "=" * 50)
    input("按回车键退出...")

if __name__ == "__main__":
    main()
