# TidyTV

**TidyTV** is a desktop application built with Python and CustomTkinter that helps you organize and rename episode files for TV shows. It supports optional metadata scraping using the TVMaze API and can rename entire seasons in bulk using a consistent format.

---

## Features

- 🎬 Rename episodes in bulk with SXXEXX formatting
- 🔍 Optional metadata scraping to include episode titles (via TVMaze)
- 🧠 Title caching to reduce API requests and improve performance
- 💾 Persistent cache stored in JSON
- 🌙 Light/Dark mode toggle
- 🧹 Clear preview and logs
- 🪟 Native-style menu bar with File / Settings / Help options
- ✅ Responsive GUI with threaded background tasks

---

## File Naming Examples

- Without Scraping:
  ```
  Solo Leveling - S01E01.mp4
  ```

- With Scraping:
  ```
  Solo Leveling - S01E01 - I'm Used to It.mp4
  ```

---

## How to Run

1. Install requirements:
   ```bash
   pip install customtkinter requests
   ```

2. Run the application:
   ```bash
   python tidy_tv.py
   ```

---

## Building with PyInstaller

To build as a standalone `.exe`:
```bash
pyinstaller --onefile --noconsole tidy_tv.py
```

---

## Project Structure

```
.
├── tidy_tv.py            # Main application
├── episode_cache.json    # Persistent title cache (auto-generated)
├── README.md             # This file
```

---

## License

This project is licensed under the MIT License.

© 2025 Christopher Couture. All rights reserved.

---

## Special Thanks

- [TVMaze API](https://www.tvmaze.com/api) for episode metadata
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for beautiful cross-platform GUI
