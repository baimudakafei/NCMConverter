# NCM Converter

一个用于将 NCM 加密格式转换为普通音频格式的工具。

## 功能特性

- 🎵 **批量转换**: 支持添加单个文件或整个文件夹
- 📁 **自定义输出目录**: 可自由选择输出位置
- 🔄 **格式转换**: 支持将 FLAC 等格式转换为 MP3
- 📊 **进度显示**: 实时显示转换进度和耗时
- ⏸️ **暂停/继续**: 支持暂停和继续转换任务
- 🎨 **元数据保留**: 自动保留歌曲标题、艺术家、专辑信息和封面

## 安装依赖

```bash
pip install pycryptodome mutagen pydub
```

## 使用方法

### 方法一：直接运行 Python 脚本（需要 Python 环境）

```bash
python ncm_converter.py
```

### 方法二：生成独立 EXE 文件（推荐，无需 Python 环境）

1. 确保已安装 Python 3.x
2. 双击运行 `build.bat` 脚本
3. 等待脚本自动完成以下步骤：
   - 创建虚拟环境
   - 安装所有依赖
   - 下载 FFmpeg
   - 打包生成 EXE 文件
4. 生成的 `dist/NCMConverter.exe` 可在无 Python 环境的 Windows 上直接运行

### 操作步骤

1. 点击「添加文件」或「添加文件夹」选择 NCM 文件
2. 选择输出目录
3. 点击「开始转换」

## 技术实现

- **加密算法**: 使用 AES-ECB 和 RC4 算法解密 NCM 文件
- **音频处理**: 使用 pydub 和 ffmpeg 进行格式转换
- **元数据编辑**: 使用 mutagen 库写入 ID3 标签

## 支持的输出格式

- MP3 (默认)

## 注意事项

- 需要安装 ffmpeg 以支持 FLAC 转 MP3 功能
- 仅用于个人合法使用，请遵守相关版权规定

## License

MIT License