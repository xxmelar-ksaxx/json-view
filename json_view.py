#!/usr/bin/env python3
"""
JSON View — A fast, beautiful JSON file viewer.
Opens JSON files and displays them in a structured, readable format.
"""

import json
import sys
import os
import math
import multiprocessing
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────

APP_NAME = "JSON View"
APP_VERSION = "1.0.0"

# Color scheme (dark theme)
COLORS = {
    "bg":           "#1e1e2e",
    "bg_secondary": "#181825",
    "bg_hover":     "#313244",
    "fg":           "#cdd6f4",
    "fg_dim":       "#6c7086",
    "accent":       "#89b4fa",
    "accent2":      "#cba6f7",
    "string":       "#a6e3a1",
    "number":       "#fab387",
    "boolean":      "#f38ba8",
    "null":         "#f38ba8",
    "key":          "#89b4fa",
    "brace":        "#cdd6f4",
    "border":       "#313244",
    "scrollbar_bg": "#1e1e2e",
    "scrollbar_fg": "#45475a",
}

FONT_FAMILY = "Consolas"
FONT_SIZE = 11


# ─── Application ──────────────────────────────────────────────────────────────

def _load_file_worker_process(filepath, out_queue):
    """Background process: read file and parse JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()

        file_size = os.path.getsize(filepath)
        data = json.loads(raw)
        formatted_text = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=False)

        out_queue.put(('success', data, file_size, formatted_text))
    except json.JSONDecodeError as e:
        out_queue.put(('json_error', e))
    except Exception as e:
        out_queue.put(('error', str(e)))

class JSONViewApp:
    def __init__(self, root, filepath=None):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.root.minsize(600, 400)
        self.root.configure(bg=COLORS["bg"])

        # Try to set icon
        self._set_icon()

        # Track loaded file
        self.current_file = None
        self.json_data = None

        # Loading state
        self._loading = False
        self._loading_angle = 0
        self._loading_overlay = None
        self._loading_canvas = None
        self._loading_text_id = None
        self._loading_anim_id = None

        # Configure styles
        self._configure_styles()

        # Build UI
        self._build_ui()

        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-plus>", lambda e: self._zoom_in())
        self.root.bind("<Control-equal>", lambda e: self._zoom_in())
        self.root.bind("<Control-minus>", lambda e: self._zoom_out())
        self.root.bind("<F5>", lambda e: self._reload_file())

        # Enable drag and drop via DnD if available, else just skip
        self._setup_drag_drop()

        # Open file if provided via command line
        if filepath:
            self.root.after(100, lambda: self.load_file(filepath))

    def _set_icon(self):
        """Set the application icon."""
        try:
            # Look for icon relative to the script/executable
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_dir, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                # Try PNG icon
                icon_png = os.path.join(base_dir, "icon.png")
                if os.path.exists(icon_png):
                    img = tk.PhotoImage(file=icon_png)
                    self.root.iconphoto(True, img)
        except Exception:
            pass  # Icon is optional

    def _configure_styles(self):
        """Configure ttk styles for the dark theme."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Treeview
        self.style.configure("JSON.Treeview",
            background=COLORS["bg_secondary"],
            foreground=COLORS["fg"],
            fieldbackground=COLORS["bg_secondary"],
            borderwidth=0,
            font=(FONT_FAMILY, FONT_SIZE),
            rowheight=26,
        )
        self.style.map("JSON.Treeview",
            background=[("selected", COLORS["bg_hover"])],
            foreground=[("selected", COLORS["accent"])],
        )
        self.style.configure("JSON.Treeview.Heading",
            background=COLORS["bg"],
            foreground=COLORS["fg_dim"],
            borderwidth=0,
            font=(FONT_FAMILY, FONT_SIZE - 1, "bold"),
        )

        # Scrollbar
        self.style.configure("JSON.Vertical.TScrollbar",
            background=COLORS["scrollbar_fg"],
            troughcolor=COLORS["scrollbar_bg"],
            borderwidth=0,
            arrowsize=0,
        )
        self.style.map("JSON.Vertical.TScrollbar",
            background=[("active", COLORS["accent"])],
        )

        # Notebook (tabs)
        self.style.configure("JSON.TNotebook",
            background=COLORS["bg"],
            borderwidth=0,
        )
        self.style.configure("JSON.TNotebook.Tab",
            background=COLORS["bg_secondary"],
            foreground=COLORS["fg_dim"],
            padding=[16, 6],
            font=(FONT_FAMILY, FONT_SIZE - 1),
            borderwidth=0,
        )
        self.style.map("JSON.TNotebook.Tab",
            background=[("selected", COLORS["bg"])],
            foreground=[("selected", COLORS["accent"])],
        )

        # Frame
        self.style.configure("JSON.TFrame",
            background=COLORS["bg"],
        )

        # Button
        self.style.configure("JSON.TButton",
            background=COLORS["bg_hover"],
            foreground=COLORS["fg"],
            padding=[12, 6],
            font=(FONT_FAMILY, FONT_SIZE - 1),
            borderwidth=0,
        )
        self.style.map("JSON.TButton",
            background=[("active", COLORS["accent"]), ("pressed", COLORS["accent2"])],
            foreground=[("active", COLORS["bg"]), ("pressed", COLORS["bg"])],
        )

    def _build_ui(self):
        """Build the main UI."""
        # ── Top bar ──
        topbar = tk.Frame(self.root, bg=COLORS["bg"], height=44)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        # App title
        title_label = tk.Label(topbar, text=f"  {APP_NAME}",
            bg=COLORS["bg"], fg=COLORS["accent"],
            font=(FONT_FAMILY, FONT_SIZE, "bold"))
        title_label.pack(side=tk.LEFT, padx=(8, 0))

        # File info label
        self.file_label = tk.Label(topbar, text="No file loaded",
            bg=COLORS["bg"], fg=COLORS["fg_dim"],
            font=(FONT_FAMILY, FONT_SIZE - 1))
        self.file_label.pack(side=tk.LEFT, padx=(16, 0))

        # Buttons (right side)
        btn_frame = tk.Frame(topbar, bg=COLORS["bg"])
        btn_frame.pack(side=tk.RIGHT, padx=8)

        open_btn = tk.Button(btn_frame, text="📂 Open",
            command=self.open_file,
            bg=COLORS["bg_hover"], fg=COLORS["fg"],
            activebackground=COLORS["accent"], activeforeground=COLORS["bg"],
            font=(FONT_FAMILY, FONT_SIZE - 1),
            bd=0, padx=12, pady=4, cursor="hand2")
        open_btn.pack(side=tk.LEFT, padx=4)

        reload_btn = tk.Button(btn_frame, text="🔄 Reload",
            command=self._reload_file,
            bg=COLORS["bg_hover"], fg=COLORS["fg"],
            activebackground=COLORS["accent"], activeforeground=COLORS["bg"],
            font=(FONT_FAMILY, FONT_SIZE - 1),
            bd=0, padx=12, pady=4, cursor="hand2")
        reload_btn.pack(side=tk.LEFT, padx=4)

        # ── Separator ──
        sep = tk.Frame(self.root, bg=COLORS["border"], height=1)
        sep.pack(fill=tk.X)

        # ── Notebook (Tree View / Text View) ──
        self.notebook = ttk.Notebook(self.root, style="JSON.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tab 1: Tree View
        tree_frame = tk.Frame(self.notebook, bg=COLORS["bg_secondary"])
        self.notebook.add(tree_frame, text="  🌳 Tree View  ")

        # Tree + scrollbar
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
            style="JSON.Vertical.TScrollbar")
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame,
            columns=("value", "type"),
            style="JSON.Treeview",
            yscrollcommand=tree_scroll_y.set,
            show="tree headings",
            selectmode="browse",
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll_y.config(command=self.tree.yview)

        # Column config
        self.tree.heading("#0", text="Key", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)
        self.tree.heading("type", text="Type", anchor=tk.W)
        self.tree.column("#0", width=300, minwidth=150)
        self.tree.column("value", width=500, minwidth=200)
        self.tree.column("type", width=100, minwidth=60)

        # Tree tags for coloring
        self.tree.tag_configure("string", foreground=COLORS["string"])
        self.tree.tag_configure("number", foreground=COLORS["number"])
        self.tree.tag_configure("boolean", foreground=COLORS["boolean"])
        self.tree.tag_configure("null", foreground=COLORS["null"])
        self.tree.tag_configure("key", foreground=COLORS["key"])
        self.tree.tag_configure("object", foreground=COLORS["accent2"])
        self.tree.tag_configure("array", foreground=COLORS["accent"])

        # Bind context menu
        self.tree.bind("<Button-3>", self._on_tree_right_click)
        if sys.platform == "darwin":
            self.tree.bind("<Button-2>", self._on_tree_right_click)
            self.tree.bind("<Control-Button-1>", self._on_tree_right_click)

        # Tab 2: Formatted Text View
        text_frame = tk.Frame(self.notebook, bg=COLORS["bg_secondary"])
        self.notebook.add(text_frame, text="  📝 Formatted Text  ")

        text_scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
            style="JSON.Vertical.TScrollbar")
        text_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_view = tk.Text(text_frame,
            bg=COLORS["bg_secondary"],
            fg=COLORS["fg"],
            font=(FONT_FAMILY, FONT_SIZE),
            wrap=tk.NONE,
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["bg_hover"],
            selectforeground=COLORS["accent"],
            bd=0, padx=16, pady=12,
            state=tk.DISABLED,
            yscrollcommand=text_scroll_y.set,
        )
        self.text_view.pack(fill=tk.BOTH, expand=True)
        text_scroll_y.config(command=self.text_view.yview)

        # Horizontal scroll for text view
        text_scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_view.config(xscrollcommand=text_scroll_x.set)
        text_scroll_x.config(command=self.text_view.xview)

        # Text tags for syntax highlighting
        self.text_view.tag_configure("key", foreground=COLORS["key"])
        self.text_view.tag_configure("string", foreground=COLORS["string"])
        self.text_view.tag_configure("number", foreground=COLORS["number"])
        self.text_view.tag_configure("boolean", foreground=COLORS["boolean"])
        self.text_view.tag_configure("null", foreground=COLORS["null"])
        self.text_view.tag_configure("brace", foreground=COLORS["brace"])

        # ── Status bar ──
        self.statusbar = tk.Label(self.root,
            text="Ready  |  Ctrl+O: Open  |  F5: Reload  |  Ctrl+/-: Zoom",
            bg=COLORS["bg_secondary"], fg=COLORS["fg_dim"],
            font=(FONT_FAMILY, FONT_SIZE - 2),
            anchor=tk.W, padx=12, pady=4)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

        # ── Loading overlay (hidden initially) ──
        self._build_loading_overlay()

        # ── Welcome screen ──
        self._show_welcome()

    def _show_welcome(self):
        """Show welcome message when no file is loaded."""
        self.text_view.config(state=tk.NORMAL)
        self.text_view.delete("1.0", tk.END)
        welcome = (
            "\n\n"
            "     ╔══════════════════════════════════════╗\n"
            "     ║          Welcome to JSON View         ║\n"
            "     ╚══════════════════════════════════════╝\n"
            "\n"
            "     Drop a JSON file here or press Ctrl+O to open.\n"
            "\n"
            "     Shortcuts:\n"
            "       Ctrl+O    Open file\n"
            "       Ctrl+Q    Quit\n"
            "       Ctrl++/-  Zoom in/out\n"
            "       F5        Reload current file\n"
        )
        self.text_view.insert("1.0", welcome)
        self.text_view.config(state=tk.DISABLED)

    def _setup_drag_drop(self):
        """Set up drag & drop support if tkinterdnd2 is available."""
        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        except ImportError:
            pass

    def _on_drop(self, event):
        """Handle dropped files."""
        filepath = event.data.strip('{}')
        if filepath.lower().endswith('.json'):
            self.load_file(filepath)

    def open_file(self):
        """Open a file dialog to select a JSON file."""
        filepath = filedialog.askopenfilename(
            title="Open JSON File",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )
        if filepath:
            self.load_file(filepath)

    # ── Loading overlay ──────────────────────────────────────────────────────

    def _build_loading_overlay(self):
        """Create the loading overlay (hidden by default)."""
        self._loading_overlay = tk.Frame(self.root, bg=COLORS["bg"])

        # Canvas for the animated spinner
        self._loading_canvas = tk.Canvas(
            self._loading_overlay,
            width=200, height=200,
            bg=COLORS["bg"], highlightthickness=0,
        )
        self._loading_canvas.pack(expand=True)

        # Status text below spinner
        self._loading_label = tk.Label(
            self._loading_overlay,
            text="Loading...",
            bg=COLORS["bg"], fg=COLORS["fg_dim"],
            font=(FONT_FAMILY, FONT_SIZE, "italic"),
        )
        self._loading_label.pack(pady=(0, 40))

    def _show_loading(self, filename=""):
        """Show the loading overlay with animated spinner."""
        if self._loading:
            return
        self._loading = True

        msg = f"Loading {filename}..." if filename else "Loading..."
        self._loading_label.config(text=msg)
        self._loading_angle = 0

        # Place overlay on top of the notebook area
        self._loading_overlay.place(
            relx=0, rely=0, relwidth=1, relheight=1,
            x=0, y=45,  # below the top bar
        )
        self._loading_overlay.lift()

        # Start animation
        self._animate_spinner()

    def _hide_loading(self):
        """Hide the loading overlay."""
        self._loading = False
        if self._loading_anim_id:
            self.root.after_cancel(self._loading_anim_id)
            self._loading_anim_id = None
        self._loading_overlay.place_forget()

    def _animate_spinner(self):
        """Draw and animate a spinning arc on the canvas."""
        if not self._loading:
            return

        canvas = self._loading_canvas
        canvas.delete("all")

        cx, cy = 100, 100  # center
        r = 36             # radius
        thickness = 4

        # Draw background ring (dim)
        canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=COLORS["bg_hover"], width=thickness,
        )

        # Draw spinning arc (accent color)
        start = self._loading_angle
        extent = 90
        canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=start, extent=extent,
            outline=COLORS["accent"], width=thickness,
            style=tk.ARC,
        )

        # Draw a second smaller arc for visual flair
        start2 = (self._loading_angle + 180) % 360
        canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=start2, extent=45,
            outline=COLORS["accent2"], width=thickness,
            style=tk.ARC,
        )

        # Pulsing dot at the leading edge of the main arc
        dot_angle = math.radians(start + extent)
        dot_x = cx + r * math.cos(dot_angle)
        dot_y = cy - r * math.sin(dot_angle)
        pulse = 3 + 2 * math.sin(math.radians(self._loading_angle * 2))
        canvas.create_oval(
            dot_x - pulse, dot_y - pulse,
            dot_x + pulse, dot_y + pulse,
            fill=COLORS["accent"], outline="",
        )

        # Advance angle
        self._loading_angle = (self._loading_angle + 6) % 360

        # Schedule next frame (~60fps)
        self._loading_anim_id = self.root.after(16, self._animate_spinner)

    # ── File loading ─────────────────────────────────────────────────────────

    def load_file(self, filepath):
        """Load and parse a JSON file (with loading animation)."""
        filepath = os.path.abspath(filepath)

        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"File not found:\n{filepath}")
            return

        # Prevent double-loading
        if self._loading:
            return

        fname = os.path.basename(filepath)
        self.statusbar.config(text=f"Loading {fname}...")
        self._show_loading(fname)

        # Prepare queue and start process
        self._load_queue = multiprocessing.Queue()
        self._load_process = multiprocessing.Process(
            target=_load_file_worker_process,
            args=(filepath, self._load_queue),
            daemon=True,
        )
        self._load_process.start()

        # Start checking the queue
        self.root.after(100, self._check_load_queue, filepath)

    def _check_load_queue(self, filepath):
        if not self._loading:
            return
            
        try:
            result = self._load_queue.get_nowait()
        except queue.Empty:
            if not self._load_process.is_alive():
                # Process died unexpectedly
                self._on_load_error("Background process died unexpectedly.")
                return
            self.root.after(50, self._check_load_queue, filepath)
            return

        status = result[0]
        if status == 'success':
            _, data, file_size, formatted_text = result
            self._on_load_success(filepath, data, file_size, formatted_text)
        elif status == 'json_error':
            _, error = result
            self._on_load_json_error(filepath, error)
        elif status == 'error':
            _, error_msg = result
            self._on_load_error(error_msg)

    def _on_load_success(self, filepath, data, file_size, formatted_text):
        """Main-thread callback after successful parse."""
        self.json_data = data
        self.current_file = filepath

        fname = os.path.basename(filepath)
        self.root.title(f"{fname} — {APP_NAME}")
        size_str = self._format_size(file_size)
        self.file_label.config(text=f"{fname}  ({size_str})")

        # Update loading message
        self._loading_label.config(text=f"Rendering {fname}...")
        self.root.update_idletasks()

        # Populate views
        self._populate_tree(data)
        self._populate_text(formatted_text)

        # Hide loading & update status
        self._hide_loading()
        self.statusbar.config(
            text=f"Loaded: {filepath}  |  {size_str}  |  Ctrl+O: Open  |  F5: Reload")

    def _on_load_json_error(self, filepath, error):
        """Main-thread callback for JSON parse errors."""
        self._hide_loading()
        messagebox.showerror("JSON Parse Error",
            f"Invalid JSON:\n\n{error.msg}\n\nLine {error.lineno}, Column {error.colno}")
        self.statusbar.config(text=f"Error: Invalid JSON in {os.path.basename(filepath)}")

    def _on_load_error(self, error_msg):
        """Main-thread callback for general errors."""
        self._hide_loading()
        messagebox.showerror("Error", f"Failed to load file:\n\n{error_msg}")
        self.statusbar.config(text="Error loading file")

    def _on_tree_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._selected_item_for_menu = item
            
            menu = tk.Menu(self.root, tearoff=0, 
                           bg=COLORS["bg_secondary"], 
                           fg=COLORS["fg"], 
                           activebackground=COLORS["accent"], 
                           activeforeground=COLORS["bg"])
            menu.add_command(label="Go to this line", command=self._go_to_this_line)
            
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def _go_to_this_line(self):
        if not hasattr(self, '_selected_item_for_menu') or not self._selected_item_for_menu:
            return
            
        item = self._selected_item_for_menu
        path = self._tree_paths.get(item)
        if path is None:
            return
            
        # Switch to Text View tab
        self.notebook.select(1)
        
        # Calculate line number
        line_num = self._find_line_number(self.json_data, path)
        
        # Scroll to line
        self.text_view.see(f"{line_num}.0")
        
        # Highlight the line
        self.text_view.tag_remove("highlight_line", "1.0", tk.END)
        self.text_view.tag_add("highlight_line", f"{line_num}.0", f"{line_num}.0 lineend")
        self.text_view.tag_config("highlight_line", background=COLORS["bg_hover"])
        
        # Place cursor at that line
        self.text_view.mark_set("insert", f"{line_num}.0")
        self.text_view.focus_set()

    def _count_json_lines(self, obj):
        if isinstance(obj, dict):
            if not obj:
                return 1
            return 2 + sum(self._count_json_lines(v) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return 1
            return 2 + sum(self._count_json_lines(v) for v in obj)
        else:
            return 1

    def _find_line_number(self, data, path):
        if not path:
            return 1
        
        current_line = 1
        current_data = data
        
        for step in path:
            current_line += 1
            
            if isinstance(current_data, dict):
                for k, v in current_data.items():
                    if k == step:
                        current_data = v
                        break
                    else:
                        current_line += self._count_json_lines(v)
            elif isinstance(current_data, list):
                for idx, v in enumerate(current_data):
                    if idx == step:
                        current_data = v
                        break
                    else:
                        current_line += self._count_json_lines(v)
        return current_line

    def _populate_tree(self, data):
        """Populate the treeview with JSON data."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._tree_paths = {}
        self._insert_count = 0
        # Build tree
        self._insert_node("", "root", data, "root", path=[])

        # Expand first level
        for child in self.tree.get_children():
            self.tree.item(child, open=True)

    def _insert_node(self, parent, key, value, node_id_prefix, path):
        """Recursively insert a node into the treeview."""
        self._insert_count += 1
        if self._insert_count % 100 == 0:
            self.root.update()

        if isinstance(value, dict):
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=(f"{{{len(value)} keys}}", "object"),
                tags=("object",), open=False)
            self._tree_paths[node] = path
            for i, (k, v) in enumerate(value.items()):
                self._insert_node(node, k, v, f"{node_id_prefix}_{i}", path + [k])

        elif isinstance(value, list):
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=(f"[{len(value)} items]", "array"),
                tags=("array",), open=False)
            self._tree_paths[node] = path
            for i, item in enumerate(value):
                self._insert_node(node, f"[{i}]", item, f"{node_id_prefix}_{i}", path + [i])

        elif isinstance(value, str):
            display_val = value if len(value) <= 200 else value[:200] + "..."
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=(f'"{display_val}"', "string"),
                tags=("string",))
            self._tree_paths[node] = path

        elif isinstance(value, bool):
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=(str(value).lower(), "boolean"),
                tags=("boolean",))
            self._tree_paths[node] = path

        elif isinstance(value, (int, float)):
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=(str(value), "number"),
                tags=("number",))
            self._tree_paths[node] = path

        elif value is None:
            node = self.tree.insert(parent, tk.END,
                text=f"  {key}",
                values=("null", "null"),
                tags=("null",))
            self._tree_paths[node] = path

    def _populate_text(self, formatted):
        """Populate the text view with formatted, syntax-highlighted JSON."""
        self.text_view.config(state=tk.NORMAL)
        self.text_view.delete("1.0", tk.END)

        self.text_view.insert("1.0", formatted)

        # Apply syntax highlighting
        self._highlight_json()

        self.text_view.config(state=tk.DISABLED)

    def _highlight_json(self):
        """Apply syntax highlighting to the text view."""
        content = self.text_view.get("1.0", tk.END)
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            if line_num % 100 == 0:
                self.root.update()

            stripped = line.strip()
            if not stripped:
                continue

            line_start = f"{line_num}.0"
            col = 0

            # Find leading whitespace
            leading = len(line) - len(line.lstrip())

            # Check for key: value pattern
            if ':' in stripped and stripped.startswith('"'):
                # Find the key
                key_end = stripped.index(':', 1)
                # Tag the key portion
                key_start_col = leading
                key_end_col = leading + key_end
                self.text_view.tag_add("key",
                    f"{line_num}.{key_start_col}",
                    f"{line_num}.{key_end_col}")

                # Highlight the value portion
                value_part = stripped[key_end + 1:].strip().rstrip(',')
                value_start_in_line = line.index(':', leading) + 1
                # Find actual value start (skip spaces after colon)
                while value_start_in_line < len(line) and line[value_start_in_line] == ' ':
                    value_start_in_line += 1

                if value_part.startswith('"'):
                    val_end = len(line.rstrip().rstrip(','))
                    self.text_view.tag_add("string",
                        f"{line_num}.{value_start_in_line}",
                        f"{line_num}.{val_end}")
                elif value_part in ('true', 'false'):
                    self.text_view.tag_add("boolean",
                        f"{line_num}.{value_start_in_line}",
                        f"{line_num}.{value_start_in_line + len(value_part)}")
                elif value_part == 'null':
                    self.text_view.tag_add("null",
                        f"{line_num}.{value_start_in_line}",
                        f"{line_num}.{value_start_in_line + 4}")
                elif value_part and value_part[0] in '0123456789-':
                    self.text_view.tag_add("number",
                        f"{line_num}.{value_start_in_line}",
                        f"{line_num}.{value_start_in_line + len(value_part)}")

            elif stripped.startswith('"'):
                # Standalone string (in array)
                self.text_view.tag_add("string",
                    f"{line_num}.{leading}",
                    f"{line_num}.{len(line.rstrip().rstrip(','))}")

            elif stripped.rstrip(',') in ('true', 'false'):
                self.text_view.tag_add("boolean",
                    f"{line_num}.{leading}",
                    f"{line_num}.{leading + len(stripped.rstrip(','))}")

            elif stripped.rstrip(',') == 'null':
                self.text_view.tag_add("null",
                    f"{line_num}.{leading}",
                    f"{line_num}.{leading + 4}")

            elif stripped.rstrip(',') and stripped.rstrip(',')[0] in '0123456789-':
                val = stripped.rstrip(',')
                self.text_view.tag_add("number",
                    f"{line_num}.{leading}",
                    f"{line_num}.{leading + len(val)}")

    def _reload_file(self):
        """Reload the currently loaded file."""
        if self.current_file:
            self.load_file(self.current_file)

    def _zoom_in(self):
        """Increase font size."""
        global FONT_SIZE
        FONT_SIZE = min(FONT_SIZE + 1, 24)
        self._update_fonts()

    def _zoom_out(self):
        """Decrease font size."""
        global FONT_SIZE
        FONT_SIZE = max(FONT_SIZE - 1, 8)
        self._update_fonts()

    def _update_fonts(self):
        """Update all fonts after zoom."""
        self.text_view.config(font=(FONT_FAMILY, FONT_SIZE))
        self.style.configure("JSON.Treeview",
            font=(FONT_FAMILY, FONT_SIZE), rowheight=FONT_SIZE + 15)

    @staticmethod
    def _format_size(size_bytes):
        """Format file size in human-readable format."""
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()

    # Get file path from command line args
    filepath = None
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    app = JSONViewApp(root, filepath)
    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
