"""Image management and display functionality."""

import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional, Tuple
from utils.constants import CANVAS_MARGIN


class ImageManager:
    """Manages image loading, scaling, and display."""

    def __init__(self):
        self.original_image: Optional[Image.Image] = None
        self.image_tk: Optional[ImageTk.PhotoImage] = None
        self.scale_factor: float = 1.0
        self.image_x: float = 0  # Current x position of the image on canvas
        self.image_y: float = 0  # Current y position of the image on canvas
        self.image_canvas_id: Optional[int] = None

    def load_image(self, image_path: str) -> bool:
        """Load an image from file. Returns True if successful."""
        try:
            self.original_image = Image.open(image_path)
            return True
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return False

    def get_image_size(self) -> Optional[Tuple[int, int]]:
        """Get the original image size (width, height)."""
        if self.original_image:
            return self.original_image.size
        return None

    def get_scaled_size(self) -> Optional[Tuple[int, int]]:
        """Get the current scaled image size."""
        if not self.original_image:
            return None

        width, height = self.original_image.size
        return int(width * self.scale_factor), int(height * self.scale_factor)

    def calculate_fit_scale(self, canvas_width: int, canvas_height: int) -> float:
        """Calculate scale factor to fit image in canvas."""
        if not self.original_image or canvas_width <= 1 or canvas_height <= 1:
            return 1.0

        img_width, img_height = self.original_image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        return min(scale_x, scale_y) * CANVAS_MARGIN

    def set_scale_and_center(
        self, scale: float, canvas_width: int, canvas_height: int
    ) -> None:
        """Set scale factor and center image on canvas."""
        self.scale_factor = scale

        if not self.original_image:
            return

        # Center image on canvas when fitting
        scaled_width, scaled_height = self.get_scaled_size()
        if scaled_width < canvas_width:
            self.image_x = (canvas_width - scaled_width) / 2
        else:
            self.image_x = 0

        if scaled_height < canvas_height:
            self.image_y = (canvas_height - scaled_height) / 2
        else:
            self.image_y = 0

    def create_scaled_image(self) -> Optional[ImageTk.PhotoImage]:
        """Create a scaled PhotoImage for display."""
        if not self.original_image:
            return None

        try:
            scaled_size = self.get_scaled_size()
            if not scaled_size:
                return None

            resized_image = self.original_image.resize(
                scaled_size, Image.Resampling.LANCZOS
            )
            self.image_tk = ImageTk.PhotoImage(resized_image)
            return self.image_tk
        except Exception as e:
            print(f"Error creating scaled image: {e}")
            return None

    def display_on_canvas(self, canvas: tk.Canvas) -> Optional[int]:
        """Display the image on a canvas. Returns the canvas item ID."""
        photo = self.create_scaled_image()
        if not photo:
            return None

        canvas.delete("all")
        self.image_canvas_id = canvas.create_image(
            self.image_x, self.image_y, anchor=tk.NW, image=photo
        )

        # Update scroll region
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        return self.image_canvas_id

    def move_image(self, canvas: tk.Canvas, dx: float, dy: float) -> None:
        """Move the image on the canvas."""
        if self.image_canvas_id:
            canvas.move(self.image_canvas_id, dx, dy)
            self.image_x += dx
            self.image_y += dy

    def canvas_to_image_coords(
        self, canvas_x: float, canvas_y: float
    ) -> Tuple[float, float]:
        """Convert canvas coordinates to original image coordinates."""
        if not self.original_image:
            return canvas_x, canvas_y

        # Adjust for image position and scale
        img_x = (canvas_x - self.image_x) / self.scale_factor
        img_y = (canvas_y - self.image_y) / self.scale_factor
        return img_x, img_y

    def image_to_canvas_coords(self, img_x: float, img_y: float) -> Tuple[float, float]:
        """Convert original image coordinates to canvas coordinates."""
        canvas_x = img_x * self.scale_factor + self.image_x
        canvas_y = img_y * self.scale_factor + self.image_y
        return canvas_x, canvas_y

    def normalize_coordinates(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> Tuple[float, float, float, float]:
        """Convert image coordinates to normalized YOLO format (x_center, y_center, width, height)."""
        if not self.original_image:
            return 0, 0, 0, 0

        img_width, img_height = self.original_image.size

        # Convert to normalized coordinates
        x_center = (x1 + x2) / 2 / img_width
        y_center = (y1 + y2) / 2 / img_height
        width = abs(x2 - x1) / img_width
        height = abs(y2 - y1) / img_height

        return x_center, y_center, width, height

    def denormalize_coordinates(
        self, x_center: float, y_center: float, width: float, height: float
    ) -> Tuple[float, float, float, float]:
        """Convert normalized YOLO coordinates to image coordinates (x1, y1, x2, y2)."""
        if not self.original_image:
            return 0, 0, 0, 0

        img_width, img_height = self.original_image.size

        # Convert from normalized coordinates
        x1 = (x_center - width / 2) * img_width
        y1 = (y_center - height / 2) * img_height
        x2 = (x_center + width / 2) * img_width
        y2 = (y_center + height / 2) * img_height

        return x1, y1, x2, y2
