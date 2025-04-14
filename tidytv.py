import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from os.path import isfile, join, splitext, basename, abspath
import requests
import json
import threading


def get_preview_data(base_path):
    """Generate preview data using only filenames without episode titles."""
    parent_dir = basename(abspath(base_path))
    subfolders = [f.path for f in os.scandir(base_path) if f.is_dir()]
    preview_list = []

    for sIndex, folder in enumerate(sorted(subfolders)):
        sPadded = f'{sIndex + 1:02d}'
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]

        for eIndex, video in enumerate(sorted(files)):
            file_name, file_extension = splitext(video)
            ePadded = f'{eIndex + 1:02d}'
            new_file_name = f'{parent_dir} - S{sPadded}E{ePadded}{file_extension}'
            preview_list.append({
                'season': sPadded,
                'episode': ePadded,
                'original': video,
                'new': new_file_name,
                'folder': folder
            })

        return parent_dir, preview_list


def get_scraped_preview_data(base_path, title_cache):
    """Generate preview data using TVMaze to include episode titles if available."""
    parent_dir = basename(abspath(base_path))
    subfolders = [f.path for f in os.scandir(base_path) if f.is_dir()]
    preview_list = []

    for sIndex, folder in enumerate(sorted(subfolders)):
        sPadded = f'{sIndex + 1:02d}'
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]

        for eIndex, video in enumerate(sorted(files)):
            file_name, file_extension = splitext(video)
            ePadded = f'{eIndex + 1:02d}'
            title = ""
            key = f"{parent_dir}_S{sPadded}E{ePadded}"

            if key in title_cache:
                title = f" - {title_cache[key]}"
            else:
                try:
                    r = requests.get(f"https://api.tvmaze.com/singlesearch/shows?q={parent_dir}&embed=episodes")
                    data = r.json()
                    for ep in data['_embedded']['episodes']:
                        if ep['season'] == int(sPadded) and ep['number'] == int(ePadded):
                            title_cache[key] = ep['name']
                            title = f" - {ep['name']}"
                            break
                except Exception:
                    pass

            new_file_name = f'{parent_dir} - S{sPadded}E{ePadded}{title}{file_extension}'
            preview_list.append({
                'season': sPadded,
                'episode': ePadded,
                'original': video,
                'new': new_file_name,
                'folder': folder
            })

    return parent_dir, preview_list


def rename_files(preview_data, log_callback):
    for item in preview_data:
        original_path = join(item['folder'], item['original'])
        new_path = join(item['folder'], item['new'])

        try:
            os.rename(original_path, new_path)
            log_callback(f"✅ Renamed: {item['original']} → {item['new']}")
        except Exception as e:
            log_callback(f"❌ Failed to rename {item['original']}: {e}")


class EpisodeRenamerApp(ctk.CTk):

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.load_preview(folder)

    import threading

    def threaded_refresh_preview(self):
        if hasattr(self, "last_folder") and self.last_folder:
            threading.Thread(target=lambda: self.load_preview(self.last_folder), daemon=True).start()

    def __init__(self):
        super().__init__()

        self.title("TidyTV")
        self.geometry("950x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.preview_data = []
        self.scrape_titles = tk.BooleanVar(value=False)
        self.title_cache = {}
        self.cache_file = "episode_cache.json"
        self.load_cache()

        # Native menu bar (attached to root window)
        self.option_add('*tearOff', False)
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label="🆕 New", command=self.clear_preview)
        file_menu.add_command(label="📂 Choose Folder", command=lambda: self.threaded_load_preview(filedialog.askdirectory()))
        file_menu.add_command(label="🚀 Start", command=self.run_rename)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menu_bar)
        options_menu = tk.Menu(settings_menu)
        options_menu.add_checkbutton(label="Scrape Episode Titles", variable=self.scrape_titles, command=self.threaded_refresh_preview)
        settings_menu.add_cascade(label="Options", menu=options_menu)
        settings_menu.add_command(label="🌓 Toggle Theme", command=self.toggle_theme)
        settings_menu.add_command(label="📋 Toggle Logs", command=self.toggle_logs)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menu_bar)
        help_menu.add_command(label="ℹ️ About", command=self.show_about_dialog)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.configure(menu=menu_bar)

        # Title and Instructions
        self.title_label = ctk.CTkLabel(self, text="🎬 TidyTV", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 5))

        self.debug_text = ctk.CTkTextbox(self, height=44, font=ctk.CTkFont(size=12, weight="bold"))
        self.debug_text.insert("0.0", "Parent Folder:\nExample:")
        self.debug_text.pack(padx=20, pady=(10, 10), fill='x')

        count_frame = ctk.CTkFrame(self, fg_color="transparent")
        count_frame.pack()

        self.season_count_label = ctk.CTkLabel(count_frame, text="Seasons: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.season_count_label.grid(row=0, column=0, padx=10)

        self.episode_count_label = ctk.CTkLabel(count_frame, text="Total Episodes: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.episode_count_label.grid(row=0, column=1, padx=10)

        self.table = ctk.CTkScrollableFrame(self, height=300)
        self.table.pack(padx=20, pady=(10, 10), fill='both', expand=True)

        self.log_label = ctk.CTkLabel(self, text="Logs:", font=ctk.CTkFont(size=12, weight="bold"))
        self.log_label.pack(padx=20, anchor="w")
        self.log_box = ctk.CTkTextbox(self, height=160)
        self.log_box.pack(padx=20, pady=(10, 20), fill='x')
        self.log_box.configure(state="disabled")

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def refresh_preview(self):
        if not hasattr(self, 'last_folder') or not self.last_folder:
            return
        self.load_preview(self.last_folder)

    def threaded_load_preview(self, folder_selected):
        threading.Thread(target=lambda: self.load_preview(folder_selected), daemon=True).start()

    def load_preview(self, folder_selected):
        self.last_folder = folder_selected
        if self.scrape_titles.get():
            parent_dir, self.preview_data = get_scraped_preview_data(folder_selected, self.title_cache)
        else:
            parent_dir, self.preview_data = get_preview_data(folder_selected)
        self.debug_text.delete("0.0", "end")
        self.debug_text.insert("0.0", f"Parent Folder: {parent_dir}\n")
        if self.preview_data:
            self.debug_text.insert("end", f"Example: {self.preview_data[0]['new']}\n")
        self.populate_table()
        season_count = len(set(item['season'] for item in self.preview_data))
        episode_count = len(self.preview_data)
        self.season_count_label.configure(text=f"Seasons: {season_count}")
        self.episode_count_label.configure(text=f"Total Episodes: {episode_count}")

    def populate_table(self):
        for widget in self.table.winfo_children():
            widget.destroy()

        headers = ["Season", "Episode", "Original", "New Filename"]
        for i, title in enumerate(headers):
            header = ctk.CTkLabel(self.table, text=title, font=ctk.CTkFont(weight="bold"))
            header.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        for rIndex, row in enumerate(self.preview_data):
            ctk.CTkLabel(self.table, text=row['season']).grid(row=rIndex + 1, column=0, padx=10, sticky="w")
            ctk.CTkLabel(self.table, text=row['episode']).grid(row=rIndex + 1, column=1, padx=10, sticky="w")
            ctk.CTkLabel(self.table, text=row['original']).grid(row=rIndex + 1, column=2, padx=10, sticky="w")
            ctk.CTkLabel(self.table, text=row['new']).grid(row=rIndex + 1, column=3, padx=10, sticky="w")

    def run_rename(self):
        try:
            self.log("🔧 Starting renaming process...")
            rename_files(self.preview_data, self.log)
            self.log("🎉 Done renaming files.")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def clear_preview(self):
        self.preview_data = []
        self.populate_table()
        self.debug_text.delete("0.0", "end")
        self.season_count_label.configure(text="Seasons: 0")
        self.episode_count_label.configure(text="Total Episodes: 0")
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.configure(state="disabled")

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

    def toggle_logs(self):
        visible = self.log_box.winfo_ismapped()
        if visible:
            self.log_box.pack_forget()
            self.log_label.pack_forget()
        else:
            self.log_label.pack(padx=20, anchor="w")
            self.log_box.pack(padx=20, pady=(10, 20), fill='x')

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.title_cache.update(json.load(f))
        except Exception as e:
            self.log(f"⚠️ Failed to load cache: {e}")

    def save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.title_cache, f, indent=2)
        except Exception as e:
            self.log(f"⚠️ Failed to save cache: {e}")

    def show_about_dialog(self):
        about_text = (
            "TidyTV\n\n"
            "Organize your Plex or Jellyfin libraries quickly and easily.\n\n"
            "Developed with:\n"
            "- Python 3\n"
            "- customtkinter\n\n"
            "License: MIT\n"
            "© 2025 Christopher Couture. All rights reserved."
        )
        about_window = ctk.CTkToplevel(self)
        about_window.title("About TidyTV")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        label = ctk.CTkLabel(about_window, text=about_text, justify="left", font=ctk.CTkFont(size=12))
        label.pack(padx=20, pady=20, anchor="w")


if __name__ == "__main__":
    app = EpisodeRenamerApp()
    app.protocol("WM_DELETE_WINDOW", lambda: [app.save_cache(), app.destroy()])
    app.mainloop()
