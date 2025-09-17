#!/usr/bin/env python3
"""
Enhanced Social Media Downloader Desktop Application
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading
import json
import os
import urllib.parse
import re
from pathlib import Path
import time
import queue
import requests
from yt_dlp import YoutubeDL

# Set appearance mode and color theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".social_downloader"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
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

class DownloadItem:
    def __init__(self, url, title="", platform="", quality="720p", format_type="mp4"):
        self.url = url
        self.title = title
        self.platform = platform
        self.quality = quality
        self.format_type = format_type
        self.status = "pending"
        self.progress = 0
        self.file_path = ""
        self.error_message = ""
        self.speed = 0.0
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start unpaused
        self.cancel_event = threading.Event()
        self.download_thread = None
        self.ydl_instance = None
        self.file_size = 0
        self.downloaded_bytes = 0
        
    def speed_mbps(self):
        return self.speed / (1024 * 1024) if self.speed else 0.0
    
    def pause(self):
        self.pause_event.clear()
        self.status = "paused"
    
    def resume(self):
        self.pause_event.set()
        if self.status == "paused":
            self.status = "downloading"
    
    def cancel(self):
        self.cancel_event.set()
        self.pause_event.set()  # Unblock if paused
        self.status = "cancelled"

class FileDownloadItem:
    def __init__(self, url, filename=None):
        self.url = url
        self.filename = filename or os.path.basename(urllib.parse.urlparse(url).path) or "download.bin"
        self.status = "pending"
        self.progress = 0
        self.speed = 0.0
        self.file_path = ""
        self.error_message = ""
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.cancel_event = threading.Event()
    
    def speed_mbps(self):
        return self.speed / (1024 * 1024) if self.speed else 0.0
    
    def pause(self):
        self.pause_event.clear()
        self.status = "paused"
    
    def resume(self):
        self.pause_event.set()
        if self.status == "paused":
            self.status = "downloading"
    
    def cancel(self):
        self.cancel_event.set()
        self.pause_event.set()
        self.status = "cancelled"

class SocialMediaDownloader:
    def __init__(self):
        self.config = Config()
        self.download_queue = queue.Queue()
        self.file_download_queue = queue.Queue()
        self.active_downloads = {}
        self.active_file_downloads = {}
        self.download_items = []
        self.file_items = []
        self.item_widgets = {}  # Track widgets for each download item
        self.file_item_widgets = {}
        
        self.root = ctk.CTk()
        self.root.title("Enhanced Social Media Downloader")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # Set window icon (if you have one)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        ctk.set_appearance_mode(self.config.config["theme"])
        
        self.setup_ui()
        
        self.worker_thread = threading.Thread(target=self.download_worker, daemon=True)
        self.worker_thread.start()
        
        self.file_worker_thread = threading.Thread(target=self.file_download_worker, daemon=True)
        self.file_worker_thread.start()
        
        # Periodic UI updates
        self.update_ui_periodically()
        
        self.root.bind('<Control-v>', self.paste_url)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Enhanced header with gradient-like appearance
        header_frame = ctk.CTkFrame(self.root, height=70, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        # App title with icon
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        ctk.CTkLabel(title_frame, text="🎬", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(title_frame, text="Social Media Downloader", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(title_frame, text="Download videos, audio & files with ease", 
                                    font=ctk.CTkFont(size=12), text_color=("gray60", "gray40"))
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Action buttons in header
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)
        
        ctk.CTkButton(button_frame, text="⚙️ Settings", width=120, height=35,
                     command=self.open_settings, corner_radius=8).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(button_frame, text="📂 Open Folder", width=120, height=35,
                     command=self.open_download_folder, corner_radius=8).pack(side="right")
        
        # Enhanced tabs
        self.notebook = ctk.CTkTabview(self.root, corner_radius=15, border_width=2)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        # Video Downloader Tab
        self.setup_video_tab()
        
        # File Downloader Tab
        self.setup_file_tab()
        
        # Enhanced status bar
        status_frame = ctk.CTkFrame(self.root, height=40, corner_radius=10)
        status_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(status_frame, text="🟢 Ready", 
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       anchor="w")
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        # Download stats
        self.stats_label = ctk.CTkLabel(status_frame, text="Downloads: 0 • Active: 0", 
                                      font=ctk.CTkFont(size=11),
                                      text_color=("gray60", "gray40"))
        self.stats_label.grid(row=0, column=1, sticky="e", padx=15, pady=10)
    
    def setup_video_tab(self):
        self.queue_tab = self.notebook.add("📺 Video Downloader")
        
        # URL input section
        input_frame = ctk.CTkFrame(self.queue_tab, corner_radius=12)
        input_frame.pack(fill="x", padx=20, pady=(20, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(input_frame, text="🔗", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=(15, 10), pady=15)
        
        self.url_entry = ctk.CTkEntry(input_frame, placeholder_text="Paste social media URL here (YouTube, Instagram, TikTok, Twitter, etc.)...", 
                                    height=45, corner_radius=8, font=ctk.CTkFont(size=12))
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        self.url_entry.bind('<Return>', lambda e: self.handle_url())
        
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=(0, 15), pady=15)
        
        ctk.CTkButton(button_frame, text="📋 Paste", width=80, height=35,
                     command=self.paste_url, corner_radius=6).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(button_frame, text="⬇️ Download", width=100, height=35,
                     command=self.handle_url, corner_radius=6,
                     fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")).pack(side="left")
        
        # Queue management
        queue_header = ctk.CTkFrame(self.queue_tab, height=50, corner_radius=10)
        queue_header.pack(fill="x", padx=20, pady=(10, 0))
        queue_header.grid_columnconfigure(0, weight=1)
        queue_header.grid_propagate(False)
        
        ctk.CTkLabel(queue_header, text="📥 Download Queue", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Queue controls
        control_frame = ctk.CTkFrame(queue_header, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)
        
        ctk.CTkButton(control_frame, text="⏸️ Pause All", width=100, height=30,
                     command=self.pause_all_downloads, corner_radius=6).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(control_frame, text="▶️ Resume All", width=100, height=30,
                     command=self.resume_all_downloads, corner_radius=6).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(control_frame, text="🗑️ Clear", width=80, height=30,
                     command=self.clear_completed_downloads, corner_radius=6,
                     fg_color=("red", "darkred"), hover_color=("darkred", "red")).pack(side="left")
        
        # Downloads list
        self.queue_scroll = ctk.CTkScrollableFrame(self.queue_tab, corner_radius=12)
        self.queue_scroll.pack(fill="both", expand=True, padx=20, pady=10)
    
    def setup_file_tab(self):
        self.file_tab = self.notebook.add("📁 File Downloader")
        
        # File URL input
        file_input_frame = ctk.CTkFrame(self.file_tab, corner_radius=12)
        file_input_frame.pack(fill="x", padx=20, pady=(20, 10))
        file_input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_input_frame, text="📎", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=(15, 10), pady=15)
        
        self.file_url_entry = ctk.CTkEntry(file_input_frame, placeholder_text="Enter direct file URL (documents, images, archives, etc.)...", 
                                         height=45, corner_radius=8, font=ctk.CTkFont(size=12))
        self.file_url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        self.file_url_entry.bind('<Return>', lambda e: self.handle_file_url())
        
        ctk.CTkButton(file_input_frame, text="⬇️ Download", width=120, height=35,
                     command=self.handle_file_url, corner_radius=6,
                     fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")).grid(row=0, column=2, padx=(0, 15), pady=15)
        
        # File queue header
        file_header = ctk.CTkFrame(self.file_tab, height=50, corner_radius=10)
        file_header.pack(fill="x", padx=20, pady=(10, 0))
        file_header.grid_columnconfigure(0, weight=1)
        file_header.grid_propagate(False)
        
        ctk.CTkLabel(file_header, text="📂 File Downloads", 
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # File downloads list
        self.file_scroll = ctk.CTkScrollableFrame(self.file_tab, corner_radius=12)
        self.file_scroll.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_download_item_widget(self, item: DownloadItem):
        """Create an enhanced widget for a download item"""
        frame = ctk.CTkFrame(self.queue_scroll, corner_radius=10, border_width=1)
        frame.pack(fill="x", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        
        # Left side - Platform icon and info
        info_frame = ctk.CTkFrame(frame, width=60, corner_radius=8)
        info_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)
        info_frame.grid_propagate(False)
        
        # Platform emoji/icon
        platform_icons = {
            "youtube": "📺", "instagram": "📸", "tiktok": "🎵", 
            "twitter": "🐦", "facebook": "📘", "generic": "🌐"
        }
        icon = platform_icons.get(item.platform.lower(), "🌐")
        
        ctk.CTkLabel(info_frame, text=icon, font=ctk.CTkFont(size=24)).pack(pady=(10, 0))
        ctk.CTkLabel(info_frame, text=item.platform, font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=("gray60", "gray40")).pack(pady=(0, 10))
        
        # Center - Title and progress
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_text = item.title if item.title and item.title != item.url else item.url[:60] + "..."
        title_label = ctk.CTkLabel(content_frame, text=title_text, font=ctk.CTkFont(size=13, weight="bold"),
                                 anchor="w", justify="left")
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Status and progress info
        status_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(status_frame, height=8, corner_radius=4)
        progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        progress_bar.set(item.progress / 100)
        
        # Status text
        status_text = self.get_status_text(item)
        status_label = ctk.CTkLabel(status_frame, text=status_text, font=ctk.CTkFont(size=11),
                                  text_color=("gray60", "gray40"), anchor="w")
        status_label.grid(row=1, column=0, sticky="w")
        
        # Right side - Control buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent", width=150)
        button_frame.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(0, 10), pady=10)
        
        # Create control buttons based on status
        self.create_control_buttons(button_frame, item)
        
        # Store references to widgets for updates
        self.item_widgets[item] = {
            'frame': frame,
            'title_label': title_label,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'button_frame': button_frame
        }
        
        return frame
    
    def create_control_buttons(self, parent_frame, item):
        """Create control buttons based on item status"""
        # Clear existing buttons
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        if item.status == "pending":
            ctk.CTkButton(parent_frame, text="⏳ Queued", width=120, height=30,
                         state="disabled", corner_radius=6).pack(pady=2)
        elif item.status == "downloading":
            ctk.CTkButton(parent_frame, text="⏸️ Pause", width=120, height=30,
                         command=lambda: self.pause_download(item), corner_radius=6).pack(pady=2)
            ctk.CTkButton(parent_frame, text="❌ Cancel", width=120, height=30,
                         command=lambda: self.cancel_download(item), corner_radius=6,
                         fg_color=("red", "darkred"), hover_color=("darkred", "red")).pack(pady=2)
        elif item.status == "paused":
            ctk.CTkButton(parent_frame, text="▶️ Resume", width=120, height=30,
                         command=lambda: self.resume_download(item), corner_radius=6,
                         fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")).pack(pady=2)
            ctk.CTkButton(parent_frame, text="❌ Cancel", width=120, height=30,
                         command=lambda: self.cancel_download(item), corner_radius=6,
                         fg_color=("red", "darkred"), hover_color=("darkred", "red")).pack(pady=2)
        elif item.status == "completed":
            ctk.CTkButton(parent_frame, text="📂 Open", width=120, height=30,
                         command=lambda: self.open_file_location(item), corner_radius=6).pack(pady=2)
            ctk.CTkButton(parent_frame, text="🗑️ Remove", width=120, height=30,
                         command=lambda: self.remove_download(item), corner_radius=6,
                         fg_color=("gray", "gray30"), hover_color=("gray30", "gray")).pack(pady=2)
        elif item.status == "error":
            ctk.CTkButton(parent_frame, text="🔄 Retry", width=120, height=30,
                         command=lambda: self.retry_download(item), corner_radius=6,
                         fg_color=("orange", "darkorange"), hover_color=("darkorange", "orange")).pack(pady=2)
            ctk.CTkButton(parent_frame, text="🗑️ Remove", width=120, height=30,
                         command=lambda: self.remove_download(item), corner_radius=6,
                         fg_color=("gray", "gray30"), hover_color=("gray30", "gray")).pack(pady=2)
        elif item.status == "cancelled":
            ctk.CTkButton(parent_frame, text="🔄 Retry", width=120, height=30,
                         command=lambda: self.retry_download(item), corner_radius=6,
                         fg_color=("orange", "darkorange"), hover_color=("darkorange", "orange")).pack(pady=2)
            ctk.CTkButton(parent_frame, text="🗑️ Remove", width=120, height=30,
                         command=lambda: self.remove_download(item), corner_radius=6,
                         fg_color=("gray", "gray30"), hover_color=("gray30", "gray")).pack(pady=2)
    
    def get_status_text(self, item):
        """Get status text for an item"""
        if item.status == "pending":
            return f"⏳ Queued • {item.format_type.upper()} {item.quality}"
        elif item.status == "downloading":
            return f"⬇️ {item.progress:.1f}% • {item.speed_mbps():.2f} MB/s • {item.format_type.upper()} {item.quality}"
        elif item.status == "paused":
            return f"⏸️ Paused at {item.progress:.1f}% • {item.format_type.upper()} {item.quality}"
        elif item.status == "completed":
            return f"✅ Completed • {item.format_type.upper()} {item.quality}"
        elif item.status == "error":
            return f"❌ Error: {item.error_message[:50]}..."
        elif item.status == "cancelled":
            return f"⭕ Cancelled • {item.format_type.upper()} {item.quality}"
        return "Unknown status"
    
    def pause_download(self, item):
        """Pause a specific download"""
        item.pause()
        self.update_item_widget(item)
    
    def resume_download(self, item):
        """Resume a specific download"""
        item.resume()
        if item not in self.active_downloads and item.status != "completed":
            self.download_queue.put(item)
        self.update_item_widget(item)
    
    def cancel_download(self, item):
        """Cancel a specific download"""
        item.cancel()
        if item in self.active_downloads:
            del self.active_downloads[item]
        self.update_item_widget(item)
    
    def retry_download(self, item):
        """Retry a failed/cancelled download"""
        item.status = "pending"
        item.progress = 0
        item.error_message = ""
        item.cancel_event.clear()
        item.pause_event.set()
        self.download_queue.put(item)
        self.update_item_widget(item)
    
    def remove_download(self, item):
        """Remove download from list"""
        if item in self.download_items:
            self.download_items.remove(item)
        if item in self.item_widgets:
            self.item_widgets[item]['frame'].destroy()
            del self.item_widgets[item]
        if item in self.active_downloads:
            item.cancel()
            del self.active_downloads[item]
        self.update_empty_state()
    
    def pause_all_downloads(self):
        """Pause all active downloads"""
        for item in self.download_items:
            if item.status == "downloading":
                self.pause_download(item)
    
    def resume_all_downloads(self):
        """Resume all paused downloads"""
        for item in self.download_items:
            if item.status == "paused":
                self.resume_download(item)
    
    def clear_completed_downloads(self):
        """Clear all completed downloads from the list"""
        completed_items = [item for item in self.download_items if item.status == "completed"]
        for item in completed_items:
            self.remove_download(item)
    
    def open_file_location(self, item):
        """Open file location in file explorer"""
        if item.file_path and os.path.exists(item.file_path):
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", "/select,", item.file_path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", "-R", item.file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", os.path.dirname(item.file_path)])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file location: {e}")
        else:
            messagebox.showwarning("Warning", "File not found or path not available")
    
    def open_download_folder(self):
        """Open the main download folder"""
        download_path = Path(self.config.config['download_path'])
        if download_path.exists():
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", str(download_path)])
                elif platform.system() == "Darwin":
                    subprocess.run(["open", str(download_path)])
                else:
                    subprocess.run(["xdg-open", str(download_path)])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open download folder: {e}")
        else:
            messagebox.showwarning("Warning", "Download folder does not exist")
    
    def update_item_widget(self, item):
        """Update the widget for a specific item"""
        if item in self.item_widgets:
            widgets = self.item_widgets[item]
            
            # Update progress bar
            widgets['progress_bar'].set(item.progress / 100)
            
            # Update status text
            status_text = self.get_status_text(item)
            widgets['status_label'].configure(text=status_text)
            
            # Update title if it changed
            if item.title and item.title != item.url:
                title_text = item.title[:60] + ("..." if len(item.title) > 60 else "")
                widgets['title_label'].configure(text=title_text)
            
            # Update control buttons
            self.create_control_buttons(widgets['button_frame'], item)
    
    def update_queue_display(self):
        """Update the entire queue display"""
        # Remove widgets for items that are no longer in the list
        for item in list(self.item_widgets.keys()):
            if item not in self.download_items:
                self.item_widgets[item]['frame'].destroy()
                del self.item_widgets[item]
        
        # Create widgets for new items or update existing ones
        for item in self.download_items:
            if item not in self.item_widgets:
                self.create_download_item_widget(item)
            else:
                self.update_item_widget(item)
        
        self.update_empty_state()
    
    def update_empty_state(self):
        """Show empty state message if no downloads"""
        if not self.download_items:
            # Clear any existing widgets
            for widget in self.queue_scroll.winfo_children():
                if widget not in [w['frame'] for w in self.item_widgets.values()]:
                    widget.destroy()
            
            empty_frame = ctk.CTkFrame(self.queue_scroll, corner_radius=15, height=200)
            empty_frame.pack(fill="x", padx=20, pady=50)
            empty_frame.pack_propagate(False)
            
            ctk.CTkLabel(empty_frame, text="📥", font=ctk.CTkFont(size=48)).pack(pady=(40, 10))
            ctk.CTkLabel(empty_frame, text="No downloads yet", 
                        font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 5))
            ctk.CTkLabel(empty_frame, text="Paste a URL above to start downloading", 
                        font=ctk.CTkFont(size=12), text_color=("gray60", "gray40")).pack()
    
    def update_file_display(self):
        """Update file downloads display with enhanced UI"""
        for widget in self.file_scroll.winfo_children():
            widget.destroy()
        
        if not self.file_items:
            empty_frame = ctk.CTkFrame(self.file_scroll, corner_radius=15, height=200)
            empty_frame.pack(fill="x", padx=20, pady=50)
            empty_frame.pack_propagate(False)
            
            ctk.CTkLabel(empty_frame, text="📁", font=ctk.CTkFont(size=48)).pack(pady=(40, 10))
            ctk.CTkLabel(empty_frame, text="No file downloads yet", 
                        font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 5))
            ctk.CTkLabel(empty_frame, text="Enter a direct file URL above to start downloading", 
                        font=ctk.CTkFont(size=12), text_color=("gray60", "gray40")).pack()
            return
        
        for item in self.file_items:
            frame = ctk.CTkFrame(self.file_scroll, corner_radius=10, border_width=1)
            frame.pack(fill="x", padx=5, pady=5)
            frame.grid_columnconfigure(1, weight=1)
            
            # File icon
            icon_frame = ctk.CTkFrame(frame, width=60, corner_radius=8)
            icon_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)
            icon_frame.grid_propagate(False)
            
            # Get file extension for appropriate icon
            file_ext = os.path.splitext(item.filename)[1].lower()
            file_icons = {
                '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📝',
                '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
                '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬',
                '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵',
                '.zip': '🗜️', '.rar': '🗜️', '.7z': '🗜️',
                '.exe': '⚙️', '.msi': '⚙️'
            }
            icon = file_icons.get(file_ext, '📎')
            
            ctk.CTkLabel(icon_frame, text=icon, font=ctk.CTkFont(size=24)).pack(pady=(15, 5))
            ctk.CTkLabel(icon_frame, text=file_ext.upper() or 'FILE', 
                        font=ctk.CTkFont(size=9, weight="bold"),
                        text_color=("gray60", "gray40")).pack()
            
            # Content
            content_frame = ctk.CTkFrame(frame, fg_color="transparent")
            content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
            content_frame.grid_columnconfigure(0, weight=1)
            
            # Filename
            filename_text = item.filename if len(item.filename) <= 50 else item.filename[:47] + "..."
            ctk.CTkLabel(content_frame, text=filename_text, font=ctk.CTkFont(size=13, weight="bold"),
                        anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 5))
            
            # Progress
            progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            progress_frame.grid(row=1, column=0, sticky="ew")
            progress_frame.grid_columnconfigure(0, weight=1)
            
            if item.status == "downloading" or item.progress > 0:
                progress_bar = ctk.CTkProgressBar(progress_frame, height=8, corner_radius=4)
                progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
                progress_bar.set(item.progress / 100)
            
            # Status
            status_text = f"{item.status.title()}"
            if item.status == "downloading":
                status_text = f"⬇️ {item.progress:.1f}% • {item.speed_mbps():.2f} MB/s"
            elif item.status == "completed":
                status_text = "✅ Download completed"
            elif item.status == "error":
                status_text = f"❌ Error: {item.error_message[:30]}..."
            elif item.status == "paused":
                status_text = f"⏸️ Paused at {item.progress:.1f}%"
            
            ctk.CTkLabel(progress_frame, text=status_text, font=ctk.CTkFont(size=11),
                        text_color=("gray60", "gray40"), anchor="w").grid(row=1, column=0, sticky="w")
            
            # Control buttons for file downloads
            button_frame = ctk.CTkFrame(frame, fg_color="transparent", width=120)
            button_frame.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(0, 10), pady=10)
            
            if item.status == "downloading":
                ctk.CTkButton(button_frame, text="⏸️ Pause", width=100, height=30,
                             command=lambda i=item: self.pause_file_download(i), corner_radius=6).pack(pady=2)
                ctk.CTkButton(button_frame, text="❌ Cancel", width=100, height=30,
                             command=lambda i=item: self.cancel_file_download(i), corner_radius=6,
                             fg_color=("red", "darkred"), hover_color=("darkred", "red")).pack(pady=2)
            elif item.status == "paused":
                ctk.CTkButton(button_frame, text="▶️ Resume", width=100, height=30,
                             command=lambda i=item: self.resume_file_download(i), corner_radius=6,
                             fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")).pack(pady=2)
            elif item.status == "completed":
                ctk.CTkButton(button_frame, text="📂 Open", width=100, height=30,
                             command=lambda i=item: self.open_file_location_file(i), corner_radius=6).pack(pady=2)
                ctk.CTkButton(button_frame, text="🗑️ Remove", width=100, height=30,
                             command=lambda i=item: self.remove_file_download(i), corner_radius=6,
                             fg_color=("gray", "gray30"), hover_color=("gray30", "gray")).pack(pady=2)
            elif item.status == "error":
                ctk.CTkButton(button_frame, text="🔄 Retry", width=100, height=30,
                             command=lambda i=item: self.retry_file_download(i), corner_radius=6,
                             fg_color=("orange", "darkorange"), hover_color=("darkorange", "orange")).pack(pady=2)
    
    def pause_file_download(self, item):
        """Pause a file download"""
        item.pause()
        self.update_file_display()
    
    def resume_file_download(self, item):
        """Resume a file download"""
        item.resume()
        if item not in self.active_file_downloads:
            self.file_download_queue.put(item)
        self.update_file_display()
    
    def cancel_file_download(self, item):
        """Cancel a file download"""
        item.cancel()
        if item in self.active_file_downloads:
            del self.active_file_downloads[item]
        self.update_file_display()
    
    def retry_file_download(self, item):
        """Retry a failed file download"""
        item.status = "pending"
        item.progress = 0
        item.error_message = ""
        item.cancel_event.clear()
        item.pause_event.set()
        self.file_download_queue.put(item)
        self.update_file_display()
    
    def remove_file_download(self, item):
        """Remove file download from list"""
        if item in self.file_items:
            self.file_items.remove(item)
        if item in self.active_file_downloads:
            item.cancel()
            del self.active_file_downloads[item]
        self.update_file_display()
    
    def open_file_location_file(self, item):
        """Open file location for file download"""
        self.open_file_location(item)
    
    def paste_url(self, event=None):
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text and self.is_valid_url(clipboard_text):
                current_tab = self.notebook.get()
                if "Video" in current_tab:
                    self.url_entry.delete(0, 'end')
                    self.url_entry.insert(0, clipboard_text)
                else:
                    self.file_url_entry.delete(0, 'end')
                    self.file_url_entry.insert(0, clipboard_text)
                
                if self.config.config.get('instant_download', False):
                    if "Video" in current_tab:
                        self.handle_url()
                    else:
                        self.handle_file_url()
                self.set_status("✅ URL pasted from clipboard")
        except Exception:
            self.set_status("❌ Clipboard error")
    
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
        
        # Clear the URL entry
        self.url_entry.delete(0, 'end')
        
        item = DownloadItem(
            url=url, 
            title=url, 
            platform="Generic", 
            quality=self.config.config['default_video_quality'], 
            format_type="mp4"
        )
        self.download_items.append(item)
        self.update_queue_display()
        self.download_queue.put(item)
        self.set_status(f"✅ Added to download queue")
    
    def handle_file_url(self):
        url = self.file_url_entry.get().strip()
        if not url or not self.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Please enter a valid file URL")
            return
        
        # Clear the URL entry
        self.file_url_entry.delete(0, 'end')
        
        item = FileDownloadItem(url=url)
        self.file_items.append(item)
        self.update_file_display()
        self.file_download_queue.put(item)
        self.set_status(f"✅ Added file download: {item.filename}")
    
    def download_worker(self):
        while True:
            try:
                item = self.download_queue.get(timeout=1)
                if item.status in ('downloading', 'completed') or item.cancel_event.is_set():
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
                if item.status in ('downloading', 'completed') or item.cancel_event.is_set():
                    continue
                
                thread = threading.Thread(target=self.file_download_item, args=(item,), daemon=True)
                self.active_file_downloads[item] = thread
                thread.start()
            except queue.Empty:
                continue
    
    def download_item(self, item: DownloadItem):
        try:
            if item.cancel_event.is_set():
                return
                
            item.status = 'downloading'
            self.root.after(0, lambda: self.update_item_widget(item))
            
            download_path = Path(self.config.config['download_path'])
            if self.config.config['create_subfolders']:
                download_path = download_path / item.platform.lower()
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Get video info first
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                try:
                    info = ydl.extract_info(item.url, download=False)
                    item.title = info.get('title', 'Unknown')[:100]
                    item.platform = info.get('extractor_key', 'Generic')
                    self.root.after(0, lambda: self.update_item_widget(item))
                except Exception as e:
                    if item.cancel_event.is_set():
                        return
            
            safe_title = re.sub(r'[<>:"/\\|?*]', '', item.title)
            if not safe_title:
                safe_title = "download"
            
            def hook(d):
                if item.cancel_event.is_set():
                    return
                
                if d['status'] == 'downloading':
                    # Handle pause/resume
                    if not item.pause_event.is_set():
                        item.status = "paused"
                        self.root.after(0, lambda: self.update_item_widget(item))
                        item.pause_event.wait()  # Block until resumed
                        if item.cancel_event.is_set():
                            return
                        item.status = "downloading"
                        self.root.after(0, lambda: self.update_item_widget(item))
                    
                    pct = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        item.progress = float(pct)
                    except:
                        item.progress = 0
                    item.speed = d.get('speed', 0) or 0
                    self.root.after(0, lambda: self.update_item_widget(item))
                elif d['status'] == 'finished':
                    item.status = 'completed'
                    item.progress = 100
                    item.file_path = d.get('filename', '')
                    self.root.after(0, lambda: self.update_item_widget(item))
            
            ydl_opts = {
                "outtmpl": str(download_path / f"{safe_title}.%(ext)s"),
                "progress_hooks": [hook],
                "quiet": True,
                "no_warnings": True,
                "concurrent_fragment_downloads": 4,
            }
            
            # Check for cancellation before starting download
            if item.cancel_event.is_set():
                return
            
            with YoutubeDL(ydl_opts) as ydl:
                item.ydl_instance = ydl
                ydl.download([item.url])
                
            if not item.cancel_event.is_set() and item.status != 'completed':
                item.status = 'completed'
                item.progress = 100
                self.root.after(0, lambda: self.update_item_widget(item))
                
        except Exception as e:
            if not item.cancel_event.is_set():
                item.status = 'error'
                item.error_message = str(e)
                self.root.after(0, lambda: self.update_item_widget(item))
        finally:
            if item in self.active_downloads:
                del self.active_downloads[item]
    
    def file_download_item(self, item: FileDownloadItem):
        try:
            if item.cancel_event.is_set():
                return
                
            item.status = "downloading"
            self.root.after(0, self.update_file_display)
            
            download_path = Path(self.config.config['download_path']) / "Files"
            download_path.mkdir(parents=True, exist_ok=True)
            target = download_path / item.filename
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            with requests.get(item.url, stream=True, timeout=30, headers=headers) as r:
                if item.cancel_event.is_set():
                    return
                    
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                start = time.time()
                
                with open(target, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024*64):
                        if item.cancel_event.is_set():
                            f.close()
                            if target.exists():
                                target.unlink()  # Delete partial file
                            return
                        
                        # Handle pause
                        if not item.pause_event.is_set():
                            item.status = "paused"
                            self.root.after(0, self.update_file_display)
                            item.pause_event.wait()
                            if item.cancel_event.is_set():
                                f.close()
                                if target.exists():
                                    target.unlink()
                                return
                            item.status = "downloading"
                            self.root.after(0, self.update_file_display)
                        
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            item.progress = (downloaded / total) * 100
                        elapsed = max(time.time() - start, 1e-3)
                        item.speed = downloaded / elapsed
                        self.root.after(0, self.update_file_display)
            
            if not item.cancel_event.is_set():
                item.status = "completed"
                item.file_path = str(target)
                item.progress = 100
                self.root.after(0, self.update_file_display)
            
        except Exception as e:
            if not item.cancel_event.is_set():
                item.status = "error"
                item.error_message = str(e)
                self.root.after(0, self.update_file_display)
        finally:
            if item in self.active_file_downloads:
                del self.active_file_downloads[item]
    
    def update_ui_periodically(self):
        """Update UI elements periodically"""
        # Update download statistics
        active_count = len(self.active_downloads) + len(self.active_file_downloads)
        total_count = len(self.download_items) + len(self.file_items)
        self.stats_label.configure(text=f"Downloads: {total_count} • Active: {active_count}")
        
        # Schedule next update
        self.root.after(1000, self.update_ui_periodically)
    
    def open_settings(self):
        settings = ctk.CTkToplevel(self.root)
        settings.title("⚙️ Settings")
        settings.geometry("550x500")
        settings.transient(self.root)
        settings.grab_set()
        settings.resizable(False, False)
        
        # Center the settings window
        settings.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        
        # Main container
        main_frame = ctk.CTkScrollableFrame(settings, corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Settings sections
        sections = [
            ("📁 Download Settings", [
                ("download_path", "Download Path", "path"),
                ("create_subfolders", "Create platform subfolders", "checkbox"),
                ("max_concurrent", "Max concurrent downloads (1-5)", "slider"),
            ]),
            ("🎬 Video Settings", [
                ("default_video_quality", "Default video quality", "dropdown", 
                 ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]),
                ("default_audio_quality", "Default audio quality", "dropdown",
                 ["96kbps", "128kbps", "192kbps", "256kbps", "320kbps"]),
            ]),
            ("⚡ Behavior", [
                ("instant_download", "Enable instant download (auto-download on paste)", "checkbox"),
            ]),
            ("🎨 Appearance", [
                ("theme", "Theme", "dropdown", ["system", "light", "dark"]),
            ])
        ]
        
        settings_vars = {}
        
        for section_title, settings_list in sections:
            # Section header
            section_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            section_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(section_frame, text=section_title, 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
            
            for setting in settings_list:
                setting_key = setting[0]
                setting_label = setting[1]
                setting_type = setting[2]
                
                setting_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
                setting_frame.pack(fill="x", padx=15, pady=(0, 10))
                setting_frame.grid_columnconfigure(1, weight=1)
                
                ctk.CTkLabel(setting_frame, text=setting_label, 
                           font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
                
                if setting_type == "path":
                    path_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
                    path_frame.grid(row=0, column=1, sticky="ew")
                    path_frame.grid_columnconfigure(0, weight=1)
                    
                    settings_vars[setting_key] = tk.StringVar(value=self.config.config[setting_key])
                    path_entry = ctk.CTkEntry(path_frame, textvariable=settings_vars[setting_key], width=250)
                    path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
                    
                    def browse_folder(key=setting_key):
                        folder = filedialog.askdirectory(initialdir=settings_vars[key].get())
                        if folder:
                            settings_vars[key].set(folder)
                    
                    ctk.CTkButton(path_frame, text="📂 Browse", width=80,
                                 command=browse_folder).grid(row=0, column=1)
                
                elif setting_type == "checkbox":
                    settings_vars[setting_key] = tk.BooleanVar(value=self.config.config[setting_key])
                    ctk.CTkCheckBox(setting_frame, text="", 
                                   variable=settings_vars[setting_key]).grid(row=0, column=1, sticky="e")
                
                elif setting_type == "slider":
                    slider_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
                    slider_frame.grid(row=0, column=1, sticky="ew")
                    
                    settings_vars[setting_key] = tk.IntVar(value=self.config.config[setting_key])
                    slider = ctk.CTkSlider(slider_frame, from_=1, to=5, number_of_steps=4, 
                                          variable=settings_vars[setting_key])
                    slider.pack(fill="x", pady=(0, 5))
                    
                    value_label = ctk.CTkLabel(slider_frame, text=f"Current: {settings_vars[setting_key].get()}")
                    value_label.pack()
                    
                    def update_slider_label(value, label=value_label):
                        label.configure(text=f"Current: {int(value)}")
                    
                    slider.configure(command=update_slider_label)
                
                elif setting_type == "dropdown":
                    options = setting[3]
                    settings_vars[setting_key] = tk.StringVar(value=self.config.config[setting_key])
                    dropdown = ctk.CTkComboBox(setting_frame, variable=settings_vars[setting_key], 
                                             values=options, width=150, state="readonly")
                    dropdown.grid(row=0, column=1, sticky="e")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        button_frame.pack(fill="x", pady=(20, 0))
        
        def save_settings():
            for key, var in settings_vars.items():
                self.config.config[key] = var.get()
            
            # Apply theme change
            ctk.set_appearance_mode(self.config.config["theme"])
            
            self.config.save_config()
            self.set_status("✅ Settings saved successfully")
            settings.destroy()
        
        def reset_settings():
            if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to default?"):
                self.config.config = self.config.default_config.copy()
                self.config.save_config()
                settings.destroy()
                self.set_status("✅ Settings reset to defaults")
        
        ctk.CTkButton(button_frame, text="💾 Save Settings", 
                     command=save_settings, height=40,
                     fg_color=("green", "darkgreen"), hover_color=("darkgreen", "green")).pack(side="right", padx=15, pady=15)
        
        ctk.CTkButton(button_frame, text="🔄 Reset to Defaults", 
                     command=reset_settings, height=40,
                     fg_color=("red", "darkred"), hover_color=("darkred", "red")).pack(side="right", padx=(15, 10), pady=15)
        
        ctk.CTkButton(button_frame, text="❌ Cancel", 
                     command=settings.destroy, height=40,
                     fg_color=("gray", "gray30"), hover_color=("gray30", "gray")).pack(side="right", padx=(15, 0), pady=15)
    
    def set_status(self, message):
        self.status_label.configure(text=message)
        self.root.after(5000, lambda: self.status_label.configure(text="🟢 Ready"))
    
    def on_closing(self):
        """Handle application closing"""
        # Cancel all active downloads
        for item in list(self.active_downloads.keys()):
            item.cancel()
        for item in list(self.active_file_downloads.keys()):
            item.cancel()
        
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = SocialMediaDownloader()
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        print(f"Application error: {e}")