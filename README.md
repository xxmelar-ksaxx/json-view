# JSON View

A fast, beautiful JSON file viewer with a dark theme. Opens JSON files and displays them in a structured, readable tree view with syntax highlighting.

![JSON View](icon.png)

## Features

- **🚀 Super fast** — Opens and formats JSON files instantly
- **🌳 Tree View** — Hierarchical tree view showing keys, values, and types
- **📝 Formatted Text** — Pretty-printed JSON with syntax highlighting
- **🎨 Dark Theme** — Easy on the eyes with a modern color scheme
- **🔍 Zoom** — Ctrl+/- to zoom in and out
- **📂 Drag & Drop** — Drop JSON files directly onto the window
- **🔄 Live Reload** — Press F5 to reload the current file
- **🖱️ Right-Click Menu** — "Open with JSON View" in Windows Explorer
- **📎 Default Handler** — Can be set as the default .json file opener

## Quick Start

### Run directly (no build needed)

```bash
python json_view.py                    # Launch app
python json_view.py myfile.json        # Open a specific file
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+Q` | Quit |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `F5` | Reload current file |

## Building

### Prerequisites

```bash
pip install -r requirements.txt
```

### Windows

```bash
# Build the executable
build_windows.bat

# Output: dist/JSON View.exe
```

### macOS (Apple Silicon & Intel)

```bash
chmod +x build_mac.sh
./build_mac.sh

# Output: dist/JSON View
```

The macOS build uses `--target-architecture universal2` to produce a universal binary that runs natively on both Apple Silicon (M1/M2/M3/M4) and Intel Macs.

## Windows Integration

### Install Right-Click Context Menu & Default Handler

After building, run **as Administrator**:

```
install_context_menu.bat
```

This will:
1. Register JSON View as an application
2. Set it as the default `.json` file opener
3. Add "Open with JSON View" to the right-click menu for `.json` files
4. Add "Open with JSON View" to the right-click menu for all files

### Uninstall

Run **as Administrator**:

```
uninstall_context_menu.bat
```

## Project Structure

```
json-view/
├── json_view.py              # Main application
├── create_icon.py             # Icon converter (PNG → ICO/ICNS)
├── icon.png                   # App icon (source)
├── icon.ico                   # App icon (Windows)
├── icon.iconset/              # App icon (macOS iconset)
├── build_windows.bat          # Windows build script
├── build_mac.sh               # macOS build script
├── install_context_menu.bat   # Windows: install right-click & default
├── uninstall_context_menu.bat # Windows: uninstall right-click & default
├── requirements.txt           # Python dependencies
├── sample.json                # Sample JSON for testing
└── README.md                  # This file
```

## Requirements

- Python 3.8+
- tkinter (included with Python)
- Pillow (for icon generation only)
- PyInstaller (for building executables only)

## License

MIT
