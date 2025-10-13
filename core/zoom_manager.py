"""Zoom and pan functionality management."""

from typing import Optional, Callable
from utils.constants import (
    MIN_ZOOM,
    MAX_ZOOM_KEYBOARD,
    ZOOM_INCREMENT_KEYBOARD,
)


class ZoomManager:
    """Manages zoom and pan operations."""

    def __init__(
        self,
        image_manager,
        update_callback: Optional[Callable] = None,
        root_window=None,
    ):
        self.image_manager = image_manager
        self.update_callback = update_callback
        self.root_window = root_window

        # Pan state
        self.is_panning: bool = False
        self.pan_start_x: Optional[float] = None
        self.pan_start_y: Optional[float] = None

        # Drawing state (prevents zoom during box drawing)
        self.drawing_box: bool = False

    def set_drawing_mode(self, drawing: bool) -> None:
        """Set whether we're currently drawing a bounding box."""
        self.drawing_box = drawing

    def can_zoom_in_keyboard(self) -> bool:
        """Check if we can zoom in using keyboard shortcuts."""
        return self.image_manager.scale_factor * ZOOM_INCREMENT_KEYBOARD <= MAX_ZOOM_KEYBOARD

    def can_zoom_out(self) -> bool:
        """Check if we can zoom out."""
        return self.image_manager.scale_factor / ZOOM_INCREMENT_KEYBOARD >= MIN_ZOOM

    def zoom_in_keyboard(self) -> bool:
        """Zoom in using keyboard increment. Returns True if zoom occurred."""
        if not self.can_zoom_in_keyboard() or self.drawing_box:
            return False

        new_scale = self.image_manager.scale_factor * ZOOM_INCREMENT_KEYBOARD
        return self._zoom_to_scale(new_scale)

    def zoom_out_keyboard(self) -> bool:
        """Zoom out using keyboard increment. Returns True if zoom occurred."""
        if not self.can_zoom_out() or self.drawing_box:
            return False

        new_scale = self.image_manager.scale_factor / ZOOM_INCREMENT_KEYBOARD
        return self._zoom_to_scale(new_scale)

    def zoom_to_scale(self, scale: float) -> bool:
        """Zoom to a specific scale. Returns True if zoom occurred."""
        if self.drawing_box:
            return False

        # Clamp scale to valid range
        scale = max(MIN_ZOOM, min(MAX_ZOOM_KEYBOARD, scale))
        return self._zoom_to_scale(scale)

    def _zoom_to_scale(self, new_scale: float) -> bool:
        """Internal method to perform zoom operation."""
        # Simple zoom without centering (mouse zoom removed)
        self.image_manager.scale_factor = new_scale

        if self.update_callback:
            self.update_callback()

        return True

    def start_pan(self, x: float, y: float) -> None:
        """Start panning operation."""
        self.is_panning = True
        self.pan_start_x = x
        self.pan_start_y = y

    def update_pan(
        self, x: float, y: float, canvas, move_callback: Optional[Callable] = None
    ) -> None:
        """Update pan operation."""
        if not self.is_panning or self.pan_start_x is None or self.pan_start_y is None:
            return

        dx = x - self.pan_start_x
        dy = y - self.pan_start_y

        # Only pan if there's significant movement
        if abs(dx) > 1 or abs(dy) > 1:
            self.image_manager.move_image(canvas, dx, dy)

            if move_callback:
                move_callback(dx, dy)

            # Update pan start position for next movement
            self.pan_start_x = x
            self.pan_start_y = y

    def end_pan(self) -> None:
        """End panning operation."""
        self.is_panning = False
        self.pan_start_x = None
        self.pan_start_y = None

    def get_zoom_percentage(self) -> int:
        """Get current zoom level as percentage."""
        return int(self.image_manager.scale_factor * 100)
