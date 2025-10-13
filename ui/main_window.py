"""Main application window and menu setup."""

import tkinter as tk
from tkinter import filedialog
from typing import Callable, Optional
from utils.constants import DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE


class MainWindow:
    """Main application window with menu and layout management."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Labeler")

        # Set initial window size and constraints
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)

        # Callback for loading images
        self.load_images_callback: Optional[Callable[[str], None]] = None

        # Setup menu
        self._setup_menu()

        # Setup keyboard bindings
        self._setup_keyboard_bindings()

    def set_load_images_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback function for loading images."""
        self.load_images_callback = callback

    def bind_keyboard_shortcuts(
        self,
        prev_image: Callable = None,
        next_image: Callable = None,
        undo_box: Callable = None,
        zoom_in: Callable = None,
        zoom_out: Callable = None,
        zoom_fit: Callable = None,
        zoom_100: Callable = None,
        zoom_200: Callable = None,
        clear_labels: Callable = None,
        grid_scroll_up: Callable = None,
        grid_scroll_down: Callable = None,
        grid_view: Callable = None,
    ) -> None:
        """Bind keyboard shortcuts to functions."""
        if prev_image:
            self.root.bind("<Left>", lambda e: prev_image())
        if next_image:
            self.root.bind("<Right>", lambda e: next_image())
        if undo_box:
            self.root.bind("<Control-z>", lambda e: undo_box())
        if zoom_in:
            self.root.bind("<Control-plus>", lambda e: zoom_in())
            self.root.bind("<Control-equal>", lambda e: zoom_in())  # Ctrl+= is same as Ctrl+Plus
        if zoom_out:
            self.root.bind("<Control-minus>", lambda e: zoom_out())
        if zoom_fit:
            self.root.bind("<Control-0>", lambda e: zoom_fit())  # Ctrl+0 to fit to canvas
        if zoom_100:
            self.root.bind("<Control-1>", lambda e: zoom_100())  # Ctrl+1 to zoom to 100%
        if zoom_200:
            self.root.bind("<Control-2>", lambda e: zoom_200())  # Ctrl+2 to zoom to 200%
        if clear_labels:
            self.root.bind("c", lambda e: clear_labels())  # Ctrl+Backspace clears labels
        if grid_scroll_up:
            self.root.bind("<Up>", lambda e: grid_scroll_up())
        if grid_scroll_down:
            self.root.bind("<Down>", lambda e: grid_scroll_down())
        if grid_view:
            self.root.bind("q", lambda e: grid_view())
        if zoom_fit:
            self.root.bind("f", lambda e: zoom_fit())
        if zoom_100:
            self.root.bind("1", lambda e: zoom_100())
        if zoom_200:
            self.root.bind("2", lambda e: zoom_200())

    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()

    def _setup_menu(self) -> None:
        """Setup the application menu."""
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image Directory", command=self._load_images_dialog)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def _setup_keyboard_bindings(self) -> None:
        """Setup basic keyboard bindings that don't require callbacks."""
        # Focus management
        self.root.focus_set()

    def _load_images_dialog(self) -> None:
        """Show dialog to select image directory."""
        dir_path = filedialog.askdirectory(title="Select Images Directory")
        if dir_path and self.load_images_callback:
            self.load_images_callback(dir_path)
