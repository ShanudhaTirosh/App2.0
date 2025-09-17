#!/usr/bin/env python3 """ Social Media Downloader Desktop Application




import tkinter as tk from tkinter import filedialog, messagebox import customtkinter as ctk import threading import json import os import urllib.parse import re from pathlib import Path import time import queue import requests from yt_dlp import YoutubeDL

Set appearance mode and color theme

ctk.set_appearance_mode("system") ctk.set_default_color_theme("blue")

class Config: def init(self): self.config_dir = Path.home() / ".social_downloader" self.config_file = self.config_dir / "config.json" self.config_dir.mkdir(exist_ok=True)

self.default_config = {
        "theme": "system",
        "download_path": str(Path.home() / "Downloads" / "SocialDownloader"),
        "default_video_quality": "720p",
        "default_audio_quality": "192kbps",
        "max_concurrent": 3,
        "naming_pattern": "{title}",
        "create_subfolders": True,
        "instant_download": False,
        "platforms": {
            "youtube": True,
            "instagram": True,
            "tiktok": True,
            "twitter": True,
            "facebook": True
        }
    }

    self.config = self.load_config()

def load_config(self):
    try:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            for key, value in self.default_config.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            return self.default_config.copy()
    except Exception:
        return self.default_config.copy()

def save_config(self):
    try:
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

class DownloadItem: def init(self, url, title="", platform="", quality="720p", format_type="mp4"): self.url = url self.title = title self.platform = platform self.quality = quality self.format_type = format_type self.status = "pending" self.progress = 0 self.file_path = "" self.error_message = "" self.speed = 0.0

def speed_mbps(self):
    return self.speed / (1024 * 1024)

class FileDownloadItem: def init(self, url, filename=None): self.url = url self.filename = filename or os.path.basename(urllib.parse.urlparse(url).path) or "download.bin" self.status = "pending" self.progress = 0 self.speed = 0.0 self.file_path = "" self.error_message = ""

def speed_mbps(self):
    return self.speed / (1024 * 1024)

class SocialMediaDownloader: def init(self): self.config = Config() self.download_queue = queue.Queue() self.file_download_queue = queue.Queue() self.active_downloads = {} self.active_file_downloads = {} self.download_items = [] self.file_items = []

self.root = ctk.CTk()
    self.root.title("Social Media Downloader")
    self.root.geometry("900x700")
    self.root.minsize(800, 600)

    ctk.set_appearance_mode(self.config.config["theme"])

    self.setup_ui()

    self.worker_thread = threading.Thread(target=self.download_worker, daemon=True)
    self.worker_thread.start()

    self.file_worker_thread = threading.Thread(target=self.file_download_worker, daemon=True)
    self.file_worker_thread.start()

    self.root.bind('<Control-v>', self.paste_url)

def setup_ui(self):
    self.root.grid_columnconfigure(0, weight=1)
    self.root.grid_rowconfigure(1, weight=1)

    # Header with settings button
    header_frame = ctk.CTkFrame(self.root, height=50)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(header_frame, text="🎬 Social Media Downloader", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=10)
    ctk.CTkButton(header_frame, text="⚙️ Settings", width=100, command=self.open_settings).grid(row=0, column=2, padx=10)

    # Tabs
    self.notebook = ctk.CTkTabview(self.root)
    self.notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    # Social downloader tab
    self.queue_tab = self.notebook.add("Video Downloader")
    url_frame = ctk.CTkFrame(self.queue_tab)
    url_frame.pack(fill="x", padx=20, pady=10)
    url_frame.grid_columnconfigure(0, weight=1)

    self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="Paste social media URL here…", height=40)
    self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    self.url_entry.bind('<Return>', lambda e: self.handle_url())
    ctk.CTkButton(url_frame, text="📋 Paste", command=self.paste_url).grid(row=0, column=1)

    self.queue_scroll = ctk.CTkScrollableFrame(self.queue_tab)
    self.queue_scroll.pack(fill="both", expand=True)

    # File downloader tab
    self.file_tab = self.notebook.add("File Downloader")
    file_frame = ctk.CTkFrame(self.file_tab)
    file_frame.pack(fill="x", padx=20, pady=10)
    file_frame.grid_columnconfigure(0, weight=1)

    self.file_url_entry = ctk.CTkEntry(file_frame, placeholder_text="Enter direct file URL…", height=40)
    self.file_url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    self.file_url_entry.bind('<Return>', lambda e: self.handle_file_url())
    ctk.CTkButton(file_frame, text="⬇️ Download", command=self.handle_file_url).grid(row=0, column=1)

    self.file_scroll = ctk.CTkScrollableFrame(self.file_tab)
    self.file_scroll.pack(fill="both", expand=True)

    # Status bar
    self.status_label = ctk.CTkLabel(self.root, text="Ready", font=ctk.CTkFont(size=11))
    self.status_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

def paste_url(self, event=None):
    try:
        clipboard_text = self.root.clipboard_get()
        if clipboard_text and self.is_valid_url(clipboard_text):
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, clipboard_text)
            self.handle_url()
    except Exception:
        self.set_status("Clipboard error")

def is_valid_url(self, url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def handle_url(self):
    url = self.url_entry.get().strip()
    if not url or not self.is_valid_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid URL")
        return

    item = DownloadItem(url=url, title=url, platform="Generic", quality=self.config.config['default_video_quality'], format_type="mp4")
    self.download_items.append(item)
    self.update_queue_display()
    self.download_queue.put(item)

def handle_file_url(self):
    url = self.file_url_entry.get().strip()
    if not url or not self.is_valid_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid file URL")
        return

    item = FileDownloadItem(url=url)
    self.file_items.append(item)
    self.update_file_display()
    self.file_download_queue.put(item)

def update_queue_display(self):
    for widget in self.queue_scroll.winfo_children():
        widget.destroy()
    if not self.download_items:
        ctk.CTkLabel(self.queue_scroll, text="📥 Queue is empty").pack(pady=10)
        return
    for item in self.download_items:
        frame = ctk.CTkFrame(self.queue_scroll)
        frame.pack(fill="x", padx=5, pady=5)
        text = f"{item.title} • {item.format_type.upper()} {item.quality}"
        if item.status == 'downloading':
            text += f" • {item.progress:.1f}% • {item.speed_mbps():.2f} MB/s"
        elif item.status == 'completed':
            text += " • ✅ Completed"
        elif item.status == 'error':
            text += " • ❌ Error"
        ctk.CTkLabel(frame, text=text).pack(side="left", padx=10)

def update_file_display(self):
    for widget in self.file_scroll.winfo_children():
        widget.destroy()
    if not self.file_items:
        ctk.CTkLabel(self.file_scroll, text="📂 No file downloads yet").pack(pady=10)
        return
    for item in self.file_items:
        frame = ctk.CTkFrame(self.file_scroll)
        frame.pack(fill="x", padx=5, pady=5)
        text = f"{item.filename}"
        if item.status == 'downloading':
            text += f" • {item.progress:.1f}% • {item.speed_mbps():.2f} MB/s"
        elif item.status == 'completed':
            text += " • ✅ Completed"
        elif item.status == 'error':
            text += " • ❌ Error"
        ctk.CTkLabel(frame, text=text).pack(side="left", padx=10)

def download_worker(self):
    while True:
        try:
            item = self.download_queue.get(timeout=1)
            if item.status in ('downloading', 'completed'):
                continue
            if len(self.active_downloads) >= self.config.config['max_concurrent']:
                self.download_queue.put(item)
                time.sleep(1)
                continue
            thread = threading.Thread(target=self.download_item, args=(item,), daemon=True)
            self.active_downloads[item] = thread
            thread.start()
        except queue.Empty:
            continue

def file_download_worker(self):
    while True:
        try:
            item = self.file_download_queue.get(timeout=1)
            if item.status in ('downloading', 'completed'):
                continue
            thread = threading.Thread(target=self.file_download_item, args=(item,), daemon=True)
            self.active_file_downloads[item] = thread
            thread.start()
        except queue.Empty:
            continue

def download_item(self, item: DownloadItem):
    try:
        item.status = 'downloading'
        self.root.after(0, self.update_queue_display)

        download_path = Path(self.config.config['download_path'])
        if self.config.config['create_subfolders']:
            download_path = download_path / item.platform.lower()
        download_path.mkdir(parents=True, exist_ok=True)

        safe_title = re.sub(r'[<>:"/\\|?*]', '', item.title)

        def hook(d):
            if d['status'] == 'downloading':
                pct = d.get('_percent_str', '0%').replace('%', '')
                try:
                    item.progress = float(pct)
                except:
                    pass
                item.speed = d.get('speed', 0.0)
                self.root.after(0, self.update_queue_display)
            elif d['status'] == 'finished':
                item.status = 'completed'
                item.progress = 100
                item.file_path = d.get('filename', '')
                self.root.after(0, self.update_queue_display)

        ydl_opts = {
            "outtmpl": str(download_path / f"{safe_title}.%(ext)s"),
            "progress_hooks": [hook],
            "quiet": True,
            "no_warnings": True,
            "concurrent_fragment_downloads": 8,
            "external_downloader": "aria2c",
            "external_downloader_args": {"aria2c": ["-x", "16", "-s", "16", "-k", "1M"]}
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([item.url])

    except Exception as e:
        item.status = 'error'
        item.error_message = str(e)
        self.root.after(0, self.update_queue_display)
    finally:
        if item in self.active_downloads:
            del self.active_downloads[item]

def file_download_item(self, item: FileDownloadItem):
    try:
        item.status = "downloading"
        self.root.after(0, self.update_file_display)

        download_path = Path(self.config.config['download_path']) / "Files"
        download_path.mkdir(parents=True, exist_ok=True)
        target = download_path / item.filename

        with requests.get(item.url, stream=True, timeout=15) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            start = time.time()

            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*64):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        item.progress = (downloaded / total) * 100
                    elapsed = max(time.time() - start, 1e-3)
                    item.speed = downloaded / elapsed
                    self.root.after(0, self.update_file_display)

        item.status = "completed"
        item.file_path = str(target)
        item.progress = 100
        self.root.after(0, self.update_file_display)
    except Exception as e:
        item.status = "error"
        item.error_message = str(e)
        self.root.after(0, self.update_file_display)
    finally:
        if item in self.active_file_downloads:
            del self.active_file_downloads[item]

def open_settings(self):
    settings = ctk.CTkToplevel(self.root)
    settings.title("Settings")
    settings.geometry("400x300")
    settings.transient(self.root)
    settings.grab_set()

    frame = ctk.CTkFrame(settings)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    instant_var = tk.BooleanVar(value=self.config.config['instant_download'])
    ctk.CTkCheckBox(frame, text="Enable Instant Download", variable=instant_var).pack(anchor="w", pady=10)

    def save():
        self.config.config['instant_download'] = instant_var.get()
        self.config.save_config()
        self.set_status("Settings saved")
        settings.destroy()

    ctk.CTkButton(frame, text="Save", command=save).pack(pady=20)

def set_status(self, message):
    self.status_label.configure(text=message)
    self.root.after(5000, lambda: self.status_label.configure(text="Ready"))

def run(self):
    self.root.mainloop()

if name == "main": try: app = SocialMediaDownloader() app.run() except KeyboardInterrupt: print("Interrupted")

