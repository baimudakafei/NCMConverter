import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import struct
import base64
import json
import binascii
import tempfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import threading
import uuid
import sys

# 声明：此程序仅用于学习，请勿应用于任何违法违规相关事项
DISCLAIMER = "此程序仅用于学习，请勿应用于任何违法违规相关事项"

class NCMConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("NCM Converter")
        self.root.geometry("850x780")
        self.root.resizable(True, True)
        self.root.configure(bg="#ffffff")
        
        self.file_list = []
        self.output_dir = ""
        self.cache_dir = ""
        self.session_temp_files = []
        self.session_suffix = ""
        
        self.is_paused = False
        self.is_stopped = False
        self.current_file_index = 0
        
        self.setup_ffmpeg_path()
        self.setup_ui()
    
    def setup_ffmpeg_path(self):
        if hasattr(sys, '_MEIPASS'):
            ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                os.environ['PATH'] = os.path.dirname(ffmpeg_path) + ';' + os.environ['PATH']
    
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TProgressbar', background='#6366f1', troughcolor='#f0f0f0')
        
        style.configure('Purple.TButton',
                       background='#6366f1',
                       foreground='#ffffff',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(24, 8))
        style.map('Purple.TButton',
                  background=[('active', '#4f46e5'), ('disabled', '#6366f1')],
                  foreground=[('active', '#ffffff'), ('disabled', '#b0b0b0')])
        
        header = tk.Frame(self.root, bg="#6366f1", padx=20, pady=12)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(header, text="🎵 NCM转换器", font=('Segoe UI', 18, 'bold'), bg="#6366f1", fg="#ffffff")
        title_label.pack(anchor=tk.W)
        
        disclaimer_label = tk.Label(header, text=DISCLAIMER, font=('Segoe UI', 9), bg="#6366f1", fg="#ffe4e6")
        disclaimer_label.pack(anchor=tk.W, pady=(4, 0))
        
        main_content = tk.Frame(self.root, bg="#f8fafc", padx=20, pady=15)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        file_section = tk.Frame(main_content, bg="#ffffff", relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground="#e2e8f0")
        file_section.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        section_header = tk.Frame(file_section, bg="#ffffff", padx=16, pady=10)
        section_header.pack(fill=tk.X)
        
        section_title = tk.Label(section_header, text="文件列表", font=('Segoe UI', 13, 'bold'), bg="#ffffff", fg="#1e293b")
        section_title.pack(anchor=tk.W)
        
        button_frame = tk.Frame(file_section, bg="#ffffff", padx=16)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_file_btn = self.create_btn(button_frame, "添加文件", self.add_files, is_primary=True)
        add_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        add_folder_btn = self.create_btn(button_frame, "添加文件夹", self.add_folder, is_primary=True)
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = self.create_btn(button_frame, "清空列表", self.clear_list, is_text=True)
        clear_btn.pack(side=tk.LEFT)
        
        listbox_frame = tk.Frame(file_section, bg="#f8fafc", padx=16)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, height=5,
                                  bg="#f8fafc", fg="#334155", font=('Segoe UI', 10),
                                  selectbackground="#e0e7ff", selectforeground="#6366f1",
                                  bd=0, relief=tk.FLAT, highlightthickness=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, bg="#e2e8f0", troughcolor="#f8fafc",
                                activebackground="#6366f1", bd=0, width=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        settings_section = tk.Frame(main_content, bg="#ffffff", relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground="#e2e8f0")
        settings_section.pack(fill=tk.X, pady=(0, 12))
        
        settings_header = tk.Frame(settings_section, bg="#ffffff", padx=16, pady=10)
        settings_header.pack(fill=tk.X)
        
        settings_title = tk.Label(settings_header, text="设置", font=('Segoe UI', 13, 'bold'), bg="#ffffff", fg="#1e293b")
        settings_title.pack(anchor=tk.W)
        
        settings_content = tk.Frame(settings_section, bg="#ffffff", padx=16)
        settings_content.pack(fill=tk.X, pady=(0, 12))
        
        output_frame = tk.Frame(settings_content, bg="#ffffff")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_label = tk.Label(output_frame, text="输出目录", font=('Segoe UI', 12), bg="#ffffff", fg="#475569")
        output_label.pack(side=tk.LEFT, padx=(0, 12))
        
        self.output_entry = self.create_entry(output_frame)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        output_browse = self.create_small_btn(output_frame, "浏览", self.select_output_dir)
        output_browse.pack(side=tk.LEFT)
        
        cache_frame = tk.Frame(settings_content, bg="#ffffff")
        cache_frame.pack(fill=tk.X, pady=(0, 10))
        
        cache_label = tk.Label(cache_frame, text="缓存目录", font=('Segoe UI', 11), bg="#ffffff", fg="#475569")
        cache_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cache_entry = self.create_entry(cache_frame)
        self.cache_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cache_browse = self.create_small_btn(cache_frame, "浏览", self.select_cache_dir)
        cache_browse.pack(side=tk.LEFT)
        
        format_frame = tk.Frame(settings_content, bg="#ffffff")
        format_frame.pack(fill=tk.X)
        
        self.convert_to_mp3_var = tk.BooleanVar(value=True)
        mp3_check = tk.Checkbutton(format_frame, text="强制转换为MP3格式", variable=self.convert_to_mp3_var,
                                   bg="#ffffff", fg="#334155", font=('Segoe UI', 11),
                                   selectcolor="#ffffff", activebackground="#ffffff",
                                   highlightthickness=0)
        mp3_check.pack(side=tk.LEFT)
        
        progress_frame = tk.Frame(main_content, bg="#ffffff", relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground="#e2e8f0")
        progress_frame.pack(fill=tk.X, pady=(0, 12))
        
        progress_content = tk.Frame(progress_frame, bg="#ffffff", padx=16, pady=12)
        progress_content.pack(fill=tk.X)
        
        current_row = tk.Frame(progress_content, bg="#ffffff")
        current_row.pack(fill=tk.X, pady=(0, 8))
        
        self.current_label = tk.Label(current_row, text="当前文件", font=('Segoe UI', 10), bg="#ffffff", fg="#475569", width=10)
        self.current_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.current_time_label = tk.Label(current_row, text="", font=('Segoe UI', 12, 'bold'), bg="#ffffff", fg="#6366f1")
        self.current_time_label.pack(side=tk.LEFT)
        
        overall_row = tk.Frame(progress_content, bg="#ffffff")
        overall_row.pack(fill=tk.X)
        
        overall_label = tk.Label(overall_row, text="整体进度", font=('Segoe UI', 10), bg="#ffffff", fg="#475569", width=10)
        overall_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.overall_canvas = tk.Canvas(overall_row, height=20, bg="#ffffff", bd=0, highlightthickness=0)
        self.overall_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        action_section = tk.Frame(main_content, bg="#ffffff", relief=tk.RAISED, bd=0, highlightthickness=1, highlightbackground="#e2e8f0")
        action_section.pack(fill=tk.X)
        
        action_header = tk.Frame(action_section, bg="#ffffff", padx=16, pady=10)
        action_header.pack(fill=tk.X)
        
        action_title = tk.Label(action_header, text="操作", font=('Segoe UI', 13, 'bold'), bg="#ffffff", fg="#1e293b")
        action_title.pack(anchor=tk.W)
        
        action_content = tk.Frame(action_section, bg="#ffffff", padx=16)
        action_content.pack(fill=tk.X, pady=(0, 12))
        
        action_frame = tk.Frame(action_content, bg="#ffffff")
        action_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(action_frame, text="开始转换", command=self.start_conversion, style='Purple.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_btn = ttk.Button(action_frame, text="暂停", command=self.toggle_pause, style='Purple.TButton')
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.pause_btn.config(state=tk.DISABLED)
        
        self.stop_btn = ttk.Button(action_frame, text="停止", command=self.stop_conversion, style='Purple.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 12))
        self.stop_btn.config(state=tk.DISABLED)
        
        clear_cache_btn = ttk.Button(action_frame, text="清空缓存", command=self.clear_cache, style='Purple.TButton')
        clear_cache_btn.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(progress_content, text="", font=('Segoe UI', 11),
                                     bg="#ffffff", fg="#6366f1")
        self.status_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.total_files = 0
        self.current_file_num = 0
        self.average_time = 0
        self.conversion_times = []
    
    def draw_progress_bar(self, canvas, current, total, label_text="", show_text=True):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width == 0:
            width = 100
        if height == 0:
            height = 20
        
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled_width = int(width * percentage / 100)
        
        canvas.create_rectangle(0, 0, width, height, fill="#ffffff", outline="#e2e8f0", width=1)
        
        canvas.create_rectangle(0, 0, filled_width, height, fill="#6366f1", outline="#6366f1", width=0)
        
        if show_text and label_text:
            text_color = "#ffffff" if percentage >= 50 else "#6366f1"
            canvas.create_text(width / 2, height / 2, text=label_text, fill=text_color, font=('Segoe UI', 9, 'bold'))
    
    def create_btn(self, parent, text, command, is_primary=False, is_secondary=False, is_text=False):
        if is_text:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#ffffff", fg="#6366f1", font=('Segoe UI', 11),
                           padx=14, pady=7, bd=0, relief=tk.FLAT,
                           activebackground="#f0f0ff", activeforeground="#6366f1",
                           highlightthickness=0)
        elif is_secondary:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#f1f5f9", fg="#475569", font=('Segoe UI', 11),
                           padx=14, pady=7, bd=0, relief=tk.FLAT,
                           activebackground="#e2e8f0", activeforeground="#334155",
                           highlightthickness=0)
        else:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#6366f1", fg="#ffffff", font=('Segoe UI', 11),
                           padx=14, pady=7, bd=0, relief=tk.FLAT,
                           activebackground="#4f46e5", activeforeground="#ffffff",
                           highlightthickness=0)
        return btn
    
    def create_small_btn(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                       bg="#f1f5f9", fg="#64748b", font=('Segoe UI', 10),
                       padx=20, pady=6, bd=0, relief=tk.FLAT,
                       activebackground="#e2e8f0", activeforeground="#475569",
                       highlightthickness=0)
        return btn
    
    def create_action_btn(self, parent, text, command, is_primary=False, is_secondary=False, is_danger=False):
        if is_danger:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#ef4444", fg="#ffffff", font=('Segoe UI', 12, 'bold'),
                           padx=32, pady=10, bd=0, relief=tk.FLAT,
                           activebackground="#dc2626", activeforeground="#ffffff",
                           highlightthickness=0)
        elif is_secondary:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#f59e0b", fg="#ffffff", font=('Segoe UI', 12, 'bold'),
                           padx=32, pady=10, bd=0, relief=tk.FLAT,
                           activebackground="#d97706", activeforeground="#ffffff",
                           highlightthickness=0)
        else:
            btn = tk.Button(parent, text=text, command=command,
                           bg="#6366f1", fg="#ffffff", font=('Segoe UI', 12, 'bold'),
                           padx=32, pady=10, bd=0, relief=tk.FLAT,
                           activebackground="#4f46e5", activeforeground="#ffffff",
                           highlightthickness=0)
        return btn
    
    def create_entry(self, parent):
        entry = tk.Entry(parent, bg="#f8fafc", fg="#334155", font=('Segoe UI', 11),
                         bd=0, relief=tk.FLAT, highlightthickness=1,
                         highlightbackground="#e2e8f0", width=45)
        return entry
    
    def detect_audio_format(self, data):
        if len(data) < 4:
            return None
        if data.startswith(b'ID3'):
            return 'mp3'
        if data.startswith(b'\xFF\xFB') or data.startswith(b'\xFF\xFA') or data.startswith(b'\xFF\xF3') or data.startswith(b'\xFF\xF2'):
            return 'mp3'
        if data.startswith(b'fLaC'):
            return 'flac'
        if len(data) > 8 and data[4:8] == b'ftyp':
            return 'm4a'
        if data.startswith(b'RIFF') and len(data) > 12 and data[8:12] == b'WAVE':
            return 'wav'
        if data.startswith(b'OggS'):
            return 'ogg'
        return None
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select NCM Files",
            filetypes=[("NCM Files", "*.ncm"), ("All Files", "*.*")]
        )
        for file in files:
            if file not in self.file_list:
                self.file_list.append(file)
                self.listbox.insert(tk.END, file)
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            for root_dir, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.ncm'):
                        full_path = os.path.join(root_dir, file)
                        if full_path not in self.file_list:
                            self.file_list.append(full_path)
                            self.listbox.insert(tk.END, full_path)
    
    def clear_list(self):
        self.file_list = []
        self.listbox.delete(0, tk.END)
    
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title="Select Output Directory")
        if self.output_dir:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_dir)
    
    def select_cache_dir(self):
        self.cache_dir = filedialog.askdirectory(title="Select Cache Directory")
        if self.cache_dir:
            self.cache_entry.delete(0, tk.END)
            self.cache_entry.insert(0, self.cache_dir)
    
    def clear_cache(self):
        cache_dir = self.cache_entry.get()
        if not cache_dir or not os.path.exists(cache_dir):
            messagebox.showinfo("Info", "Please select a valid cache directory first")
            return
        try:
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            messagebox.showinfo("Success", "Cache cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {str(e)}")
    
    def start_conversion(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "Please add NCM files first")
            return
        
        self.output_dir = self.output_entry.get()
        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select output directory")
            return
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.cache_dir = self.cache_entry.get()
        if not self.cache_dir:
            self.cache_dir = os.path.join(self.output_dir, "cache")
            self.cache_entry.delete(0, tk.END)
            self.cache_entry.insert(0, self.cache_dir)
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self.session_suffix = f"_{uuid.uuid4().hex[:8]}_ncm_temp"
        self.session_temp_files = []
        
        self.is_paused = False
        self.is_stopped = False
        self.current_file_index = 0
        self.total_files = len(self.file_list)
        self.current_file_num = 0
        
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="暂停")
        self.stop_btn.config(state=tk.NORMAL)
        
        self.root.after(100, lambda: self.draw_progress_bar(self.overall_canvas, 0, self.total_files, f"0/{self.total_files}"))
        self.root.after(100, lambda: self.current_time_label.config(text="准备开始"))
        
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def flac_to_mp3(self, flac_path, mp3_path):
        try:
            from pydub import AudioSegment
            if hasattr(sys, '_MEIPASS'):
                ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', 'ffmpeg.exe')
                AudioSegment.converter = ffmpeg_path
            
            audio = AudioSegment.from_file(flac_path, format='flac')
            audio.export(mp3_path, format='mp3', bitrate='320k')
            return True
        except Exception as e:
            print(f"FLAC to MP3 failed: {e}")
            return False
    
    def decrypt_ncm(self, ncm_file):
        core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
        meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
        
        try:
            with open(ncm_file, 'rb') as f:
                header = f.read(8)
                if header != b'CTENFDAM':
                    return None, None, None, None
                
                f.seek(2, 1)
                
                key_len_data = f.read(4)
                key_len = struct.unpack('<I', key_len_data)[0]
                key_data = f.read(key_len)
                
                key_data_array = bytearray(key_data)
                for i in range(len(key_data_array)):
                    key_data_array[i] ^= 0x64
                key_data = bytes(key_data_array)
                
                cipher = AES.new(core_key, AES.MODE_ECB)
                key_data = cipher.decrypt(key_data)
                
                try:
                    key_data = unpad(key_data, AES.block_size)
                except:
                    pass
                
                expected_prefix = b"neteasecloudmusic"
                if not key_data.startswith(expected_prefix):
                    return None, None, None, None
                
                rc4_key = key_data[len(expected_prefix):]
                
                key_box = bytearray(range(256))
                j = 0
                for i in range(256):
                    j = (j + key_box[i] + rc4_key[i % len(rc4_key)]) % 256
                    key_box[i], key_box[j] = key_box[j], key_box[i]
                
                meta_len_data = f.read(4)
                meta_len = struct.unpack('<I', meta_len_data)[0]
                meta_data = f.read(meta_len)
                
                meta_data_array = bytearray(meta_data)
                for i in range(len(meta_data_array)):
                    meta_data_array[i] ^= 0x63
                meta_data = bytes(meta_data_array)
                
                expected_prefix = b"163 key(Don't modify):"
                if not meta_data.startswith(expected_prefix):
                    return None, None, None, None
                
                meta_data = meta_data[len(expected_prefix):]
                meta_data = base64.b64decode(meta_data)
                
                cipher = AES.new(meta_key, AES.MODE_ECB)
                meta_data = cipher.decrypt(meta_data)
                
                try:
                    meta_data = unpad(meta_data, AES.block_size)
                except:
                    pass
                
                expected_prefix = b"music:"
                if not meta_data.startswith(expected_prefix):
                    return None, None, None, None
                
                meta_data = meta_data[len(expected_prefix):]
                
                try:
                    meta_str = meta_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        meta_str = meta_data.decode('gbk')
                    except UnicodeDecodeError:
                        meta_str = meta_data.decode('utf-8', errors='replace')
                
                meta = json.loads(meta_str)
                
                f.read(4)
                f.seek(5, 1)
                
                cover_len_data = f.read(4)
                cover_len = struct.unpack('<I', cover_len_data)[0]
                cover_data = f.read(cover_len)
                
                audio_data = f.read()
                
                decrypted_audio = bytearray()
                for i, byte in enumerate(audio_data):
                    j = (i + 1) % 256
                    a = key_box[j]
                    b = key_box[(a + j) % 256]
                    k = key_box[(a + b) % 256]
                    decrypted_audio.append(byte ^ k)
                
                return bytes(decrypted_audio), meta, cover_data, meta.get('format', 'mp3')
        
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None, None, None, None
    
    def convert_files(self):
        import time
        import threading
        
        success_count = 0
        self.current_progress = 0
        self.current_elapsed = 0
        self.time_update_running = True
        
        def update_time():
            while self.time_update_running:
                self.current_elapsed = int(time.time() - self.current_file_start_time)
                self.current_time_label.config(text=f"{self.current_elapsed}s")
                self.root.update_idletasks()
                time.sleep(0.1)
        
        for idx, ncm_file in enumerate(self.file_list):
            if self.is_stopped:
                break
            
            while self.is_paused:
                if self.is_stopped:
                    break
                time.sleep(0.1)
            
            if self.is_stopped:
                break
            
            try:
                self.time_update_running = True
                self.current_file_start_time = time.time()
                self.current_progress = 0
                self.current_elapsed = 0
                
                self.current_file_index = idx
                self.current_file_num = idx + 1
                filename = os.path.basename(ncm_file)
                
                self.status_label.config(text=f"正在转换: {filename}")
                self.draw_progress_bar(self.overall_canvas, idx, self.total_files, f"{idx}/{self.total_files}")
                self.current_time_label.config(text="0s")
                self.root.update_idletasks()
                
                time_thread = threading.Thread(target=update_time)
                time_thread.daemon = True
                time_thread.start()
                
                if not os.path.exists(ncm_file):
                    self.time_update_running = False
                    time.sleep(0.1)
                    continue
                
                self.current_progress = min(self.current_progress + 15, 100)
                time.sleep(0.01)
                
                decrypted_audio, meta, cover_data, declared_format = self.decrypt_ncm(ncm_file)
                
                if decrypted_audio is None or meta is None:
                    self.time_update_running = False
                    time.sleep(0.1)
                    continue
                
                self.current_progress = min(self.current_progress + 15, 100)
                time.sleep(0.01)
                
                detected_format = self.detect_audio_format(decrypted_audio)
                ext = detected_format if detected_format else declared_format
                if ext not in ['mp3', 'flac', 'm4a', 'wav', 'ogg']:
                    ext = 'mp3'
                
                self.current_progress = min(self.current_progress + 15, 100)
                time.sleep(0.01)
                
                original_name = os.path.splitext(os.path.basename(ncm_file))[0]
                
                if self.convert_to_mp3_var.get():
                    final_output_path = os.path.join(self.output_dir, f"{original_name}.mp3")
                else:
                    final_output_path = os.path.join(self.output_dir, f"{original_name}.{ext}")
                
                self.current_progress = min(self.current_progress + 15, 100)
                time.sleep(0.01)
                
                temp_path = None
                if self.convert_to_mp3_var.get() and ext != 'mp3':
                    self.current_progress = min(self.current_progress + 10, 100)
                    time.sleep(0.01)
                    self.root.update_idletasks()
                    
                    temp_filename = f"{uuid.uuid4().hex}{self.session_suffix}.{ext}"
                    temp_path = os.path.join(self.cache_dir, temp_filename)
                    self.session_temp_files.append(temp_path)
                    
                    with open(temp_path, 'wb') as temp_file:
                        temp_file.write(decrypted_audio)
                    
                    self.current_progress = min(self.current_progress + 10, 100)
                    
                    success = self.flac_to_mp3(temp_path, final_output_path)
                    
                    if not success:
                        with open(final_output_path, 'wb') as out_f:
                            out_f.write(decrypted_audio)
                else:
                    with open(final_output_path, 'wb') as out_f:
                        out_f.write(decrypted_audio)
                
                self.current_progress = min(self.current_progress + 10, 100)
                
                if cover_data and len(cover_data) > 0:
                    try:
                        import mutagen
                        from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
                        
                        try:
                            audio = ID3(final_output_path)
                        except mutagen.id3.ID3NoHeaderError:
                            audio = ID3()
                        
                        if 'musicName' in meta:
                            audio.add(TIT2(encoding=3, text=meta['musicName']))
                        if 'artist' in meta and meta['artist']:
                            artists = [a[0] for a in meta['artist']]
                            audio.add(TPE1(encoding=3, text='/'.join(artists)))
                        if 'album' in meta:
                            audio.add(TALB(encoding=3, text=meta['album']))
                        if cover_data:
                            if cover_data.startswith(b'\xFF\xD8'):
                                mime = 'image/jpeg'
                            elif cover_data.startswith(b'\x89PNG'):
                                mime = 'image/png'
                            else:
                                mime = 'image/jpeg'
                            audio.add(APIC(encoding=3, mime=mime, type=3, desc=u'Cover', data=cover_data))
                        
                        audio.save(final_output_path, v2_version=3)
                    except Exception as e:
                        print(f"Add tag failed: {e}")
                
                success_count += 1
                
                self.current_progress = 100
                
                file_end_time = time.time()
                file_time = file_end_time - self.current_file_start_time
                self.conversion_times.append(file_time)
                if len(self.conversion_times) > 0:
                    self.average_time = sum(self.conversion_times) / len(self.conversion_times)
                
                self.time_update_running = False
                time.sleep(0.1)
                
                elapsed_sec = int(file_time)
                self.current_time_label.config(text=f"{elapsed_sec}s")
                self.root.update_idletasks()
                
            except Exception as e:
                self.time_update_running = False
                print(f"Convert failed: {e}")
        
        self.conversion_complete(success_count)
    
    def conversion_complete(self, success_count):
        total_count = len(self.file_list)
        
        self.draw_progress_bar(self.overall_canvas, total_count, total_count, f"{total_count}/{total_count}")
        self.root.update_idletasks()
        
        if self.is_stopped:
            self.status_label.config(text=f"已停止！成功: {success_count}/{total_count}")
            messagebox.showinfo("已停止", f"转换已停止！\n成功: {success_count}/{total_count}\n输出目录: {self.output_dir}")
        else:
            self.status_label.config(text=f"已完成！成功: {success_count}/{total_count}")
            messagebox.showinfo("成功", f"转换完成！\n成功: {success_count}/{total_count}\n输出目录: {self.output_dir}")
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.cleanup_session_temp_files()
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="继续")
            self.status_label.config(text="已暂停")
        else:
            self.pause_btn.config(text="暂停")
            current_file = self.file_list[self.current_file_index] if self.current_file_index < len(self.file_list) else ""
            if current_file:
                self.status_label.config(text=f"正在转换: {os.path.basename(current_file)}")
    
    def stop_conversion(self):
        self.is_stopped = True
        self.is_paused = False
    
    def cleanup_session_temp_files(self):
        cleaned_count = 0
        for temp_file in self.session_temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    cleaned_count += 1
                except Exception as e:
                    print(f"Failed to remove temp file: {temp_file}, Error: {e}")
        
        self.session_temp_files = []
        self.session_suffix = ""
        
        if cleaned_count > 0:
            print(f"Cleaned {cleaned_count} temp files")


def main():
    root = tk.Tk()
    app = NCMConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
