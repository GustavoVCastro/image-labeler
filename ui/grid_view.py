"""Grid view for browsing image thumbnails."""

import tkinter as tk
import os
from PIL import Image, ImageTk
from typing import List, Callable, Optional
from utils.constants import GRID_COLUMNS, THUMBNAIL_SIZE, SCROLLBAR_WIDTH
from utils.file_utils import get_label_file_path


class GridView:
    """Grid view for displaying image thumbnails."""

    def __init__(self, parent: tk.Widget, labels_dir: str = ""):
        self.parent = parent
        self.labels_dir = labels_dir

        # Grid canvas for browsing images
        self.canvas = tk.Canvas(parent, bg="white")
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.frame)

        self.scrollbar = tk.Scrollbar(
            parent, orient=tk.VERTICAL, command=self.canvas.yview, width=SCROLLBAR_WIDTH
        )
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Image selection callback
        self.selection_callback: Optional[Callable[[int], None]] = None

        # Store references to prevent garbage collection
        self.thumbnail_refs: List[ImageTk.PhotoImage] = []

    def set_selection_callback(self, callback: Callable[[int], None]) -> None:
        """Set the callback function for when an image is selected."""
        self.selection_callback = callback

    def show(self) -> None:
        """Show the grid view."""
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._bind_scroll_events()

    def hide(self) -> None:
        """Hide the grid view."""
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        self._unbind_scroll_events()

    def populate_grid(self, image_paths: List[str]) -> None:
        """Populate the grid with image thumbnails."""
        # Store image paths for refresh capability
        self.image_paths = image_paths

        # Clear existing thumbnails
        self._clear_grid()

        # Create thumbnails
        for i, image_path in enumerate(image_paths):
            try:
                self._create_thumbnail_button(i, image_path)
            except Exception as e:
                print(f"Error loading thumbnail for {image_path}: {e}")

        # Update scroll region
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def refresh_checkmarks(self) -> None:
        """Refresh checkmarks for all images in the grid."""
        if not hasattr(self, "image_paths"):
            return

        # Update checkmarks by re-populating grid
        self.populate_grid(self.image_paths)

    def _clear_grid(self) -> None:
        """Clear all thumbnails from the grid."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.thumbnail_refs.clear()

    def _create_thumbnail_button(self, index: int, image_path: str) -> None:
        """Create a thumbnail button for an image."""
        # Create thumbnail
        img = Image.open(image_path)
        img.thumbnail(THUMBNAIL_SIZE)
        photo = ImageTk.PhotoImage(img)

        # Store reference to prevent garbage collection
        self.thumbnail_refs.append(photo)

        # Create container frame for thumbnail and checkmark
        container = tk.Frame(self.frame, width=THUMBNAIL_SIZE[0], height=THUMBNAIL_SIZE[1])
        container.grid_propagate(False)  # Don't resize based on contents
        container.grid(row=index // GRID_COLUMNS, column=index % GRID_COLUMNS, padx=5, pady=5)

        # Create button with thumbnail
        btn = tk.Button(
            container,
            image=photo,
            command=lambda idx=index: self._on_image_selected(idx),
            borderwidth=0,
            highlightthickness=0,
        )
        btn.image = photo  # Keep reference
        btn.place(x=0, y=0, width=THUMBNAIL_SIZE[0], height=THUMBNAIL_SIZE[1])

        # Check if image has labels
        has_labels = self._has_labels(image_path)

        # Add green square overlay if labeled
        if has_labels:
            indicator = tk.Label(
                container, bg="#4CAF50", relief="solid", borderwidth=1  # Green color
            )
            # Position in bottom right corner
            indicator.place(x=THUMBNAIL_SIZE[0] - 16, y=THUMBNAIL_SIZE[1] - 16, width=12, height=12)

    def _on_image_selected(self, index: int) -> None:
        """Handle image selection."""
        if self.selection_callback:
            self.selection_callback(index)

    def _has_labels(self, image_path: str) -> bool:
        """Check if an image has associated labels."""
        if not self.labels_dir:
            return False

        label_path = get_label_file_path(image_path, self.labels_dir)
        return os.path.exists(label_path) and os.path.getsize(label_path) > 0

    def _bind_scroll_events(self) -> None:
        """Bind mousewheel and scroll events for grid scrolling."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mouse_scroll(event):
            if event.num == 4:  # Scroll up
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                self.canvas.yview_scroll(1, "units")

        # Bind to the canvas and all its children
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mouse_scroll)
        self.canvas.bind_all("<Button-5>", _on_mouse_scroll)

    def _unbind_scroll_events(self) -> None:
        """Unbind scroll events."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def scroll_up(self) -> None:
        """Scroll up in grid view (keyboard shortcut)."""
        if self.canvas.winfo_viewable():
            self.canvas.yview_scroll(-1, "units")

    def scroll_down(self) -> None:
        """Scroll down in grid view (keyboard shortcut)."""
        if self.canvas.winfo_viewable():
            self.canvas.yview_scroll(1, "units")
